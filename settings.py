import os

class BaseSettings(object):
    DEBUG = True
    DEFAULT_FROM_EMAIL = "noreply@iufm-mtp-planning.herokuapp.com"
    EMAIL_SUBJECT_PREFIX = "[IUFM Mtp Planning] "

class ProductionSettings(BaseSettings):
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    ADMINS = [os.environ.get('ADMIN_EMAIL')]
    EMAIL_HOST= 'smtp.sendgrid.net'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = os.environ.get('SENDGRID_USERNAME')
    EMAIL_HOST_PASSWORD = os.environ.get('SENDGRID_PASSWORD')

class DevelopmentSettings(BaseSettings):
    DEBUG = True
    SECRET_KEY = "95obsDnE292Y3HMXJVZj3MX9+dnAHxge"
