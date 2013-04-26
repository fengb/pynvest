# Settings for test execution

from .settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test/pynvest.db',
    }
}
