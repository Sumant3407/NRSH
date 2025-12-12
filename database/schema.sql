-- Supabase Database Schema for Road Safety Infrastructure Analysis System
-- Run this SQL in your Supabase SQL Editor to create the tables

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Videos table
CREATE TABLE IF NOT EXISTS videos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    filename VARCHAR(255) NOT NULL,
    video_type VARCHAR(20) NOT NULL CHECK (video_type IN ('base', 'present')),
    file_path TEXT NOT NULL,
    file_size BIGINT NOT NULL,
    upload_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    gps_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Analyses table
CREATE TABLE IF NOT EXISTS analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    base_video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    present_video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    progress INTEGER NOT NULL DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
    error TEXT,
    summary JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Detections table
CREATE TABLE IF NOT EXISTS detections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_id UUID NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
    element_type VARCHAR(50) NOT NULL CHECK (element_type IN (
        'pavement_crack',
        'faded_marking',
        'missing_stud',
        'damaged_sign',
        'roadside_furniture_damage',
        'vru_path_obstruction'
    )),
    bbox REAL[] NOT NULL CHECK (bbox IS NOT NULL AND array_length(bbox, 1) = 4), -- [x1, y1, x2, y2]
    confidence REAL NOT NULL CHECK (confidence >= 0.0 AND confidence <= 1.0),
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('minor', 'moderate', 'severe')),
    severity_score REAL NOT NULL DEFAULT 0.0 CHECK (severity_score >= 0.0 AND severity_score <= 10.0),
    gps_coords REAL[], -- [lat, lon] - stored as array for compatibility
    gps_lat REAL, -- Latitude for indexing and queries
    gps_lon REAL, -- Longitude for indexing and queries
    frame_number INTEGER,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Reports table
CREATE TABLE IF NOT EXISTS reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_id UUID NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    file_size BIGINT NOT NULL,
    generated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Road segments table
CREATE TABLE IF NOT EXISTS road_segments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255),
    gps_coords JSONB NOT NULL, -- Polygon coordinates stored as JSONB: [[lat, lon], ...] for better querying
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_videos_video_type ON videos(video_type);
CREATE INDEX IF NOT EXISTS idx_videos_created_at ON videos(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_analyses_status ON analyses(status);
CREATE INDEX IF NOT EXISTS idx_analyses_base_video ON analyses(base_video_id);
CREATE INDEX IF NOT EXISTS idx_analyses_present_video ON analyses(present_video_id);
CREATE INDEX IF NOT EXISTS idx_analyses_created_at ON analyses(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_detections_analysis_id ON detections(analysis_id);
CREATE INDEX IF NOT EXISTS idx_detections_element_type ON detections(element_type);
CREATE INDEX IF NOT EXISTS idx_detections_severity ON detections(severity);
CREATE INDEX IF NOT EXISTS idx_detections_gps_lat ON detections(gps_lat) WHERE gps_lat IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_detections_gps_lon ON detections(gps_lon) WHERE gps_lon IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_detections_gps_coords_composite ON detections(gps_lat, gps_lon) WHERE gps_lat IS NOT NULL AND gps_lon IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_reports_analysis_id ON reports(analysis_id);
CREATE INDEX IF NOT EXISTS idx_reports_generated_at ON reports(generated_at DESC);

CREATE INDEX IF NOT EXISTS idx_road_segments_gps_coords ON road_segments USING GIN (gps_coords);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Function to sync gps_coords array to gps_lat and gps_lon columns
CREATE OR REPLACE FUNCTION sync_gps_coords()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.gps_coords IS NOT NULL AND array_length(NEW.gps_coords, 1) >= 2 THEN
        NEW.gps_lat := NEW.gps_coords[1];
        NEW.gps_lon := NEW.gps_coords[2];
    ELSE
        NEW.gps_lat := NULL;
        NEW.gps_lon := NULL;
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers for updated_at (using DROP IF EXISTS to avoid errors on re-runs)
DROP TRIGGER IF EXISTS update_videos_updated_at ON videos;
CREATE TRIGGER update_videos_updated_at BEFORE UPDATE ON videos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_analyses_updated_at ON analyses;
CREATE TRIGGER update_analyses_updated_at BEFORE UPDATE ON analyses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_road_segments_updated_at ON road_segments;
CREATE TRIGGER update_road_segments_updated_at BEFORE UPDATE ON road_segments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Trigger to sync gps_coords array to separate lat/lon columns for indexing
DROP TRIGGER IF EXISTS sync_detections_gps_coords ON detections;
CREATE TRIGGER sync_detections_gps_coords BEFORE INSERT OR UPDATE ON detections
    FOR EACH ROW EXECUTE FUNCTION sync_gps_coords();

-- Enable Row Level Security (RLS) - Optional, configure based on your needs
-- ALTER TABLE videos ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE analyses ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE detections ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE reports ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE road_segments ENABLE ROW LEVEL SECURITY;

-- Create policies (example - adjust based on your authentication needs)
-- CREATE POLICY "Allow public read access" ON videos FOR SELECT USING (true);
-- CREATE POLICY "Allow public insert" ON videos FOR INSERT WITH CHECK (true);
-- CREATE POLICY "Allow public update" ON videos FOR UPDATE USING (true);
-- CREATE POLICY "Allow public delete" ON videos FOR DELETE USING (true);

-- Grant necessary permissions (adjust based on your setup)
-- GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
-- GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;

