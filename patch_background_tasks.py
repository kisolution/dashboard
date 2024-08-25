import os
import sys

def patch_compat():
    compat_path = os.path.join(sys.prefix, 'lib', 'python3.12', 'site-packages', 'compat', '__init__.py')
    with open(compat_path, 'r') as file:
        content = file.readlines()
    
    new_content = []
    for line in content:
        if line.strip().startswith('from django.conf.urls import'):
            new_content.append("from django.urls import re_path as url, include\n")
            new_content.append("from django.urls import path\n")
            new_content.append("from django.conf.urls import handler404, handler500\n")
        elif line.strip().startswith('from django.conf.urls.defaults import'):
            new_content.append("from django.urls import re_path as url, include\n")
            new_content.append("from django.urls import path\n")
            new_content.append("from django.conf.urls import handler404, handler500\n")
        else:
            new_content.append(line)
    
    with open(compat_path, 'w') as file:
        file.writelines(new_content)

if __name__ == "__main__":
    patch_compat()