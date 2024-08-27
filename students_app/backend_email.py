"""Module to set up email authentication"""
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class BackendEmail(ModelBackend):
    """Class for Backend email"""
    def authenticate_email(self,username=None, password=None, **kwargs):
        """function to authenticate email"""
        print(kwargs)
        user_model=get_user_model()
        try:
            user=user_model.objects.get(email=username)
        except user_model.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user
        return None
