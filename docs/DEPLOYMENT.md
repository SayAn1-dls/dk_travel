# Deployment Guide

## Frontend — Vercel

1. Push your code to GitHub (`main` branch)
2. Go to [vercel.com](https://vercel.com) and import the repository
3. Set the root directory to `frontend`
4. Framework preset: **Vite**
5. Build command: `npm run build`
6. Output directory: `dist`
7. Add environment variables:
   - `VITE_API_BASE_URL` — your backend API URL
8. Click **Deploy**

Vercel will auto-deploy on every push to `main`.

## Backend — Render

1. Go to [render.com](https://render.com) and create a new **Web Service**
2. Connect your GitHub repository
3. Set the root directory to `backend`
4. Runtime: **Python 3**
5. Build command: `pip install -r requirements.txt`
6. Start command: `python app.py`
7. Add environment variables:
   - `MONGODB_URI` — MongoDB Atlas connection string
   - `JWT_SECRET` — secret key for JWT signing
   - `CORS_ORIGINS` — frontend URL for CORS
8. Click **Create Web Service**

## Environment Variables Summary

| Variable           | Service  | Description                    |
|--------------------|----------|--------------------------------|
| `VITE_API_BASE_URL`| Frontend | Backend API URL                |
| `MONGODB_URI`      | Backend  | MongoDB connection string      |
| `JWT_SECRET`       | Backend  | JWT signing secret             |
| `CORS_ORIGINS`     | Backend  | Allowed CORS origins           |

## Post-Deployment Checklist

- [ ] Verify frontend loads at Vercel URL
- [ ] Verify API responds at Render URL
- [ ] Test authentication flow end-to-end
- [ ] Check CORS headers are correct
