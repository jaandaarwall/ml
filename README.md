source .venv/bin/activate
redis-server
celery -A app.celery worker --loglevel=info
celery -A app.celery beat --loglevel=info

npm create vue@latest
    project-name
    route
    pinia

cd frontend
   npm install
   npm run dev