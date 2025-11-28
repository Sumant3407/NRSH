# Database Setup Guide

This guide explains how to set up the Supabase database for the Road Safety Infrastructure Analysis System.

## Prerequisites

1. A Supabase account (sign up at https://supabase.com)
2. A new Supabase project created

## Setup Steps

### 1. Create Supabase Project

1. Go to https://app.supabase.com
2. Click "New Project"
3. Fill in project details:
   - Name: Road Safety Analysis (or your preferred name)
   - Database Password: Choose a strong password
   - Region: Select closest region
4. Wait for project to be created (takes a few minutes)

### 2. Get API Credentials

1. In your Supabase project dashboard, go to **Settings** → **API**
2. Copy the following values:
   - **Project URL** (SUPABASE_URL)
   - **anon/public key** (SUPABASE_KEY)
3. Save these for later use

### 3. Create Database Tables

1. In your Supabase project, go to **SQL Editor**
2. Click "New Query"
3. Copy and paste the contents of `database/schema.sql`
4. Click "Run" to execute the SQL
5. Verify tables are created by checking **Table Editor**

### 4. Configure Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your Supabase credentials:
   ```
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_KEY=your-anon-key-here
   ```

### 5. Install Python Dependencies

Make sure you have the Supabase Python client installed:
```bash
pip install -r requirements.txt
```

### 6. Verify Connection

Run a test script to verify the connection:
```python
from backend.services.database_service import get_database_service

db = get_database_service()
if db:
    print("✅ Database connection successful!")
else:
    print("❌ Database connection failed. Check your credentials.")
```

## Database Schema

The database consists of 5 main tables:

### 1. `videos`
Stores uploaded video files and metadata
- `id`: Unique identifier (UUID)
- `filename`: Original filename
- `video_type`: 'base' or 'present'
- `file_path`: Path to video file
- `file_size`: File size in bytes
- `gps_data`: Optional GPS metadata (JSONB)
- `upload_date`: Upload timestamp

### 2. `analyses`
Stores analysis jobs and their status
- `id`: Unique identifier (UUID)
- `base_video_id`: Reference to base video
- `present_video_id`: Reference to present video
- `status`: 'pending', 'processing', 'completed', 'failed'
- `progress`: Progress percentage (0-100)
- `error`: Error message if failed
- `summary`: Analysis summary (JSONB)

### 3. `detections`
Stores detected road infrastructure issues
- `id`: Unique identifier (UUID)
- `analysis_id`: Reference to analysis
- `element_type`: Type of detected element
- `bbox`: Bounding box coordinates [x1, y1, x2, y2]
- `confidence`: Detection confidence (0.0-1.0)
- `severity`: 'minor', 'moderate', 'severe'
- `severity_score`: Numeric severity score (0.0-10.0)
- `gps_coords`: GPS coordinates [lat, lon]
- `frame_number`: Frame number in video

### 4. `reports`
Stores generated PDF reports
- `id`: Unique identifier (UUID)
- `analysis_id`: Reference to analysis
- `file_path`: Path to report file
- `file_size`: File size in bytes
- `generated_at`: Generation timestamp

### 5. `road_segments`
Stores road segment definitions
- `id`: Unique identifier (UUID)
- `name`: Segment name
- `gps_coords`: Polygon coordinates [[lat, lon], ...]
- `created_at`, `updated_at`: Timestamps

## Indexes

The schema includes indexes for:
- Video type and creation date
- Analysis status and video references
- Detection analysis ID, element type, severity, and GPS coordinates
- Report analysis ID and generation date

## Row Level Security (RLS)

RLS is disabled by default. To enable it:

1. Uncomment RLS lines in `schema.sql`
2. Create appropriate policies based on your authentication needs
3. Configure authentication in your application

## Migration from File-based Storage

If you're migrating from file-based storage:

1. The system will automatically use Supabase if credentials are configured
2. Existing file-based data won't be automatically migrated
3. You can create a migration script to import existing data

## Troubleshooting

### Connection Errors

- **"Invalid API key"**: Check that SUPABASE_KEY is correct
- **"Invalid URL"**: Verify SUPABASE_URL format
- **"Connection timeout"**: Check network/firewall settings

### Table Errors

- **"Table does not exist"**: Run `schema.sql` in SQL Editor
- **"Permission denied"**: Check RLS policies if enabled

### Data Type Errors

- **"Invalid enum value"**: Check that enum values match schema
- **"Array length mismatch"**: Verify bbox and gps_coords formats

## Best Practices

1. **Backup**: Regularly backup your database
2. **Indexes**: Monitor query performance and add indexes as needed
3. **RLS**: Enable RLS for production deployments
4. **Monitoring**: Use Supabase dashboard to monitor usage
5. **Connection Pooling**: Configure connection pooling for production

## Support

For issues:
- Check Supabase documentation: https://supabase.com/docs
- Review error messages in application logs
- Check Supabase project logs in dashboard

