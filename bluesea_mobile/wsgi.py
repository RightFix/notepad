import os
from django.core.wsgi import get_wsgi_application

# Set the Django settings module (adjust 'bluesea_mobile.settings' if your settings file is named differently)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bluesea_mobile.settings')

# Create the WSGI application and expose it as 'app' (Vercel requirement)
app = get_wsgi_application()

# Optional: Keep 'application' for local compatibility (e.g., gunicorn)
application = app