from .base import *


# During development — print emails in the console
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

DEBUG = True
ALLOWED_HOSTS = ["*"]
