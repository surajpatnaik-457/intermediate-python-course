# Intermediate Python Course

Hey there, 

In this course you will create a dice-rolling program using python. The code you create will be stored in the dice-roller.py file. This repo also contains course materials under the issues tab. 

## User Dashboard API (FastAPI)

- Install dependencies:

```
pip install -r requirements.txt
```

- Configure environment variables (copy `.env.example` to `.env` and adjust):

```
cp .env.example .env
```

- Run the server:

```
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

- Test endpoints:
- Health: `GET http://localhost:8000/healthz`
- Stored procedure: `GET http://localhost:8000/user-dashboard/{employee_id}`
