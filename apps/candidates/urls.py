from django.urls import path

from . import views

app_name = "candidates"

urlpatterns = [
    path("onboarding/", views.onboarding, name="onboarding"),
    path("onboarding/profile/", views.onboarding_profile, name="onboarding-profile"),
    path("onboarding/education/", views.onboarding_education, name="onboarding-education"),
    path("onboarding/experience/", views.onboarding_experience, name="onboarding-experience"),
    path("onboarding/targets/", views.onboarding_targets, name="onboarding-targets"),
    path("onboarding/assessment/", views.onboarding_assessment, name="onboarding-assessment"),
]
