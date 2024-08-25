import os
import sys

def patch_compat():
    compat_path = os.path.join(sys.prefix, 'lib', 'python3.12', 'site-packages', 'compat', '__init__.py')
    with open(compat_path, 'r') as file:
        content = file.read()
    
    content = content.replace(
        "from django.conf.urls import url, include, handler404, handler500",
        "from django.urls import re_path as url, include\nfrom django.conf.urls import handler404, handler500"
    )
    content = content.replace(
        "from django.conf.urls.defaults import url, include, handler404, handler500",
        "from django.urls import re_path as url, include\nfrom django.conf.urls import handler404, handler500"
    )
    
    with open(compat_path, 'w') as file:
        file.write(content)

if __name__ == "__main__":
    patch_compat()