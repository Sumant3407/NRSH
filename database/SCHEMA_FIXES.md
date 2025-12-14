# Database Schema Fixes Applied

## Issues Fixed

### 1. **GIST Index on REAL[] Array (Line 86)**

- *Problem:** GIST indexes cannot be created directly on simple REAL[] arrays without proper extensions.

- *Solution:**
- Added separate `gps_lat` and `gps_lon` columns for better indexing
- Created composite index on (gps_lat, gps_lon) for efficient geospatial queries
- Added trigger to automatically sync these columns from the `gps_coords` array
- Maintains backward compatibility - code can still use `gps_coords` array

### 2. **REAL[][] for Road Segments (Line 69)**

- *Problem:** Multidimensional arrays (REAL[][]) are less flexible for querying polygon coordinates.

- *Solution:**
- Changed `gps_coords` in `road_segments` table from `REAL[][]` to `JSONB`
- Added GIN index on JSONB column for efficient JSON queries
- JSONB provides better querying capabilities and is more flexible

### 3. **Trigger Re-creation Errors**

- *Problem:** Triggers would fail if schema was run multiple times.

- *Solution:**
- Added `DROP TRIGGER IF EXISTS` before creating triggers
- Prevents errors when re-running the schema

### 4. **Improved NULL Handling**

- *Problem:** CHECK constraint on bbox didn't explicitly handle NULL cases.

- *Solution:**
- Enhanced CHECK constraint: `bbox IS NOT NULL AND array_length(bbox, 1) = 4`
- Added partial indexes with `WHERE` clauses for NULL-safe indexing

## New Features

### Automatic GPS Coordinate Synchronization

- When `gps_coords` array is inserted/updated, `gps_lat` and `gps_lon` are automatically populated
- This allows efficient indexing while maintaining API compatibility
- Code can continue using `gps_coords` array format

### Better Indexing Strategy

- Composite index on (gps_lat, gps_lon) for efficient range queries
- Partial indexes (only on non-NULL values) for better performance
- GIN index on JSONB column for flexible polygon queries

## Migration Notes

If you have an existing database:

1. **For detections table:**
   ```sql
   ALTER TABLE detections ADD COLUMN IF NOT EXISTS gps_lat REAL;
   ALTER TABLE detections ADD COLUMN IF NOT EXISTS gps_lon REAL;

   - - Populate existing data
   UPDATE detections
   SET gps_lat = gps_coords[1],
       gps_lon = gps_coords[2]
   WHERE gps_coords IS NOT NULL AND array_length(gps_coords, 1) >= 2;
   ```

2. **For road_segments table:**
   ```sql
   - - Convert REAL[][] to JSONB (if you have existing data)
   - - This requires manual conversion based on your data structure
   ```

## Testing

After applying the schema, test with:

```sql
- - Test GPS coordinate sync
INSERT INTO detections (analysis_id, element_type, bbox, confidence, severity, gps_coords)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'pavement_crack',
    ARRAY[10.0, 20.0, 30.0, 40.0],
    0.95,
    'moderate',
    ARRAY[28.7041, 77.1025]  -- Delhi coordinates
);

- - Verify lat/lon were populated
SELECT gps_coords, gps_lat, gps_lon FROM detections WHERE gps_coords IS NOT NULL;
```

## Compatibility

**Backward Compatible:** Existing code using `gps_coords` array will continue to work
**Forward Compatible:** New code can use either `gps_coords` array or `gps_lat`/`gps_lon` columns
**Performance:** Better indexing for geospatial queries
