import os
import sys

# Ensure Django project root is on the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.wsgi import application
app = application
