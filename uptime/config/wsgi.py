import os
import sys
from os.path import dirname, realpath
from site import addsitedir

BASE_DIR = dirname(dirname(realpath(__file__)))

WORKON_HOME = '/home/alexander/.envs/'
VENV = 'uptime-new'

addsitedir('{0}/{1}/lib/python3.6/site-packages'.format(WORKON_HOME, VENV))
sys.path = [BASE_DIR] + sys.path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# activamos el entorno virtual
activate_this = os.path.expanduser(
    '{0}/{1}/bin/activate_this.py'.format(WORKON_HOME, VENV))

exec(open(activate_this).read(), dict(__file__=activate_this))

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
