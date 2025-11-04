# Realtime API Deployment Checklist

## Pre-Deployment Checklist

### Environment Configuration

- [ ] **OpenAI API Key:**
  - [ ] Verify API key has Realtime API beta access
  - [ ] Test connection to `wss://api.openai.com/v1/realtime`
  - [ ] Set `OPENAI_API_KEY` environment variable in production
  - [ ] Rotate API key and update secrets manager

- [ ] **Realtime API Configuration:**
  ```bash
  # .env.production
  ENABLE_REALTIME_API=true
  REALTIME_API_MODEL=gpt-4o-realtime-preview-2024-10-01
  REALTIME_VOICE=alloy
  REALTIME_TEMPERATURE=0.7
  REALTIME_MAX_RESPONSE_TOKENS=1000
  ```

- [ ] **Database Migration:**
  - [ ] Run migration: `alembic upgrade head`
  - [ ] Verify `interviews.realtime_cost_usd` column exists
  - [ ] Test data integrity (no NULL values)

- [ ] **CORS Configuration:**
  - [ ] Allow WebSocket upgrade requests
  - [ ] Configure `Access-Control-Allow-Origin` for production domain
  - [ ] Verify preflight OPTIONS requests work
  ```python
  # backend/app/main.py
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["https://app.yourapp.com"],
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )
  ```

### Infrastructure Setup

- [ ] **WebSocket Support:**
  - [ ] Load balancer supports WebSocket connections
  - [ ] Configure connection timeout (recommended: 30 minutes)
  - [ ] Enable sticky sessions for WebSocket connections
  - [ ] Test WebSocket upgrade handshake

- [ ] **Reverse Proxy (Nginx/Apache):**
  ```nginx
  # nginx.conf
  location /api/v1/interviews/*/realtime/connect {
      proxy_pass http://backend;
      proxy_http_version 1.1;
      proxy_set_header Upgrade $http_upgrade;
      proxy_set_header Connection "upgrade";
      proxy_set_header Host $host;
      proxy_read_timeout 1800s;  # 30 minutes
      proxy_send_timeout 1800s;
  }
  ```

- [ ] **SSL/TLS:**
  - [ ] Configure `wss://` (secure WebSocket) in production
  - [ ] Install SSL certificate
  - [ ] Test HTTPS → WSS upgrade
  - [ ] Enable HTTP Strict Transport Security (HSTS)

- [ ] **Firewall Rules:**
  - [ ] Allow outbound WebSocket connections to `api.openai.com:443`
  - [ ] Allow inbound WebSocket connections from frontend domain
  - [ ] Configure rate limiting rules

### Monitoring & Logging

- [ ] **Structured Logging:**
  - [ ] Configure `structlog` for production
  - [ ] Set log level to `INFO` (or `WARNING` for production)
  - [ ] Enable JSON logging for aggregation
  ```python
  # backend/app/core/logging.py
  import structlog
  structlog.configure(
      processors=[
          structlog.processors.JSONRenderer()
      ]
  )
  ```

- [ ] **Performance Monitoring:**
  - [ ] Deploy APM tool (e.g., New Relic, Datadog)
  - [ ] Create dashboards for:
    - WebSocket connection count
    - AI response latency (P50, P95, P99)
    - Audio processing time
    - Cost per interview
  - [ ] Set up alerts for:
    - High latency (P95 > 2s)
    - High error rate (>5%)
    - High cost per interview (>$10)

- [ ] **Error Tracking:**
  - [ ] Configure Sentry or similar error tracking
  - [ ] Enable source maps for frontend
  - [ ] Tag errors with `service:realtime` label

### Security

- [ ] **JWT Token Validation:**
  - [ ] Verify JWT secret is strong (min 32 characters)
  - [ ] Set appropriate token expiration (15 minutes recommended)
  - [ ] Enable token refresh mechanism
  - [ ] Test token expiration handling

- [ ] **Rate Limiting:**
  - [ ] Configure rate limiter (e.g., Redis-based)
  - [ ] Limit: Max 1 WebSocket connection per interview
  - [ ] Limit: Max 10 audio chunks per second per connection
  - [ ] Test rate limit enforcement

- [ ] **PII Sanitization:**
  - [ ] Verify transcripts are sanitized in logs
  - [ ] No sensitive data in plaintext logs
  - [ ] GDPR compliance: Audio deleted after transcription

- [ ] **Dependency Updates:**
  - [ ] Update all dependencies to latest secure versions
  - [ ] Run security audit: `npm audit` (frontend)
  - [ ] Run security audit: `pip-audit` (backend)
  - [ ] Fix critical vulnerabilities

### Cost Management

- [ ] **Cost Alerts:**
  - [ ] Configure billing alerts in OpenAI dashboard
  - [ ] Set budget cap (e.g., $1000/month)
  - [ ] Monitor daily spend
  - [ ] Alert engineering team if budget exceeds 80%

- [ ] **Cost Optimization:**
  - [ ] Reduce `max_response_output_tokens` to 500 if needed
  - [ ] Monitor average cost per interview
  - [ ] Target: <$5 per interview
  - [ ] Review cost reports weekly

---

## Deployment Steps

### 1. Backend Deployment

```bash
# 1. Pull latest code
git pull origin main

# 2. Install dependencies
cd backend
uv pip install -r requirements.txt

# 3. Run database migrations
uv run alembic upgrade head

# 4. Run tests
uv run pytest tests/unit/test_realtime_cost.py -v

# 5. Build Docker image (if applicable)
docker build -t teamified-backend:latest .

# 6. Deploy to production
# (Specific steps depend on your deployment platform)

# 7. Verify deployment
curl -I https://api.yourapp.com/health
```

### 2. Frontend Deployment

```bash
# 1. Pull latest code
git pull origin main

# 2. Install dependencies
cd frontend
pnpm install

# 3. Build production bundle
pnpm build

# 4. Run linting
pnpm lint

# 5. Deploy to production
# (Specific steps depend on your deployment platform)

# 6. Verify deployment
curl -I https://app.yourapp.com
```

### 3. Smoke Testing

- [ ] **Backend Health Check:**
  ```bash
  curl https://api.yourapp.com/health
  # Expected: 200 OK
  ```

- [ ] **WebSocket Connection:**
  ```bash
  # Install wscat: npm install -g wscat
  wscat -c "wss://api.yourapp.com/api/v1/interviews/{interview_id}/realtime/connect?token={jwt}"
  # Expected: Connection established
  ```

- [ ] **Frontend Smoke Test:**
  - Navigate to interview page: `https://app.yourapp.com/interview/{session_id}`
  - Click "Voice Mode" button
  - Verify "Connected" status appears
  - Speak into microphone
  - Verify AI response audio plays
  - End interview
  - Verify transcript saved

### 4. Rollback Plan

If deployment fails:

```bash
# 1. Rollback backend
git revert HEAD
git push origin main
# Redeploy previous version

# 2. Rollback frontend
git revert HEAD
git push origin main
# Redeploy previous version

# 3. Rollback database migration (if needed)
cd backend
uv run alembic downgrade -1

# 4. Disable Realtime API via feature flag
# Set ENABLE_REALTIME_API=false in environment
# Restart backend services

# 5. Notify users
# Post status update on status page
```

---

## Post-Deployment Validation

### Automated Tests

- [ ] **Run E2E Tests:**
  ```bash
  cd frontend
  pnpm test:e2e
  ```

- [ ] **Load Testing:**
  ```bash
  # Use locust or k6 for load testing
  locust -f tests/load/realtime_load.py --host=https://api.yourapp.com
  ```

### Manual Testing

- [ ] **Happy Path:**
  - [ ] Start interview in voice mode
  - [ ] Complete full interview (5-10 questions)
  - [ ] Verify transcript accuracy
  - [ ] Verify cost tracking in database
  - [ ] Verify performance metrics logged

- [ ] **Error Scenarios:**
  - [ ] Test connection drop and reconnection
  - [ ] Test invalid JWT token (should reject with 1008)
  - [ ] Test rate limiting (2+ connections to same interview)
  - [ ] Test audio format mismatch
  - [ ] Test fallback to text mode

- [ ] **Cross-Browser Testing:**
  - [ ] Chrome (desktop + mobile)
  - [ ] Firefox (desktop)
  - [ ] Safari (desktop + iOS)
  - [ ] Edge (desktop)

### Performance Validation

- [ ] **Latency Targets Met:**
  - [ ] P95 AI response latency < 1 second
  - [ ] WebSocket roundtrip < 200ms
  - [ ] Audio processing delay < 100ms

- [ ] **Stability:**
  - [ ] No crashes or memory leaks after 1 hour
  - [ ] Connection success rate > 99%
  - [ ] Error rate < 1%

### Monitoring Dashboards

- [ ] **Create Grafana/Datadog Dashboard:**
  - WebSocket connection count (gauge)
  - AI response latency histogram
  - Cost per interview (avg, P95)
  - Error rate (%)
  - Connection success rate (%)

- [ ] **Set Up Alerts:**
  - High latency: P95 > 2s for 5 minutes → Alert
  - High error rate: >5% for 2 minutes → Alert
  - High cost: >$10 per interview → Warning
  - Low connection success: <95% for 5 minutes → Alert

---

## Gradual Rollout Strategy

### Week 1: 10% of Users

```python
# backend/app/services/interview_engine.py
def should_use_realtime(user_id: UUID) -> bool:
    """Gradual rollout: 10% of users."""
    if not settings.enable_realtime_api:
        return False
    
    # Hash user ID to deterministic 0-99 range
    hash_val = int(hashlib.md5(str(user_id).encode()).hexdigest(), 16)
    bucket = hash_val % 100
    
    return bucket < 10  # 10% rollout
```

**Monitoring:**
- Track success rate for realtime users vs. legacy users
- Compare average interview latency
- Monitor cost per interview
- Collect user feedback

**Success Criteria:**
- ✅ P95 latency < 1.5s
- ✅ Connection success rate > 98%
- ✅ No critical bugs reported
- ✅ User satisfaction score ≥ 4/5

### Week 2: 25% of Users

Update rollout percentage to 25%:
```python
return bucket < 25  # 25% rollout
```

**Monitoring:** Same as Week 1

### Week 3: 50% of Users

Update rollout percentage to 50%:
```python
return bucket < 50  # 50% rollout
```

**Monitoring:** Same as Week 1

### Week 4: 100% of Users

Enable for all users:
```python
# backend/app/core/config.py
ENABLE_REALTIME_API=true

# Remove rollout logic
def should_use_realtime(user_id: UUID) -> bool:
    return settings.enable_realtime_api
```

**Success Criteria:**
- ✅ All performance targets met for 1 week
- ✅ No increase in support tickets
- ✅ Cost within budget
- ✅ Legacy STT/TTS pipeline still functional (fallback)

---

## Monitoring Checklist

### Daily Monitoring (First Week)

- [ ] Check error rate in Sentry
- [ ] Review performance metrics in APM
- [ ] Monitor cost per interview
- [ ] Check user feedback/support tickets
- [ ] Verify connection success rate > 98%

### Weekly Monitoring

- [ ] Review cost trends (week-over-week)
- [ ] Analyze performance degradation patterns
- [ ] Review top errors in Sentry
- [ ] Update documentation based on issues found
- [ ] Team retrospective on deployment

### Monthly Monitoring

- [ ] Cost analysis and optimization
- [ ] Performance trend analysis
- [ ] Security audit (dependency updates)
- [ ] Review and update runbooks
- [ ] Evaluate deprecation of legacy pipeline

---

## Rollback Triggers

Immediately rollback (disable Realtime API) if:

- ❌ Connection success rate drops below 90%
- ❌ P95 latency exceeds 3 seconds for >10 minutes
- ❌ Critical security vulnerability discovered
- ❌ OpenAI API outage lasting >30 minutes
- ❌ Cost per interview exceeds $15 (3x expected)
- ❌ Critical bugs affecting >10% of users

**Rollback Procedure:**
```bash
# 1. Disable feature flag
export ENABLE_REALTIME_API=false

# 2. Restart backend services
kubectl rollout restart deployment/backend

# 3. Verify legacy pipeline still works
curl -X POST https://api.yourapp.com/api/v1/interviews/{id}/audio \
  -H "Authorization: Bearer {token}" \
  -F "audio=@test_audio.webm"

# 4. Post incident report
# Document issue, impact, resolution
```

---

## Documentation Updates

- [ ] **API Documentation:**
  - [ ] Update with Realtime API endpoints
  - [ ] Add WebSocket protocol specs
  - [ ] Include code examples

- [ ] **User Guide:**
  - [ ] Explain voice mode vs. text mode
  - [ ] Browser compatibility matrix
  - [ ] Troubleshooting common issues

- [ ] **Internal Runbooks:**
  - [ ] Realtime API troubleshooting guide
  - [ ] Incident response procedures
  - [ ] Cost optimization playbook

---

## Support Preparation

- [ ] **Training:**
  - [ ] Train support team on new voice mode
  - [ ] Create FAQs for common issues
  - [ ] Prepare troubleshooting flowchart

- [ ] **Communication:**
  - [ ] Announce feature to users via email/blog
  - [ ] Update help center articles
  - [ ] Prepare status page updates

- [ ] **Escalation:**
  - [ ] Define escalation path for critical issues
  - [ ] On-call rotation for Realtime API issues
  - [ ] Contact info for OpenAI support

---

## Success Metrics

### Technical Metrics

| Metric | Target | Acceptable | Critical |
|--------|--------|------------|----------|
| P95 AI Latency | <1s | <1.5s | >2s |
| Connection Success | >99% | >98% | <95% |
| Error Rate | <0.5% | <1% | >2% |
| Cost Per Interview | <$4 | <$6 | >$10 |

### Business Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| User Satisfaction | >4.5/5 | Post-interview survey |
| Interview Completion | >95% | Analytics |
| Time to Complete | <20 min | Analytics |
| Support Tickets | <10/week | Support system |

---

## Related Documentation

- [API Reference](./REALTIME_API.md)
- [Developer Guide](./REALTIME_DEVELOPER_GUIDE.md)
- [Migration Guide](./REALTIME_MIGRATION.md)
- [Story 1.5.6](./stories/1.5.6.gpt4-realtime-voice-integration.md)

---

**Last Updated:** November 2025  
**Version:** 1.0  
**Deployment Status:** Ready for Production