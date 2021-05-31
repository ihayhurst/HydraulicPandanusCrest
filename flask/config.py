""" # Default config overridden by instance configuration"""


class Config(object):
    APP_NAME = "HPC-without-instanceconfig active"
    LDAP_PORT = "389"
    SECRET_KEY = "justsoitworksoutofgit-overridewithinstanceconf"

    # Uploads
    MAX_CONTENT_LENGTH = 1024 * 1024
    UPLOAD_EXTENSIONS = ["csv", "txt"]
    # UPLOAD_PATH not used as presently in memory handling of uploads
    UPLOAD_PATH = "./uploads"

    # Mail Config
    MAIL_SERVER = "172.26.44.22"
    MAIL_PORT = "25"
    MAIL_USERNAME = "root"


class Production(Config):
    APP_NAME = "HPC-homeProd"
