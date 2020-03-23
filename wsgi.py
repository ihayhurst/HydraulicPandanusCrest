import os, sys
sys.path.insert(0, '/var/www/hpc-gbjh.app.intra/html')
os.chdir("/var/www/hpc-gbjh.app.intra/html")

from server import app as application
