"""Module to set app name"""
from django.apps import AppConfig


class StudentManagementAppConfig(AppConfig):
    """Set the app_name of student management."""
    name = 'students_app'
