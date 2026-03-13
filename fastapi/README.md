# FastAPI Folder Deployment

This folder is now self-contained. The backend loads its model from `fastapi/backend/models/ensemble_model.pkl`, and the frontend reads the backend URL from `fastapi/.env`, Streamlit secrets, or environment variables.

## Shared .env file

Edit [fastapi/.env](c:/Users/vikym/Documents/GitHub/mlops_1credit/fastapi/.env) when you want to change the API URL locally.

The most important value is:

```env
BACKEND_URL=https://your-backend-url.onrender.com
```

If you do not set `API_BASE_URL`, the backend smoke test will also use `BACKEND_URL` automatically.

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

For Render, keep using the Render dashboard environment variables. The local `.env` file is mainly for local development and quick testing.

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
- The API smoke test supports both local and hosted URLs through `API_BASE_URL` or `BACKEND_URL`.

## Vercel deployment

Vercel can host the backend as a Python function, but it cannot run the existing Streamlit frontend as a long-lived app. For Vercel, this repo now includes a separate static frontend in `fastapi/public` and a Python entrypoint in `fastapi/api/index.py`.

Use these settings in Vercel:

1. Create a new project from this repository.
2. Set the Root Directory to `fastapi`.
3. Do not set a custom build command.
4. Deploy.

After deployment:

- Frontend URL: your Vercel project root, for example `https://your-app.vercel.app`
- Backend URL: `https://your-app.vercel.app/api`
- API docs: `https://your-app.vercel.app/api/docs`

Why the earlier Vercel build failed:

- Vercel was building the repository root, not `fastapi`.
- There was no supported Python entrypoint at that root.
- The Streamlit frontend is not compatible with Vercel's serverless model.

If you want to keep the Streamlit frontend, use Render for that deployment path. If you want Vercel, use the new static frontend instead.