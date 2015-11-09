# The secret key is used for signing the session and creating the csrf hmacs
SECRET_KEY = "gocu5eYoosh8oocoozeeG9queeghae7ushahp9ufaighoo5gex1vulaexohtepha"

# this is the dbapi connection string for sqlalchemy
DB_CONNECTION = None

# Turn this off in production!
DEBUG = True

# This is useful for deployment behind a reverse proxy
SERVER_NAME = 'localhost:5000'
APPLICATION_ROOT = "/"
BEHIND_REVERSE_PROXY = False

# Register a mapquest app key at http://developer.mapquest.com/web/products/open
MAPQUEST_KEY=""

# Mail configuration
MAIL_SERVER = "localhost"
MAIL_PORT = 25
MAIL_USE_TLS = False
MAIL_USE_SSL = False
MAIL_DEBUG = DEBUG
MAIL_USERNAME = None
MAIL_PASSWORD = None
MAIL_DEFAULT_SENDER = "meet-and-eat@exmatrikulationsamt.de"

CONFIRM_SUBJECT = "Meet & Eat Aktivierung"

ERROR_ADDRESS = ['meetandeat@exmatrikulationsamt.de']
ERROR_SENDER = 'server-error@exmatrikulationsamt.de'
ERROR_FORMAT = '''
Message type:       %(levelname)s
Location:           %(pathname)s:%(lineno)d
Module:             %(module)s
Function:           %(funcName)s
Time:               %(asctime)s

Message:

%(message)s
'''
ERROR_SUBJECT = "Fehler in der Meet&Eat Registrierung"

ADMIN_USER = "admin"
ADMIN_PASSWORD = "test"

# end date for registing
# Format: "yyyy-mm-dd HH:MM"
REGISTER_END = "2020-05-01 22:30"
MAX_TEAMS = 51
VOLUME = 11

# Date of the event (for plan mails)
# Format: "yyyy-mm-dd HH:MM"
EVENT_DATE = "2015-11-07 18:00"
EVENT_DATE_PRETTY = "7. November"

CONTACT_PHONE = "000 00000"
CONTACT_EMAIL = "redaktion@exmatrikulationsamt.de"

TEAM_GROUPS = 2

PHOTO_URL = "http://foo.bar"
PHOTO_UPLOAD = "http://foo.bar"
PHOTO_UPLOAD_USER = "user"
PHOTO_UPLOAD_PASS = "pass"
