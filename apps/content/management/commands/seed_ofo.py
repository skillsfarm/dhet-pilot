from django.core.management.base import BaseCommand

from apps.content.models import Occupation, OccupationTask, Skill


class Command(BaseCommand):
    help = "Seed OFO (Organising Framework for Occupations) data"

    def handle(self, *args, **options):
        self.stdout.write("Seeding OFO data...")

        # Generic skills applicable across ICT occupations
        skills_data = [
            # Project Management Skills
            {"name": "Project Planning", "description": "Develop and manage project plans, schedules, and timelines"},
            {"name": "Budget Management", "description": "Manage project budgets and financial analysis"},
            {"name": "Risk Management", "description": "Identify, monitor, and mitigate project risks"},
            {"name": "Stakeholder Management", "description": "Engage and communicate with stakeholders"},
            {"name": "Vendor Management", "description": "Manage vendors, suppliers, and contracts"},
            {"name": "Resource Allocation", "description": "Allocate and coordinate resources and teams"},
            {"name": "Project Governance", "description": "Ensure adherence to governance frameworks and methodologies"},
            {"name": "Change Management", "description": "Track and manage changes to project scope and requirements"},
            # Methodologies
            {"name": "PMBOK", "description": "Project Management Body of Knowledge methodology"},
            {"name": "PRINCE2", "description": "Projects IN Controlled Environments methodology"},
            {"name": "Agile/Scrum", "description": "Agile project management and Scrum framework"},
            {"name": "ITIL", "description": "IT Infrastructure Library service management framework"},
            # Technical Skills
            {"name": "Network Infrastructure", "description": "LAN, WAN, network deployments and management"},
            {"name": "Cloud Platforms", "description": "Cloud infrastructure management and deployment"},
            {"name": "Data Centre Management", "description": "Server infrastructure and data centre operations"},
            {"name": "Cybersecurity", "description": "Security platforms and cybersecurity solutions"},
            {"name": "VoIP Systems", "description": "Voice over IP telecommunications systems"},
            {"name": "Fibre Connectivity", "description": "Fibre network connectivity deployments"},
            # Tools
            {"name": "Project Management Tools", "description": "Project planning and scheduling software"},
            {"name": "Project Documentation", "description": "Create and maintain project documentation and reports"},
            # Soft Skills
            {"name": "Leadership", "description": "Lead teams and provide guidance"},
            {"name": "Communication", "description": "Effective verbal and written communication"},
            {"name": "Negotiation", "description": "Contract negotiation and stakeholder alignment"},
            {"name": "Problem Solving", "description": "Analytical and critical thinking to resolve issues"},
            {"name": "Attention to Detail", "description": "Accuracy in documentation and delivery"},
        ]

        skills = {}
        for skill_data in skills_data:
            skill, created = Skill.objects.get_or_create(
                name=skill_data["name"], defaults={"description": skill_data["description"]}
            )
            skills[skill_data["name"]] = skill
            if created:
                self.stdout.write(self.style.SUCCESS(f"  Created skill: {skill.name}"))

        # Generic OFO Occupations - ICT Project Manager category
        occupations_data = [
            {
                "ofo_code": "133102",
                "ofo_title": "ICT Project Manager",
                "description": "Manages and delivers ICT projects from initiation to closeout. Responsible for scoping, planning, execution, monitoring, and handover of projects.",
                "years_of_experience": 5,
                "tasks": [
                    {
                        "title": "Develop project plans",
                        "description": "Develop and manage project plans, schedules, budgets, and communication frameworks",
                        "skills": ["Project Planning", "Budget Management", "Communication"],
                    },
                    {
                        "title": "Define project scope",
                        "description": "Define scope, allocate resources, set milestones, and monitor progress",
                        "skills": ["Resource Allocation", "Project Planning"],
                    },
                    {
                        "title": "Apply project management methodologies",
                        "description": "Apply project management methodologies and techniques to ensure delivery excellence",
                        "skills": ["PMBOK", "PRINCE2", "Agile/Scrum", "Project Management Tools"],
                    },
                    {
                        "title": "Monitor and mitigate risks",
                        "description": "Monitor project risks, issues, and dependencies; implement mitigation strategies",
                        "skills": ["Risk Management", "Problem Solving"],
                    },
                    {
                        "title": "Maintain project documentation",
                        "description": "Maintain accurate project documentation, reports, and registers",
                        "skills": ["Project Documentation", "Attention to Detail"],
                    },
                    {
                        "title": "Manage stakeholder communication",
                        "description": "Provide regular project updates to stakeholders",
                        "skills": ["Stakeholder Management", "Communication"],
                    },
                    {
                        "title": "Manage vendor relationships",
                        "description": "Manage vendor and supplier contracts, ensuring deliverables are met",
                        "skills": ["Vendor Management", "Negotiation"],
                    },
                    {
                        "title": "Oversee solution implementation",
                        "description": "Oversee implementation of technology solutions",
                        "skills": ["Network Infrastructure", "Cloud Platforms"],
                    },
                    {
                        "title": "Ensure governance compliance",
                        "description": "Ensure adherence to standards and quality frameworks",
                        "skills": ["Project Governance", "ITIL"],
                    },
                ],
            },
            {
                "ofo_code": "133103",
                "ofo_title": "ICT Infrastructure Project Manager",
                "description": "Leads and delivers infrastructure and telecommunications technology projects. Manages projects involving network connectivity, data centres, and cloud platforms.",
                "years_of_experience": 7,
                "tasks": [
                    {
                        "title": "Manage project lifecycle",
                        "description": "Manage the full project lifecycle from initiation through to commissioning and handover",
                        "skills": ["Project Planning", "Project Governance", "Leadership"],
                    },
                    {
                        "title": "Deliver concurrent projects",
                        "description": "Deliver multiple concurrent ICT infrastructure projects",
                        "skills": ["Resource Allocation", "Project Planning"],
                    },
                    {
                        "title": "Manage network deployments",
                        "description": "Manage projects involving network infrastructure deployments",
                        "skills": ["Fibre Connectivity", "Network Infrastructure"],
                    },
                    {
                        "title": "Manage data centre projects",
                        "description": "Oversee data centres and server infrastructure projects",
                        "skills": ["Data Centre Management"],
                    },
                    {
                        "title": "Manage cloud projects",
                        "description": "Deliver cloud infrastructure projects",
                        "skills": ["Cloud Platforms"],
                    },
                    {
                        "title": "Manage security implementations",
                        "description": "Implement security platforms and integrated systems",
                        "skills": ["Cybersecurity", "VoIP Systems"],
                    },
                    {
                        "title": "Develop risk registers",
                        "description": "Develop and manage project plans, schedules, budgets, and risk registers",
                        "skills": ["Risk Management", "Budget Management", "Project Planning"],
                    },
                    {
                        "title": "Provide governance reporting",
                        "description": "Provide project reporting and governance documentation to stakeholders",
                        "skills": ["Project Governance", "Project Documentation", "Stakeholder Management"],
                    },
                    {
                        "title": "Manage procurement activities",
                        "description": "Manage vendors, subcontractors, and procurement activities",
                        "skills": ["Vendor Management", "Negotiation"],
                    },
                    {
                        "title": "Transition to operations",
                        "description": "Ensure successful transition to operations post-implementation",
                        "skills": ["Change Management", "ITIL"],
                    },
                ],
            },
            {
                "ofo_code": "133104",
                "ofo_title": "Senior ICT Project Manager",
                "description": "Manages and delivers multiple cross-functional and large-scale IT projects aligned with organisational strategy.",
                "years_of_experience": 8,
                "tasks": [
                    {
                        "title": "Execute strategic projects",
                        "description": "Execute and deliver projects on-time, within scope and budget, aligned to strategy",
                        "skills": ["Project Planning", "Budget Management", "Project Governance"],
                    },
                    {
                        "title": "Define project feasibility",
                        "description": "Ensure project feasibility by defining purpose, objectives and deliverables",
                        "skills": ["Problem Solving", "Communication"],
                    },
                    {
                        "title": "Engage executive stakeholders",
                        "description": "Work with executive stakeholders to define expectations and deliverables",
                        "skills": ["Stakeholder Management", "Leadership", "Communication"],
                    },
                    {
                        "title": "Develop integrated project plans",
                        "description": "Develop integrated project plans with clearly defined elements",
                        "skills": ["Project Planning", "Resource Allocation"],
                    },
                    {
                        "title": "Obtain project authorisations",
                        "description": "Ensure required authorisations and sign-off from sponsors",
                        "skills": ["Stakeholder Management", "Project Governance"],
                    },
                    {
                        "title": "Coordinate resources",
                        "description": "Coordinate internal resources and external parties for project execution",
                        "skills": ["Resource Allocation", "Vendor Management"],
                    },
                    {
                        "title": "Manage procurement",
                        "description": "Manage procurement and negotiate contracts with suppliers",
                        "skills": ["Vendor Management", "Negotiation"],
                    },
                    {
                        "title": "Create project documentation",
                        "description": "Create and maintain comprehensive project documentation",
                        "skills": ["Project Documentation", "Attention to Detail", "Project Management Tools"],
                    },
                    {
                        "title": "Perform risk management",
                        "description": "Perform risk management to minimise project risks",
                        "skills": ["Risk Management", "Problem Solving"],
                    },
                    {
                        "title": "Track project performance",
                        "description": "Track and measure project performance using appropriate tools",
                        "skills": ["Project Planning", "Project Management Tools"],
                    },
                    {
                        "title": "Provide status reporting",
                        "description": "Provide regular visibility on project status through reporting",
                        "skills": ["Communication", "Project Documentation", "Stakeholder Management"],
                    },
                    {
                        "title": "Ensure methodology adherence",
                        "description": "Ensure adherence to project governance and methodologies",
                        "skills": ["Project Governance", "PMBOK", "PRINCE2"],
                    },
                    {
                        "title": "Conduct lessons learnt",
                        "description": "Capture project lessons learnt and opportunities for improvement",
                        "skills": ["Communication", "Problem Solving"],
                    },
                ],
            },
        ]

        for occ_data in occupations_data:
            occupation, created = Occupation.objects.get_or_create(
                ofo_code=occ_data["ofo_code"],
                defaults={
                    "ofo_title": occ_data["ofo_title"],
                    "description": occ_data["description"],
                    "years_of_experience": occ_data["years_of_experience"],
                },
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"  Created occupation: {occupation.ofo_code} - {occupation.ofo_title}")
                )

                # Create tasks for this occupation
                for task_data in occ_data["tasks"]:
                    task = OccupationTask.objects.create(
                        occupation=occupation,
                        title=task_data["title"],
                        description=task_data["description"],
                    )

                    # Add skills to task
                    for skill_name in task_data["skills"]:
                        if skill_name in skills:
                            task.skills.add(skills[skill_name])

                    self.stdout.write(f"    - Created task: {task.title}")
            else:
                self.stdout.write(f"  Occupation already exists: {occupation.ofo_code}")

        self.stdout.write(self.style.SUCCESS("\nOFO data seeding completed!"))
        self.stdout.write(f"  Total Occupations: {Occupation.objects.count()}")
        self.stdout.write(f"  Total Skills: {Skill.objects.count()}")
        self.stdout.write(f"  Total Tasks: {OccupationTask.objects.count()}")
