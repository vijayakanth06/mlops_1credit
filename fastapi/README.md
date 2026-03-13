# FastAPI Folder Deployment

This folder is now self-contained. The backend loads its model from `fastapi/backend/models/ensemble_model.pkl`, and the frontend reads the backend URL from the `BACKEND_URL` environment variable.

## Local run

Backend:

```powershell
python .\fastapi\backend\server.py
```

Frontend:

```powershell
streamlit run .\fastapi\frontend\main.py
```

Smoke test the API:

```powershell
python .\fastapi\backend\test_api.py
```

Test a deployed backend:

```powershell
$env:API_BASE_URL="https://your-backend-url.onrender.com"
python .\fastapi\backend\test_api.py
```

## Render deployment

Render supports custom Blueprint paths, so you can deploy directly from `fastapi/render.yaml`.

1. Push the repository to GitHub.
2. In Render, create a new Blueprint deployment.
3. Point Render at `fastapi/render.yaml`.
4. Deploy the backend service first if you want to confirm the public URL before the frontend goes live.
5. Set `BACKEND_URL` on the frontend service to your backend public URL, for example `https://playtennis-backend.onrender.com`.
6. Redeploy the frontend service.

## Manual service setup on Render

Backend service:

- Root directory: `fastapi/backend`
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn server:app --host 0.0.0.0 --port $PORT`
- Health check path: `/health`
- Environment variables: `ALLOWED_ORIGINS=*`

Frontend service:

- Root directory: `fastapi/frontend`
- Build command: `pip install -r requirements.txt`
- Start command: `streamlit run main.py --server.address 0.0.0.0 --server.port $PORT --server.headless true`
- Environment variables: `BACKEND_URL=https://your-backend-url.onrender.com`

## What changed

- Backend no longer depends on `day1/playtennis.csv`, so deploying only the `fastapi` folder works.
- CORS is enabled for hosted frontend access.
- Frontend API calls are configurable for local and deployed environments.
- The API smoke test supports both local and hosted URLs through `API_BASE_URL`.