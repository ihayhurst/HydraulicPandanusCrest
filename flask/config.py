""" # Default config overridden by instance configuration"""

class Config(object):
    APP_NAME = "HPC-homedev"
class Production(Config):
    APP_NAME = "HPC-homeprod"