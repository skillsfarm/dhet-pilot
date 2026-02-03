from django.db.models import Count, Q
from django.utils import timezone
from .models import CandidateProfile, AssessmentResponse
from apps.content.models import Occupation

# Proficiency Scoring Weights
PROFICIENCY_SCORING_WEIGHTS = {
    "ASSESSMENT": 0.50,      # Weight for task-based assessment responses
    "EXPERIENCE": 0.30,      # Weight for years of work experience vs requirements
    "QUALIFICATION": 0.20,   # Weight for education relevancy to the occupation
}

# Task Coverage for Assessments
# Candidates are assessed on 80% of tasks per occupation, not all tasks.
# This makes assessments more manageable while still being comprehensive.
TASK_COVERAGE_PERCENTAGE = 0.80


def get_candidate_occupation_score(candidate: CandidateProfile, occupation: Occupation):
    """
    Calculates a comprehensive proficiency score considering:
    1. Assessment responses (Tasks) - Based on 80% of tasks
    2. Years of experience (Work History)
    3. Qualification relevancy (Education)
    """
    # 1. Assessment Score (50%)
    all_tasks_count = occupation.tasks.count()
    # We only assess 80% of tasks, so proficiency is calculated against this subset
    required_tasks_count = max(1, int(all_tasks_count * TASK_COVERAGE_PERCENTAGE))
    
    assessment_score = 0
    if all_tasks_count > 0:
        responses = AssessmentResponse.objects.filter(
            candidate=candidate,
            task__occupation=occupation
        )
        weighted_sum = 0
        for r in responses:
            if r.response == AssessmentResponse.ResponseType.YES:
                weighted_sum += 1
            elif r.response == AssessmentResponse.ResponseType.PARTIALLY:
                weighted_sum += 0.5
        # Score based on required tasks (80%), not all tasks
        # This means answering 80% perfectly gives 100% assessment score
        assessment_score = (weighted_sum / required_tasks_count) * 100
        # Cap at 100% in case they answered more than the required amount
        assessment_score = min(100, assessment_score)

    # 2. Experience Score (30%)
    total_years_exp = sum(exp.years_experience for exp in candidate.work_experience.all())
    required_years = occupation.years_of_experience
    if required_years <= 0:
        experience_score = 100 if total_years_exp > 0 else 50 # Base score for entry level
    else:
        experience_score = min(1.0, total_years_exp / required_years) * 100

    # 3. Qualification Score (20%)
    # Compare candidate's highest NQF level against occupation's preferred NQF level
    NQF_MAP = {
        "MATRIC": 4,
        "CERTIFICATE": 5,
        "DIPLOMA": 6,
        "DEGREE": 7,
        "HONORS": 8,
        "MASTERS": 9,
        "DOCTORATE": 10
    }
    
    candidate_nqf = 0
    for edu in candidate.education_history.all():
        level = NQF_MAP.get(edu.education_type, 0)
        if level > candidate_nqf:
            candidate_nqf = level
    
    required_nqf = occupation.preferred_nqf_level
    if required_nqf <= 0:
        # Entry level, any education is a bonus
        qualification_score = 100 if candidate_nqf > 0 else 50
    else:
        # Compare against required
        if candidate_nqf >= required_nqf:
            qualification_score = 100
        elif candidate_nqf > 0:
            # Partial credit based on gap
            qualification_score = max(0, 100 - ((required_nqf - candidate_nqf) * 20))
        else:
            qualification_score = 10

    # Weighted Total
    total_score = (
        (assessment_score * PROFICIENCY_SCORING_WEIGHTS["ASSESSMENT"]) +
        (experience_score * PROFICIENCY_SCORING_WEIGHTS["EXPERIENCE"]) +
        (qualification_score * PROFICIENCY_SCORING_WEIGHTS["QUALIFICATION"])
    )

    return int(total_score)


def compute_candidate_stats(candidate: CandidateProfile):
    """
    Computes and updates cached stats for a candidate.
    """
    # 1. Highest NQF Level
    nqf_map = {
        "MATRIC": 4,
        "CERTIFICATE": 5,
        "DIPLOMA": 6,
        "DEGREE": 7,
        "HONORS": 8,
        "MASTERS": 9,
        "DOCTORATE": 10
    }
    
    education_entries = candidate.education_history.all()
    max_nqf = 0
    max_nqf_label = "None"
    
    for edu in education_entries:
        level = nqf_map.get(edu.education_type, 0)
        if level > max_nqf:
            max_nqf = level
            # Use the display label from choices if possible, otherwise simple map
            label = edu.get_education_type_display()
            max_nqf_label = f"{level} - {label}"
            
    candidate.highest_nqf_level = max_nqf_label

    # 2. Occupation Matches (Targets)
    targets = candidate.occupation_targets.select_related('occupation', 'occupation__industry').all()
    candidate.occupation_matches_count = targets.count()
    
    # 3. Assessment Progress
    # We want to know for each target occupation, how many tasks they've assessed vs total tasks.
    progress_data = {}
    
    # Keep track of industries for recommendations
    target_industries = set()
    target_occupation_ids = set()

    for target in targets:
        occ = target.occupation
        target_occupation_ids.add(occ.id)
        if occ.industry:
            target_industries.add(occ.industry)

        all_tasks_count = occ.tasks.count()
        # Show progress against 80% of tasks (the required amount for proficiency)
        required_tasks_count = max(1, int(all_tasks_count * TASK_COVERAGE_PERCENTAGE))
        
        responded_tasks = AssessmentResponse.objects.filter(
            candidate=candidate,
            task__occupation=occ
        ).count()
        
        pct = 0
        if required_tasks_count > 0:
            # Calculate percentage against required tasks (80%), not all tasks
            pct = int((responded_tasks / required_tasks_count) * 100)
            # Cap at 100% for display purposes
            pct = min(100, pct)
            
        progress_data[str(occ.ofo_code)] = {
            "title": occ.ofo_title,
            "answered": responded_tasks,
            "total": required_tasks_count,  # Show required count, not all tasks
            "percentage": pct,
            "occupation_id": str(occ.id)  # For direct linking to assessment
        }
        
    candidate.assessment_progress = progress_data

    # 4. Proficiency Gaps (Projected into recommended_occupations field)
    # The user wants to see "occupations they chose" and "where they are lacking".
    # We will use the 'recommended_occupations' JSON field to store these "Gaps".
    
    # 4. Proficiency Scores
    # We calculate a weighted score: YES=1, PARTIALLY=0.5, NO=0
    # Score = (Weighted Sum / Total Tasks) * 100
    
    proficiency_stats = []
    
    for target in targets:
        occ = target.occupation
        proficiency_stats.append({
            "ofo_code": occ.ofo_code,
            "title": occ.ofo_title,
            "score": get_candidate_occupation_score(candidate, occ),
            "industry": occ.industry.name if occ.industry else None,
            "is_target": True,
            "id": str(occ.id)
        })

    # 5. Recommendations based on Industry
    # Find other occupations in the same industries (limit to 5 total recommendations)
    if target_industries:
        # Calculate how many slots we have left to reach 5 items
        current_count = len(proficiency_stats)
        slots_available = 5 - current_count
        
        if slots_available > 0:
            suggestions = Occupation.objects.filter(
                industry__in=target_industries
            ).exclude(id__in=target_occupation_ids)[:slots_available]

            for occ in suggestions:
                 proficiency_stats.append({
                    "ofo_code": occ.ofo_code,
                    "title": occ.ofo_title,
                    "score": get_candidate_occupation_score(candidate, occ),
                    "industry": occ.industry.name if occ.industry else None,
                    "is_target": False,
                    "id": str(occ.id)
                })
            
    candidate.recommended_occupations = proficiency_stats
    
    # Finalize
    candidate.stats_update_needed = False
    candidate.stats_last_computed = timezone.now()
    candidate.save()
