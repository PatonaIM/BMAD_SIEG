# Database Connection Management for Supabase

## Problem
Supabase imposes strict connection limits, especially on free tier (~15 concurrent connections). Without proper connection management, applications can exhaust the connection pool, causing timeouts and requiring manual session clearing.

## Our Solution

### 1. Conservative Connection Pooling
**File:** `app/core/database.py`

```python
pool_size=2              # Minimal base pool
max_overflow=3           # Max 5 total connections
pool_recycle=300         # Recycle every 5 minutes
pool_timeout=30          # Wait 30s for available connection
```

**Why:**
- Supabase free tier: ~15 connections max
- Multiple backend instances share this limit
- Conservative pool prevents exhaustion
- Aggressive recycling prevents stale connections

### 2. Proper Session Lifecycle Management

**Enhanced `get_db()` Dependency:**
```python
async def get_db():
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()      # Commit on success
    except Exception:
        await session.rollback()    # Rollback on error
    finally:
        await session.close()       # ALWAYS close (returns to pool)
```

**Key Improvements:**
- ✅ Explicit commit/rollback handling
- ✅ Guaranteed connection return via `finally`
- ✅ Prevents connection leaks on exceptions

### 3. Connection Pool Monitoring

**Middleware:** `app/middleware/db_monitor.py`
- Checks pool utilization every 10 requests
- Warns when >80% capacity
- Logs slow queries (>5s) that may hold connections
- Rate-limited warnings (1/minute) to prevent log spam

**Debug Endpoint:** `GET /debug/db-pool`
```json
{
  "status": "ok",
  "pool": {
    "size": 2,
    "checked_out": 1,
    "overflow": 0,
    "checked_in": 1,
    "max_connections": 5,
    "warning": null
  }
}
```

### 4. Health Monitoring

**Enhanced Health Check:** `GET /health`
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": {
    "status": "connected",
    "pool": {
      "size": 2,
      "checked_out": 0,
      "overflow": 0
    }
  }
}
```

## Best Practices

### ✅ DO
1. **Always use FastAPI dependencies** for database sessions
   ```python
   @app.get("/users")
   async def get_users(db: AsyncSession = Depends(get_db)):
       ...
   ```

2. **Use context manager for background tasks**
   ```python
   from app.core.database import get_db_context
   
   async with get_db_context() as db:
       user = await db.get(User, user_id)
   ```

3. **Keep transactions short**
   - Fetch data → Process → Commit
   - Don't hold connections during external API calls

4. **Monitor pool status** in development
   ```bash
   curl http://localhost:8000/debug/db-pool
   ```

### ❌ DON'T
1. **Never create sessions manually without proper cleanup**
   ```python
   # BAD - connection leak if exception occurs
   session = AsyncSessionLocal()
   user = await session.get(User, user_id)
   await session.close()  # Never executed if exception!
   ```

2. **Don't hold connections during long operations**
   ```python
   # BAD - holds connection for entire video encoding
   async def process_video(db: AsyncSession):
       video = await db.get(Video, video_id)
       await encode_video_for_30_seconds(video)  # Connection held!
       video.status = "processed"
       await db.commit()
   ```

3. **Don't increase pool size arbitrarily**
   - More connections ≠ better performance with Supabase
   - Focus on optimizing queries and transaction length

## Troubleshooting

### Symptom: Connection Timeouts
**Causes:**
1. Wrong credentials (check `.env` file)
2. SSL configuration issues
3. Pool exhaustion (too many concurrent requests)
4. Supabase service down

**Debug Steps:**
```bash
# 1. Check pool status
curl http://localhost:8000/debug/db-pool

# 2. Check application logs for warnings
grep "high_db_pool_utilization" logs/app.log

# 3. Check health endpoint
curl http://localhost:8000/health

# 4. Test direct connection
cd backend
source .venv/bin/activate
python -c "
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()
async def test():
    conn = await asyncpg.connect(
        host=os.getenv('DB_HOST'),
        port=int(os.getenv('DB_PORT')),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        ssl='prefer',
        timeout=10
    )
    print('✅ Connection successful!')
    await conn.close()

asyncio.run(test())
"
```

### Symptom: High Pool Utilization Warnings
**Solutions:**
1. Check for slow queries:
   ```python
   # Enable SQL logging temporarily
   engine = create_async_engine(settings.database_url, echo=True)
   ```

2. Identify long-running requests:
   - Check logs for `slow_request` warnings
   - Optimize or refactor slow endpoints

3. Verify proper session cleanup:
   - All routes use `Depends(get_db)`
   - No manual session creation without `finally`

### Symptom: "Too Many Connections" Error
**Immediate Fix:**
1. Restart backend server (releases all connections)
2. Check Supabase dashboard for active connections
3. Consider upgrading Supabase plan for more connections

**Long-term Fix:**
1. Reduce `pool_size` and `max_overflow`
2. Implement connection pooling at Supabase level (Transaction pooler)
3. Add request rate limiting

## Configuration for Different Environments

### Development (Current)
```python
pool_size=2
max_overflow=3
# Total: 5 connections max
```

### Production (Paid Supabase Plan)
```python
pool_size=5
max_overflow=10
# Total: 15 connections max
# Adjust based on Supabase plan limits
```

### High-Traffic Production
```python
# Use Transaction Pooler (port 6543)
DB_PORT=6543  # in .env
pool_size=10
max_overflow=20
# Transaction pooler supports more connections
```

## Monitoring Checklist

Weekly:
- [ ] Check `/debug/db-pool` for capacity trends
- [ ] Review logs for `high_db_pool_utilization` warnings
- [ ] Identify and optimize slow queries

Monthly:
- [ ] Review connection pool configuration
- [ ] Analyze Supabase connection usage dashboard
- [ ] Consider plan upgrade if hitting limits

## Additional Resources
- [Supabase Connection Pooling Docs](https://supabase.com/docs/guides/database/connecting-to-postgres#connection-pooler)
- [SQLAlchemy AsyncIO Documentation](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [FastAPI Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)
