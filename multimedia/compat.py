from django.conf import settings


__all__ = ['user_model']


# Django >= 1.5 uses AUTH_USER_MODEL to specify the currently active
# User model. Previous versions of Django do not have this setting
# and use the built-in User model.
#
# This is not needed when support for Django 1.4 is dropped.
user_model = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')
