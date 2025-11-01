# Video Storage Management

This document describes the video storage infrastructure for candidate interview recordings using Supabase Storage.

## Overview

Interview videos are recorded during candidate sessions and stored in Supabase Storage for recruiter review. The system implements automated retention policies, GDPR-compliant deletion, and cost monitoring to manage storage efficiently.

## Storage Configuration

### Supabase Storage Bucket

**Bucket Name:** `interview-recordings`

**Configuration:**
- **Access:** Private (requires authentication)
- **Max File Size:** 100MB per video file
- **Allowed Formats:** MP4, WebM
- **Encryption:** At-rest encryption enabled (Supabase default)
- **File Path Structure:** `{organization_id}/{interview_id}/recording.mp4`

### Environment Variables

Required configuration in `.env`:

```bash
# Supabase Storage
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_KEY=your_service_role_key_here
SUPABASE_ANON_KEY=your_anon_key_here  # Optional

# Video Retention Policy
VIDEO_RETENTION_DAYS=30              # Days before soft delete
HARD_DELETE_AFTER_DAYS=90           # Days after soft delete before permanent removal
VIDEO_STORAGE_THRESHOLD_GB=100      # Storage quota alert threshold
```

## Video Retention Policy

The system implements a two-stage deletion policy for GDPR compliance and cost management:

### Stage 1: Soft Delete (After 30 Days)

- Videos older than `VIDEO_RETENTION_DAYS` (default: 30 days) are automatically soft-deleted
- Soft delete marks the `deleted_at` timestamp in the `video_recordings` table
- Video file remains in storage but is hidden from queries
- Allows recovery if needed within the grace period

### Stage 2: Hard Delete (After 90 Days)

- Videos soft-deleted for more than `HARD_DELETE_AFTER_DAYS` (default: 90 days) are permanently removed
- Hard delete removes the video file from Supabase Storage
- Database record is deleted permanently
- Action is irreversible

### Manual Deletion

Candidates and recruiters can request immediate video deletion via the API:

```bash
# Delete video for specific interview
DELETE /api/v1/videos/{interview_id}
Authorization: Bearer {user_token}
```

**Authorization:**
- Candidates can delete their own interview videos
- Recruiters can delete videos from their organization
- Admins can delete any video

**Response:**
- `204 No Content` - Video successfully marked for deletion
- `403 Forbidden` - User lacks permission
- `404 Not Found` - Video does not exist

## Automated Cleanup Job

### Cleanup Script

**Location:** `backend/scripts/cleanup_videos.py`

**Purpose:** Automatically soft-delete expired videos and hard-delete old soft-deleted videos

**Schedule:** Daily at 2:00 AM (configured via cron)

### Running Manually

```bash
# From backend directory
cd /path/to/backend
python scripts/cleanup_videos.py

# Or with Poetry
poetry run python scripts/cleanup_videos.py

# Or with uv
uv run python scripts/cleanup_videos.py
```

### Cron Configuration

Add to system crontab or container orchestrator:

```bash
# Run cleanup daily at 2 AM
0 2 * * * cd /app/backend && python scripts/cleanup_videos.py >> /var/log/video_cleanup.log 2>&1
```

### Cleanup Output

The script outputs a summary of actions taken:

```json
{
  "soft_deleted": 12,
  "hard_deleted": 3,
  "errors": 0,
  "storage_usage_gb": 45.2,
  "timestamp": "2025-11-01T02:00:00Z"
}
```

## Storage Monitoring

### Usage Monitoring Endpoint

**Endpoint:** `GET /api/v1/admin/storage/usage`

**Authorization:** Admin only

**Response:**
```json
{
  "total_size_bytes": 48578306867,
  "total_size_gb": 45.2,
  "file_count": 342,
  "threshold_gb": 100,
  "usage_percentage": 45.2
}
```

### Storage Alerts

The system automatically logs warnings when storage usage exceeds the configured threshold:

- **Threshold:** `VIDEO_STORAGE_THRESHOLD_GB` (default: 100GB)
- **Alert Type:** Structured log entry with `level=WARNING`
- **Action:** Review retention policy or increase storage quota

**Log Example:**
```
WARNING: Storage usage exceeded threshold
{
  "event": "storage_threshold_exceeded",
  "current_usage_gb": 105.3,
  "threshold_gb": 100,
  "usage_percentage": 105.3
}
```

## Cost Management

### Storage Costs

**Supabase Pricing:** ~$0.021/GB/month

**Estimated Costs:**
- 720p video, 20 minutes: ~150MB
- Cost per video: ~$0.003/month
- 1000 videos: ~$3.15/month
- Target: <$0.10 per interview over 30-day retention

### Cost Optimization Strategies

1. **Automated Cleanup:** Daily job removes expired videos
2. **Retention Limits:** 30-day default retention (configurable per organization)
3. **Quality Settings:** 720p @ 30fps balances quality and file size
4. **Compression:** H.264 codec provides efficient compression
5. **Monitoring:** Threshold alerts prevent unexpected overage

## GDPR Compliance

### Data Subject Rights

**Right to Deletion:**
- Candidates can request immediate video deletion via API
- Deletion requests processed within 7 days (automatic soft delete)
- Hard delete after 90-day grace period

**Right to Access:**
- Candidates can view their interview recordings (signed URLs)
- Recruiters can access videos from their organization only

**Data Retention:**
- Videos retained for 30 days by default
- Extended retention configurable per organization (post-MVP)
- Automatic deletion after retention period

### Audit Trail

- All video deletions logged in application logs
- Metadata retained in database even after video file deletion
- `storage_path` set to NULL after hard delete for audit purposes

## Row Level Security (RLS)

Supabase Storage uses Row Level Security policies to enforce access control. These policies must be configured manually in the Supabase dashboard.

### Configuration Steps

1. Navigate to: Supabase Dashboard > Storage > interview-recordings > Policies
2. Create the following policies:

### Policy 1: Authenticated Upload

**Policy Name:** `authenticated_upload`
**Operation:** INSERT
**Target Roles:** authenticated

**Policy Expression:**
```sql
bucket_id = 'interview-recordings' 
AND (storage.foldername(name))[1] = auth.uid()::text
```

**Purpose:** Users can only upload to their own organization's folder

### Policy 2: Organization Member Read

**Policy Name:** `org_member_read`
**Operation:** SELECT
**Target Roles:** authenticated

**Policy Expression:**
```sql
-- User must belong to same organization as the interview
-- Implement based on your organization membership logic
```

**Purpose:** Users can only read videos from interviews in their organization

### Policy 3: Service Role All Operations

**Policy Name:** `service_role_all`
**Operation:** ALL
**Target Roles:** service_role

**Policy Expression:**
```sql
bucket_id = 'interview-recordings'
```

**Purpose:** Backend service can manage all files for cleanup and admin tasks

## Troubleshooting

### Video Upload Fails

**Symptoms:** Video chunks fail to upload during interview

**Common Causes:**
1. Network connectivity issues
2. Supabase service key invalid/expired
3. Storage bucket misconfigured
4. File size exceeds 100MB limit

**Resolution:**
```bash
# Test Supabase connection
curl -X GET "${SUPABASE_URL}/storage/v1/bucket/interview-recordings" \
  -H "Authorization: Bearer ${SUPABASE_SERVICE_KEY}"

# Check bucket exists and is accessible
# Verify environment variables are set correctly
```

### Cleanup Script Fails

**Symptoms:** Daily cleanup job not running or throwing errors

**Common Causes:**
1. Database connection issues
2. Supabase authentication failure
3. RLS policies blocking service role

**Resolution:**
```bash
# Run cleanup manually with verbose output
python scripts/cleanup_videos.py

# Check logs for specific errors
tail -f /var/log/video_cleanup.log

# Verify service role key has full permissions
```

### Storage Usage Not Decreasing

**Symptoms:** Storage usage remains high despite cleanup

**Common Causes:**
1. Videos not being soft-deleted (retention period not met)
2. Hard delete not running (grace period not met)
3. Supabase Storage bucket not refreshing usage stats

**Resolution:**
```bash
# Check how many videos are pending deletion
# Query video_recordings table for deleted_at timestamps

# Force hard delete of old soft-deleted videos
python scripts/cleanup_videos.py --force-hard-delete

# Check Supabase dashboard for actual storage usage
```

## API Reference

### Delete Video

```http
DELETE /api/v1/videos/{interview_id}
Authorization: Bearer {token}
```

**Parameters:**
- `interview_id` (path, UUID) - Interview ID

**Response:**
- `204 No Content` - Success
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Video not found

### Get Storage Usage (Admin)

```http
GET /api/v1/admin/storage/usage
Authorization: Bearer {admin_token}
```

**Response:**
```json
{
  "total_size_bytes": 48578306867,
  "total_size_gb": 45.2,
  "file_count": 342,
  "threshold_gb": 100,
  "usage_percentage": 45.2
}
```

## Related Documentation

- **Architecture:** `docs/architecture/backend/06-external-apis-services.md#supabase-storage`
- **Database Schema:** `docs/stories/2.0.video-interview-database-schema.md`
- **Cleanup Service:** `backend/app/services/video_cleanup_service.py`
- **Storage Client:** `backend/app/utils/supabase_storage.py`
- **Epic:** `docs/epics/epic-02-video-interview-experience.md#story-28`
