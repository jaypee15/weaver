# Weaver Deployment Checklist

Use this checklist to ensure a smooth deployment to production.

## Pre-Deployment

### 1. Environment Setup

- [ ] Google Cloud Project created
- [ ] GCP billing enabled
- [ ] Cloud SQL (PostgreSQL) instance provisioned with pgvector
- [ ] Cloud Storage bucket created (`weaver-docs`)
- [ ] Memorystore (Redis) instance provisioned
- [ ] Google Gemini API key obtained
- [ ] Supabase project created
- [ ] Supabase OAuth configured (production callback URLs)
- [ ] GCP Secret Manager configured

### 2. Database Setup

- [ ] Cloud SQL instance accessible
- [ ] pgvector extension installed
- [ ] Database migrations run (`models.sql`)
- [ ] Connection pooling configured
- [ ] Backup schedule configured (daily recommended)
- [ ] Read replicas configured (optional, for scale)

### 3. Secrets Configuration

Create secrets in GCP Secret Manager:

- [ ] `DATABASE_URL` - Cloud SQL connection string
- [ ] `REDIS_URL` - Memorystore connection string
- [ ] `GOOGLE_API_KEY` - Gemini API key
- [ ] `GCS_BUCKET_NAME` - Storage bucket name
- [ ] `GCS_PROJECT_ID` - GCP project ID
- [ ] `SUPABASE_URL` - Supabase project URL
- [ ] `SUPABASE_KEY` - Supabase anon key
- [ ] `SENTRY_DSN` - Sentry project DSN (optional)

### 4. Docker Images

- [ ] API image built and pushed to GCR
- [ ] Worker image built and pushed to GCR
- [ ] Images tagged with version/commit hash
- [ ] Images scanned for vulnerabilities

### 5. Infrastructure Configuration

- [ ] Cloud Run service configured (API)
- [ ] Compute Engine or GKE configured (Workers)
- [ ] VPC networking configured
- [ ] Cloud SQL proxy configured (if needed)
- [ ] Load balancer configured (if needed)
- [ ] CDN configured for static assets (optional)
- [ ] Domain name configured
- [ ] SSL certificate provisioned

## Deployment Steps

### 1. Deploy Database

```bash
# Connect to Cloud SQL
gcloud sql connect INSTANCE_NAME --user=postgres

# Run migrations
\i /path/to/models.sql

# Verify tables
\dt
```

### 2. Deploy API (Cloud Run)

```bash
# Build and push
docker build -t gcr.io/PROJECT_ID/weaver-api:v1.0.0 -f infra/docker/Dockerfile --target api .
docker push gcr.io/PROJECT_ID/weaver-api:v1.0.0

# Deploy
gcloud run deploy weaver-api \
  --image gcr.io/PROJECT_ID/weaver-api:v1.0.0 \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --min-instances 1 \
  --max-instances 10 \
  --set-secrets=DATABASE_URL=weaver-secrets:latest \
  --set-env-vars ENVIRONMENT=production
```

### 3. Deploy Workers

```bash
# Build and push
docker build -t gcr.io/PROJECT_ID/weaver-worker:v1.0.0 -f infra/docker/Dockerfile --target worker .
docker push gcr.io/PROJECT_ID/weaver-worker:v1.0.0

# Deploy to Compute Engine or GKE
# See infra/deploy/cloudrun.yaml for configuration
```

### 4. Deploy Frontend

```bash
cd frontend

# Build
npm run build

# Deploy to Vercel/Netlify or Cloud Run
# Update environment variables:
# - NEXT_PUBLIC_API_URL=https://your-api-url
# - NEXT_PUBLIC_SUPABASE_URL
# - NEXT_PUBLIC_SUPABASE_ANON_KEY
```

## Post-Deployment

### 1. Smoke Tests

- [ ] Health check endpoint responds: `GET /health`
- [ ] API documentation accessible: `GET /docs`
- [ ] Metrics endpoint responds: `GET /metrics`
- [ ] OAuth login flow works
- [ ] Document upload succeeds
- [ ] API key creation works
- [ ] Query endpoint responds correctly
- [ ] Streaming endpoint works
- [ ] Rate limiting enforces limits
- [ ] Analytics endpoints return data

### 2. Performance Tests

- [ ] Query latency p95 < 2s
- [ ] Ingestion completes successfully
- [ ] System handles 50 concurrent users
- [ ] Database queries optimized (check slow query log)
- [ ] Vector search performs well (< 100ms)

### 3. Security Verification

- [ ] API keys properly hashed in database
- [ ] No secrets in logs
- [ ] HTTPS enforced
- [ ] CORS configured correctly
- [ ] Rate limiting active
- [ ] Tenant isolation verified (no data leakage)
- [ ] SQL injection protection verified
- [ ] XSS protection verified

### 4. Monitoring Setup

- [ ] Prometheus scraping metrics
- [ ] Grafana dashboards configured
- [ ] Sentry error tracking active
- [ ] GCP Logging configured
- [ ] Alerts configured:
  - [ ] High error rate (> 2%)
  - [ ] High latency (p95 > 3s)
  - [ ] Ingestion failures (> 5%)
  - [ ] Database connection issues
  - [ ] Redis connection issues
  - [ ] High memory usage (> 80%)
  - [ ] High CPU usage (> 80%)

### 5. Backup & Recovery

- [ ] Database backup schedule active
- [ ] Backup restoration tested
- [ ] GCS bucket versioning enabled
- [ ] Disaster recovery plan documented
- [ ] RTO/RPO defined and tested

## Production Readiness

### Documentation

- [ ] API documentation published
- [ ] User guide created
- [ ] Admin guide created
- [ ] Troubleshooting guide created
- [ ] Runbook created for on-call

### Operational

- [ ] On-call rotation established
- [ ] Incident response plan documented
- [ ] Escalation procedures defined
- [ ] Status page configured
- [ ] Customer support process defined

### Compliance (if applicable)

- [ ] GDPR compliance reviewed
- [ ] Data retention policy defined
- [ ] Privacy policy published
- [ ] Terms of service published
- [ ] Data processing agreement prepared

## Rollback Plan

In case of issues:

1. **API Rollback**:
```bash
gcloud run services update-traffic weaver-api \
  --to-revisions=PREVIOUS_REVISION=100
```

2. **Database Rollback**:
```bash
# Restore from backup
gcloud sql backups restore BACKUP_ID \
  --backup-instance=INSTANCE_NAME
```

3. **Worker Rollback**:
```bash
# Redeploy previous image version
kubectl set image deployment/weaver-worker \
  worker=gcr.io/PROJECT_ID/weaver-worker:PREVIOUS_VERSION
```

## Maintenance

### Daily

- [ ] Check error logs
- [ ] Review metrics dashboard
- [ ] Monitor ingestion queue

### Weekly

- [ ] Review slow queries
- [ ] Check storage usage
- [ ] Review security alerts
- [ ] Update dependencies (if needed)

### Monthly

- [ ] Review and optimize costs
- [ ] Analyze usage patterns
- [ ] Update documentation
- [ ] Security audit
- [ ] Performance review

## Scaling Considerations

### When to Scale Up

- API: > 70% CPU or memory usage
- Workers: Queue backlog > 100 jobs
- Database: > 80% connection pool usage
- Redis: > 75% memory usage

### Scaling Actions

- [ ] Increase Cloud Run max instances
- [ ] Add more Celery workers
- [ ] Upgrade Cloud SQL instance
- [ ] Add read replicas
- [ ] Implement caching layer
- [ ] Optimize vector indexes

## Support Contacts

- **GCP Support**: [Link]
- **Supabase Support**: [Link]
- **On-Call Engineer**: [Contact]
- **Team Lead**: [Contact]

---

**Deployment Date**: _____________

**Deployed By**: _____________

**Version**: _____________

**Sign-off**: _____________

