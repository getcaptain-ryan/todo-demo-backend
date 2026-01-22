# Railway Quick Start Guide

Get your Todo Demo Backend deployed to Railway in under 10 minutes!

## Prerequisites

- GitHub account with this repository
- Railway account (sign up at [railway.app](https://railway.app))

## Step-by-Step Deployment

### 1. Create Railway Project (2 minutes)

1. Go to [railway.app](https://railway.app) and log in
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose **`todo-demo-backend`** repository
5. Railway will detect the Dockerfile automatically

### 2. Add PostgreSQL Database (1 minute)

1. In your Railway project, click **"New"**
2. Select **"Database"** → **"PostgreSQL"**
3. Railway automatically creates the database and sets `DATABASE_URL`

### 3. Configure Environment Variables (2 minutes)

1. Click on your **backend service** (not the database)
2. Go to **"Variables"** tab
3. Click **"New Variable"** and add:

```bash
ALLOWED_ORIGINS=https://your-frontend-domain.com
```

**Note**: Replace `your-frontend-domain.com` with your actual frontend URL. For testing, you can use:
```bash
ALLOWED_ORIGINS=http://localhost:3000,https://your-frontend.railway.app
```

### 4. Deploy! (3-5 minutes)

Railway automatically deploys when you:
- Connect the repository (first deployment starts immediately)
- Push to your main branch (auto-deploy on every push)

**Watch the deployment**:
1. Click on your backend service
2. Go to **"Deployments"** tab
3. Click on the active deployment to see logs

### 5. Verify Deployment (1 minute)

1. **Get your URL**: Click **"Settings"** → Copy the **"Public Domain"**
2. **Test health endpoint**:
   ```bash
   curl https://your-app.railway.app/health
   ```
   Expected response: `{"status":"healthy"}`

3. **Test API**:
   ```bash
   curl https://your-app.railway.app/
   ```
   Expected response: `{"message":"Welcome to Todo Demo Backend API"}`

## What Happens During Deployment?

```
1. Railway clones your repository
2. Builds Docker image using Dockerfile
3. Starts container with environment variables
4. Waits for PostgreSQL to be ready
5. Runs database migrations (alembic upgrade head)
6. Starts FastAPI application
7. Verifies health check (/health endpoint)
8. Routes traffic to your application ✓
```

## Deployment Logs to Watch For

### ✅ Successful Deployment

```
Starting Todo Demo Backend...
Waiting for database to be ready...
Database is ready!
Running database migrations...
INFO  [alembic.runtime.migration] Running upgrade -> a2140c338b0b
INFO  [alembic.runtime.migration] Running upgrade a2140c338b0b -> 4ff83a080ba6
Migrations completed successfully!
Starting FastAPI application on port 8001...
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### ❌ Common Issues

**Issue**: Database connection timeout
```
Error: Could not connect to database
```
**Solution**: Wait 1-2 minutes for PostgreSQL to initialize, then redeploy

**Issue**: Migration failed
```
Error: Migrations failed!
```
**Solution**: Check migration files in `alembic/versions/` are valid

## Environment Variables Reference

### Automatically Set by Railway

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string (auto-generated) |
| `PORT` | Port to listen on (auto-assigned) |

### You Need to Set

| Variable | Example | Required? |
|----------|---------|-----------|
| `ALLOWED_ORIGINS` | `https://your-frontend.railway.app` | Yes |
| `PROJECT_NAME` | `Todo Demo Backend` | No (has default) |
| `VERSION` | `0.1.0` | No (has default) |

## Testing Your Deployment

### 1. Health Check
```bash
curl https://your-app.railway.app/health
```

### 2. API Documentation
Visit: `https://your-app.railway.app/docs`

### 3. Test Endpoints
```bash
# Get all todos
curl https://your-app.railway.app/api/todos

# Create a todo (example)
curl -X POST https://your-app.railway.app/api/todos \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Todo","description":"Testing Railway deployment"}'
```

## Updating Your Application

### Automatic Deployment

Every time you push to your main branch, Railway automatically:
1. Builds new Docker image
2. Runs migrations
3. Deploys new version
4. Switches traffic (zero downtime)

```bash
# Make changes to your code
git add .
git commit -m "feat: add new feature"
git push origin main

# Railway automatically deploys!
```

### Manual Deployment

1. Go to Railway dashboard
2. Click on your service
3. Go to "Deployments" tab
4. Click "Deploy" button

## Rollback (If Needed)

If something goes wrong:

1. Go to **"Deployments"** tab
2. Find the last working deployment
3. Click **"Redeploy"**

Railway will rollback to that version.

## Next Steps

- [ ] Set up custom domain in Railway settings
- [ ] Configure production CORS origins
- [ ] Connect your frontend application
- [ ] Set up monitoring and alerts
- [ ] Review logs regularly

## Troubleshooting

### Can't access the application

1. **Check deployment status**: Go to Deployments tab
2. **View logs**: Click on deployment → View logs
3. **Verify health check**: Test `/health` endpoint
4. **Check environment variables**: Verify `ALLOWED_ORIGINS` is set

### CORS errors from frontend

1. **Update ALLOWED_ORIGINS**: Include your frontend domain
2. **Format**: Comma-separated, no spaces
3. **Example**: `https://app1.com,https://app2.com`

### Database connection issues

1. **Verify PostgreSQL service**: Check it's running in Railway
2. **Check DATABASE_URL**: Should be auto-set by Railway
3. **Wait for initialization**: PostgreSQL takes 1-2 minutes on first deploy

## Support Resources

- **Railway Docs**: https://docs.railway.app
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Project Documentation**: See `RAILWAY_DEPLOYMENT.md` for detailed guide
- **Containerization Details**: See `CONTAINERIZATION_PLAN.md`

## Success! 🎉

Your Todo Demo Backend is now deployed on Railway with:
- ✅ Automatic deployments on git push
- ✅ Automatic database migrations
- ✅ Health checks and monitoring
- ✅ Zero-downtime deployments
- ✅ Easy rollback capability

**Your API is live at**: `https://your-app.railway.app`

