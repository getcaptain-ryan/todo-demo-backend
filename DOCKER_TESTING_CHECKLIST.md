# Docker Testing Checklist

Complete this checklist before deploying to Railway to ensure everything works correctly.

## Prerequisites

- [ ] Docker Desktop installed and running
- [ ] Docker Compose installed
- [ ] Git repository is up to date
- [ ] `.env` file created (copy from `.env.example`)

## Phase 1: Local Docker Build Testing

### 1.1 Build Docker Image

```bash
# Build the image
docker build -t todo-demo-backend .
```

**Expected Output**:
- ✅ Both stages complete successfully
- ✅ No errors during dependency installation
- ✅ Final image created

**Checklist**:
- [ ] Build completes without errors
- [ ] Build time is reasonable (2-5 minutes first time)
- [ ] No security warnings

### 1.2 Verify Image Size

```bash
# Check image size
docker images todo-demo-backend
```

**Expected**:
- Image size: ~200-300 MB

**Checklist**:
- [ ] Image size is reasonable
- [ ] No unexpectedly large layers

### 1.3 Inspect Image Layers

```bash
# View image history
docker history todo-demo-backend
```

**Checklist**:
- [ ] Dependencies layer is cached
- [ ] Application code is in separate layer
- [ ] No sensitive data in layers

## Phase 2: Docker Compose Testing

### 2.1 Start Services

```bash
# Start all services
docker-compose up
```

**Expected Output**:
```
postgres_1  | database system is ready to accept connections
backend_1   | Waiting for database to be ready...
backend_1   | Database is ready!
backend_1   | Running database migrations...
backend_1   | Migrations completed successfully!
backend_1   | Starting FastAPI application on port 8001...
backend_1   | Application startup complete.
```

**Checklist**:
- [ ] PostgreSQL starts successfully
- [ ] Backend waits for database
- [ ] Migrations run successfully
- [ ] Application starts without errors
- [ ] No error messages in logs

### 2.2 Test Health Endpoint

```bash
# In a new terminal
curl http://localhost:8001/health
```

**Expected Response**:
```json
{"status":"healthy"}
```

**Checklist**:
- [ ] Health endpoint responds
- [ ] Response is 200 OK
- [ ] Response body is correct

### 2.3 Test Root Endpoint

```bash
curl http://localhost:8001/
```

**Expected Response**:
```json
{"message":"Welcome to Todo Demo Backend API"}
```

**Checklist**:
- [ ] Root endpoint responds
- [ ] Response is 200 OK
- [ ] Response body is correct

### 2.4 Test API Documentation

Open in browser: `http://localhost:8001/docs`

**Checklist**:
- [ ] Swagger UI loads
- [ ] All endpoints are visible
- [ ] Can expand endpoint details

### 2.5 Test Database Connection

```bash
# Check database tables
docker-compose exec postgres psql -U postgres -d todo_db -c "\dt"
```

**Expected Output**:
```
              List of relations
 Schema |      Name       | Type  |  Owner   
--------+-----------------+-------+----------
 public | alembic_version | table | postgres
 public | todos           | table | postgres
 public | columns         | table | postgres
 public | tasks           | table | postgres
```

**Checklist**:
- [ ] All tables exist
- [ ] Alembic version table exists
- [ ] No migration errors

### 2.6 Test API Endpoints

```bash
# Test GET /api/todos
curl http://localhost:8001/api/todos

# Test GET /api/users
curl http://localhost:8001/api/users

# Test GET /api/columns
curl http://localhost:8001/api/columns

# Test GET /api/tasks
curl http://localhost:8001/api/tasks
```

**Checklist**:
- [ ] All endpoints respond
- [ ] No 500 errors
- [ ] Responses are valid JSON

### 2.7 Test CORS Configuration

```bash
# Test CORS headers
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     -v \
     http://localhost:8001/api/todos
```

**Expected Headers**:
```
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Methods: *
Access-Control-Allow-Headers: *
```

**Checklist**:
- [ ] CORS headers are present
- [ ] Allowed origins include localhost:3000
- [ ] No CORS errors

## Phase 3: Migration Testing

### 3.1 Test Migration Execution

```bash
# Stop services
docker-compose down

# Start again (migrations should run)
docker-compose up
```

**Checklist**:
- [ ] Migrations run on startup
- [ ] No duplicate migration errors
- [ ] Database schema is correct

### 3.2 Test Migration Idempotency

```bash
# Run migrations manually
docker-compose exec backend alembic upgrade head
```

**Expected Output**:
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
```

**Checklist**:
- [ ] No errors when running migrations twice
- [ ] Alembic detects current version
- [ ] No duplicate table errors

### 3.3 Check Migration Status

```bash
# Check current migration version
docker-compose exec backend alembic current
```

**Checklist**:
- [ ] Shows current migration version
- [ ] Version matches latest migration file

## Phase 4: Environment Variable Testing

### 4.1 Test PORT Override

```bash
# Stop services
docker-compose down

# Start with different port
PORT=8002 docker-compose up
```

**Checklist**:
- [ ] Application starts on port 8002
- [ ] Health check works on new port
- [ ] No port conflicts

### 4.2 Test DATABASE_URL Override

Edit `docker-compose.yml` to use different database name, then:

```bash
docker-compose down -v
docker-compose up
```

**Checklist**:
- [ ] Connects to correct database
- [ ] Migrations create new schema
- [ ] Application works with new database

## Phase 5: Error Handling Testing

### 5.1 Test Database Unavailable

```bash
# Stop only PostgreSQL
docker-compose stop postgres

# Watch backend logs
docker-compose logs -f backend
```

**Expected Behavior**:
- Backend waits for database
- Retries connection
- Eventually times out or succeeds when postgres restarts

**Checklist**:
- [ ] Backend handles database unavailability
- [ ] Retry logic works
- [ ] Clear error messages

### 5.2 Test Migration Failure

Create an invalid migration file and test:

**Checklist**:
- [ ] Deployment fails gracefully
- [ ] Error message is clear
- [ ] Container stops (doesn't run with bad schema)

## Phase 6: Performance Testing

### 6.1 Test Build Cache

```bash
# Make a small code change
echo "# comment" >> app/main.py

# Rebuild
docker-compose up --build
```

**Expected**:
- Build time: 10-30 seconds (cached dependencies)

**Checklist**:
- [ ] Dependencies are cached
- [ ] Only application layer rebuilds
- [ ] Build is fast

### 6.2 Test Startup Time

```bash
# Time the startup
time docker-compose up -d
docker-compose logs -f backend
```

**Expected**:
- Total startup: 30-60 seconds

**Checklist**:
- [ ] Startup time is reasonable
- [ ] No unnecessary delays
- [ ] Health check passes quickly

## Phase 7: Cleanup Testing

### 7.1 Test Clean Shutdown

```bash
# Stop services gracefully
docker-compose down
```

**Expected Output**:
```
Stopping todo-demo-backend ... done
Stopping todo-demo-postgres ... done
Removing todo-demo-backend ... done
Removing todo-demo-postgres ... done
```

**Checklist**:
- [ ] Services stop gracefully
- [ ] No error messages
- [ ] Containers are removed

### 7.2 Test Volume Cleanup

```bash
# Remove volumes
docker-compose down -v
```

**Checklist**:
- [ ] Volumes are removed
- [ ] No orphaned data
- [ ] Can start fresh

## Phase 8: Security Testing

### 8.1 Verify Non-Root User

```bash
# Check user in container
docker-compose exec backend whoami
```

**Expected Output**: `appuser`

**Checklist**:
- [ ] Container runs as non-root user
- [ ] User is `appuser`
- [ ] Application still works

### 8.2 Check for Secrets

```bash
# Search for potential secrets in image
docker history todo-demo-backend --no-trunc | grep -i password
```

**Checklist**:
- [ ] No passwords in image layers
- [ ] No API keys in image
- [ ] No sensitive data exposed

## Final Checklist

Before deploying to Railway:

- [ ] All Phase 1 tests pass (Docker Build)
- [ ] All Phase 2 tests pass (Docker Compose)
- [ ] All Phase 3 tests pass (Migrations)
- [ ] All Phase 4 tests pass (Environment Variables)
- [ ] All Phase 5 tests pass (Error Handling)
- [ ] All Phase 6 tests pass (Performance)
- [ ] All Phase 7 tests pass (Cleanup)
- [ ] All Phase 8 tests pass (Security)
- [ ] Documentation is up to date
- [ ] `.env.example` is current
- [ ] No sensitive data in repository

## Ready for Railway Deployment! 🚀

Once all tests pass, you're ready to deploy to Railway. Follow the steps in `RAILWAY_QUICKSTART.md`.

## Troubleshooting

### Build fails
- Clear Docker cache: `docker builder prune -a`
- Check `uv.lock` is committed
- Verify `pyproject.toml` is valid

### Migrations fail
- Check migration files in `alembic/versions/`
- Verify `DATABASE_URL` format
- Test migrations manually: `docker-compose exec backend alembic upgrade head`

### Application won't start
- Check logs: `docker-compose logs backend`
- Verify environment variables in `.env`
- Test database connection: `docker-compose exec postgres psql -U postgres`

### CORS errors
- Check `ALLOWED_ORIGINS` in `.env`
- Verify format (comma-separated, no spaces)
- Test with curl (see Phase 2.7)

