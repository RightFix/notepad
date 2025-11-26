#!/bin/bash
# Install dependencies first (Vercel already does this, but safe to repeat)
pip install -r requirements.txt

# Now run Django commands
python manage.py migrate --noinput
python manage.py collectstatic --noinput --clear