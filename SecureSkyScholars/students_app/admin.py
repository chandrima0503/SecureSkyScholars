"""Admin file that overrides django admin """
from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin

from students_app.models import CustomisedUser


class UserModel(UserAdmin):
    pass

admin.site.register(CustomisedUser,UserModel)
