from django.apps import AppConfig
from django.contrib import admin
from django.contrib.admin import sites

from dhet_admin.sites import DhetAdminAdminSite


class DefaultAppConfig(AppConfig):
    name = "dhet_admin"
    default = True

    def ready(self):
        site = DhetAdminAdminSite()

        admin.site = site
        sites.site = site


class BasicAppConfig(AppConfig):
    name = "dhet_admin"
