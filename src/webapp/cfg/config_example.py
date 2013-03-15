
# The secret key is used for signing the session and creating the csrf hmacs
SECRET_KEY = "gocu5eYoosh8oocoozeeG9queeghae7ushahp9ufaighoo5gex1vulaexohtepha"

# this is the dbapi connection string for sqlalchemy
DB_CONNECTION = None

# Turn this off in production!
DEBUG = True

SERVER_NAME = 'localhost:5000'
APPLICATION_ROOT = "/"


# Mail configuration
MAIL_SERVER = "localhost"
MAIL_PORT = 25
MAIL_USE_TLS = False
MAIL_USE_SSL = False
MAIL_DEBUG = DEBUG
MAIL_USERNAME = None
MAIL_PASSWORD = None
DEFAULT_MAIL_SENDER = "meet-and-eat@exmatrikulationsamt.de"

CONFIRM_SUBJECT = "Meet & Eat Aktivierung"