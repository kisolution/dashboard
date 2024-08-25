import sys

try:
    from django.urls import re_path as url, include
    from django.urls import path
    from django.conf.urls import handler404, handler500
except ImportError:
    from django.conf.urls import url, include, handler404, handler500

try:
    from django.utils.encoding import force_text
except ImportError:
    from django.utils.encoding import force_unicode as force_text

try:
    from django.utils.encoding import force_bytes
except ImportError:
    from django.utils.encoding import smart_str as force_bytes

try:
    from django.utils.encoding import force_str
except ImportError:
    from django.utils.encoding import force_text as force_str

# Add any other imports that the original compat/__init__.py file had

# Python 2/3 compatibility
if sys.version_info[0] == 3:
    string_types = str,
    from io import StringIO
else:
    string_types = basestring,
    from StringIO import StringIO