from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from rest_framework.routers import DefaultRouter
from scalar import urlpatterns_scalar
from apps.core import views as core_views
from apps.accounts import viewsets, views as account_views
from apps.candidates import views as candidate_views

from allauth.account.views import LoginView, LogoutView

# API router
router = DefaultRouter()
router.register(r"users", viewsets.UserViewSet)

# Admin Configuration
admin.site.site_header = "DHET Administration"
admin.site.site_title = "DHET Admin"
admin.site.index_title = "Welcome to DHET Portal"

urlpatterns = [
    path("", core_views.home, name="home"),
    path("admin/login/", LoginView.as_view(), name="admin_login"),
    path("admin/logout/", LogoutView.as_view(), name="admin_logout"),
    # Custom admin profile URL must be before admin.site.urls
    path("admin/profile/", account_views.profile, name="admin-profile"),
    path("admin/", admin.site.urls),
    path("api/storage/", include("apps.storage.urls")),
    path("api/", include(router.urls)),  # DRF routers (no namespace)
    path("accounts/", include("allauth.urls")),  # login / signup / reset
    # UI views
    path("dashboard/", core_views.dashboard_redirect, name="dashboard"),
    path("dashboard/user/", core_views.user_dashboard, name="user-dashboard"),
    path(
        "dashboard/content-manager/",
        core_views.content_manager_dashboard,
        name="content-manager-dashboard",
    ),
    path("users/", account_views.user_list, name="user_list"),
    path("users/<str:pk>/edit/", account_views.user_edit, name="user_edit"),
    path("occupations/", core_views.occupation_list, name="occupations"),
    path("", include("apps.content.urls")),  # content management views
    path(
        "occupations/<str:occupation_id>/",
        core_views.occupation_detail,
        name="occupation-detail",
    ),
    path("user/profile/", account_views.profile, name="user-profile"),
    path("developer/profile/", account_views.profile, name="developer-profile"),
    path(
        "content-manager/profile/",
        account_views.profile,
        name="content-manager-profile",
    ),
    path("super/profile/", account_views.profile, name="super-profile"),
    # Profile partials (HTMX endpoints)
    path("profile/account/", account_views.profile_account, name="profile-account"),
    path("profile/security/", account_views.profile_security, name="profile-security"),
    path(
        "profile/onboarding/",
        account_views.profile_onboarding,
        name="profile-onboarding",
    ),
    path(
        "profile/education/",
        account_views.profile_education,
        name="profile-education",
    ),
    path(
        "profile/education/<str:pk>/",
        account_views.profile_education_detail,
        name="profile-education-detail",
    ),
    path(
        "profile/experience/",
        account_views.profile_experience,
        name="profile-experience",
    ),
    path(
        "profile/experience/<str:pk>/",
        account_views.profile_experience_detail,
        name="profile-experience-detail",
    ),
    path(
        "profile/targets/",
        account_views.profile_targets,
        name="profile-targets",
    ),
    path(
        "profile/targets/<str:pk>/",
        account_views.profile_targets_detail,
        name="profile-targets-detail",
    ),
    path("onboarding/", candidate_views.onboarding, name="onboarding"),
    path("candidates/", include("apps.candidates.urls")),
    path(
        "save-cookie-preferences/",
        core_views.save_cookie_preferences,
        name="save_cookie_preferences",
    ),
    path("cookies/", include("cookie_consent.urls")),
] + urlpatterns_scalar

if settings.DEBUG:
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns += [
            path("__debug__/", include(debug_toolbar.urls)),
        ]

    if "silk" in settings.INSTALLED_APPS:
        urlpatterns += [
            path("silk/", include("silk.urls", namespace="silk")),
        ]
