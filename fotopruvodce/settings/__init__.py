import os

from .base import *

try:
    from .local import *
except ImportError:
    pass

if "FOTOPRUVODCE_SECRET_KEY" in os.environ:
    SECRET_KEY = os.environ["FOTOPRUVODCE_SECRET_KEY"]

del os
