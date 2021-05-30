""" # Default config overridden by instance configuration"""

class Config(object):
    APP_NAME = "HPC-homedev"
    LDAP_PORT = "389"
    SECRET_KEY = 'justsoitworksoutofgit-overridewithinstanceconf'
class Production(Config):
    APP_NAME = "HPC-homeProd"
