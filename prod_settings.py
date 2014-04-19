import os

SECRET_KEY = os.environ['SECRET_KEY']
DEBUG = False

EMAIL_SUBJECT_PREFIX = "[IUFM Mtp Planning] "
ADMINS = [os.environ['ADMIN_EMAIL']]
DEFAULT_FROM_EMAIL = "noreply@iufm-mtp-planning.herokuapp.com"
EMAIL_HOST_USER = os.environ['SENDGRID_USERNAME']
EMAIL_HOST= 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_PASSWORD = os.environ['SENDGRID_PASSWORD']
