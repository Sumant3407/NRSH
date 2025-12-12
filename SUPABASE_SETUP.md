# Supabase Database Setup

This guide will help you set up Supabase database for the Road Safety Infrastructure Analysis System.

## Quick Setup

### 1. Create Supabase Project

1. Go to https://app.supabase.com and sign up/login
2. Click "New Project"
3. Fill in:
   - **Name**: Road Safety Analysis
   - **Database Password**: (choose a strong password)
   - **Region**: (select closest to you)
4. Wait 2-3 minutes for project creation

### 2. Get API Credentials

1. In Supabase dashboard, go to **Settings** → **API**
2. Copy:
   - **Project URL** → This is your `SUPABASE_URL`
   - **anon public key** → This is your `SUPABASE_KEY`

### 3. Create Database Tables

1. In Supabase dashboard, go to **SQL Editor**
2. Click **New Query**
3. Copy the entire contents of `database/schema.sql`
4. Paste and click **Run** (or press Ctrl+Enter)
5. Verify tables are created in **Table Editor**

### 4. Configure Environment

Create a `.env` file in the project root:

```bash
# Supabase Configuration

SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here

# Optional

API_HOST=0.0.0.0
API_PORT=8000
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Test Connection

The system will automatically use Supabase if credentials are configured. If not, it falls back to file-based storage.

## Database Schema

The database includes 5 tables:

- **videos**: Stores uploaded video metadata
- **analyses**: Tracks analysis jobs and status
- **detections**: Stores detected road infrastructure issues
- **reports**: Stores generated PDF reports
- **road_segments**: Defines road segments for analysis

See `database/schema.sql` for full schema details.

## Features

✅ **Automatic Fallback**: If Supabase is not configured, the system uses file-based storage
✅ **Real-time Updates**: Status updates are stored in database
✅ **Efficient Queries**: Indexed tables for fast lookups
✅ **Scalable**: Handles large volumes of data

## Troubleshooting

- *Connection Failed?**
- Check `SUPABASE_URL` and `SUPABASE_KEY` in `.env`
- Verify tables exist in Supabase dashboard
- Check network/firewall settings

- *Tables Not Found?**
- Run `database/schema.sql` in SQL Editor
- Check for errors in SQL execution

- *Data Not Saving?**
- Check Supabase logs in dashboard
- Verify RLS policies if enabled
- Check application logs for errors

## Next Steps

1. Configure Row Level Security (RLS) for production
2. Set up authentication if needed
3. Configure backups
4. Monitor usage in Supabase dashboard

For more details, see `database/README.md`.
