from django.db.models import Count, Q
from django.utils import timezone
from .models import CandidateProfile, AssessmentResponse
from apps.content.models import Occupation

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
            # We can construct a nice label: "NQF 7 - Bachelor's Degree"
            label = edu.get_education_type_display()
            max_nqf_label = f"NQF {level} - {label}"
            
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

        total_tasks = occ.tasks.count()
        
        responded_tasks = AssessmentResponse.objects.filter(
            candidate=candidate,
            task__occupation=occ
        ).count()
        
        pct = 0
        if total_tasks > 0:
            pct = int((responded_tasks / total_tasks) * 100)
            
        progress_data[str(occ.ofo_code)] = {
            "title": occ.ofo_title,
            "answered": responded_tasks,
            "total": total_tasks,
            "percentage": pct
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
        total_tasks = occ.tasks.count()
        
        score = 0
        if total_tasks > 0:
            responses = AssessmentResponse.objects.filter(
                candidate=candidate,
                task__occupation=occ
            )
            
            weighted_sum = 0
            for r in responses:
                if r.response == AssessmentResponse.ResponseType.YES:
                    weighted_sum += 1
                elif r.response == AssessmentResponse.ResponseType.PARTIALLY:
                    weighted_sum += 0.5
            
            score = int((weighted_sum / total_tasks) * 100)
        
        proficiency_stats.append({
            "ofo_code": occ.ofo_code,
            "title": occ.ofo_title,
            "score": score,
            "industry": occ.industry.name if occ.industry else None,
            "is_target": True
        })

    # 5. Recommendations based on Industry
    # Find other occupations in the same industries
    if target_industries:
        suggestions = Occupation.objects.filter(
            industry__in=target_industries
        ).exclude(id__in=target_occupation_ids)

        for occ in suggestions:
             proficiency_stats.append({
                "ofo_code": occ.ofo_code,
                "title": occ.ofo_title,
                "score": 0, # No score for non-targets yet
                "industry": occ.industry.name if occ.industry else None,
                "is_target": False
            })
            
    candidate.recommended_occupations = proficiency_stats
    
    # Finalize
    candidate.stats_update_needed = False
    candidate.stats_last_computed = timezone.now()
    candidate.save()
