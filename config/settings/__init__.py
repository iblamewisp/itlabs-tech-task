import os
from decouple import config

ENV = config('DJANGO_ENV', default='development')

if ENV == 'production':
    from .production import *
else:
    from .development import *