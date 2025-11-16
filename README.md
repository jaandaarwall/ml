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


## **Step 1: Create and Activate Virtual Environment**
```bash
mkdir my_project && cd my_project
uv venv .venv
source .venv/bin/activate
```

---
## **Step 2: Install Dependencies**
Navigate to the Flask backend directory and install dependencies:
```bash
cd backend  # Change to the backend directory
uv pip install -r requirements.txt
```

---
## **Step 3: Start Redis Server**
Ensure Redis is installed and start the Redis server:
```bash
sudo service redis-server start
or 
redis-server

```
To check if Redis is running:
```bash
redis-cli ping  # Should return 'PONG'
```

---
## **Step 4: Start Celery Worker**
```bash
cd backend  # Ensure you're in the backend directory
celery -A app.celery worker --loglevel=info
```

---
## **Step 5: Start Celery Beat**
```bash
celery -A app.celery beat --loglevel=info
```

---
## **Step 6: Start Flask Application**
```bash
python app.py
```
The Flask app should now be running.

---
## **Step 7: Load VueJS via CDN**
Instead of using Vue CLI, the Vue application is loaded via CDN in an `index.html` file. Ensure your project structure includes:

Ensure this file is in the frontend directory and served properly.

---
## **Step 8: Testing the Setup**
- Open your browser and navigate to the Flask backend API: `http://localhost:5000`
- Open `index.html` in a browser or serve it using a lightweight HTTP server (e.g., `python -m http.server` in the frontend directory).
- Monitor Celery logs to ensure background tasks are working correctly.

---
## **Stopping Services**
To stop the services:
```bash
sudo servicectl stop redis  # Stop Redis
or 
sudo systemctl stop redis

pkill -f "celery"  # Stop Celery worker and beat
```
