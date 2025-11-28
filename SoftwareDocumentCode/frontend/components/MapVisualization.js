'use client'

import { useState, useEffect } from 'react'
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'
import axios from 'axios'

// Fix for default marker icons in Next.js
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

function MapUpdater({ bounds }) {
  const map = useMap()
  
  useEffect(() => {
    if (bounds) {
      map.fitBounds([
        [bounds.south, bounds.west],
        [bounds.north, bounds.east]
      ])
    }
  }, [bounds, map])
  
  return null
}

export default function MapVisualization({ analysisId }) {
  const [mapData, setMapData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (analysisId) {
      fetchMapData()
    }
  }, [analysisId])

  const fetchMapData = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/v1/dashboard/map-data/${analysisId}`)
      setMapData(response.data)
    } catch (error) {
      console.error('Error fetching map data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-8 text-center">
        <p>Loading map data...</p>
      </div>
    )
  }

  if (!mapData || !mapData.markers || mapData.markers.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
        <p>No geospatial data available</p>
      </div>
    )
  }

  // Default center if no bounds
  const center = mapData.bounds 
    ? [(mapData.bounds.north + mapData.bounds.south) / 2, (mapData.bounds.east + mapData.bounds.west) / 2]
    : [12.9716, 77.5946] // Default to Bangalore

  const getMarkerColor = (severity) => {
    switch (severity) {
      case 'severe':
        return '#dc2626'
      case 'moderate':
        return '#f59e0b'
      default:
        return '#fbbf24'
    }
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-2xl font-bold mb-4">Geospatial Visualization</h2>
      <div style={{ height: '500px', width: '100%' }}>
        <MapContainer
          center={center}
          zoom={13}
          style={{ height: '100%', width: '100%' }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {mapData.bounds && <MapUpdater bounds={mapData.bounds} />}
          {mapData.markers.map((marker, idx) => (
            <Marker
              key={idx}
              position={[marker.lat, marker.lon]}
              icon={L.divIcon({
                className: 'custom-marker',
                html: `<div style="background-color: ${getMarkerColor(marker.severity)}; width: 20px; height: 20px; border-radius: 50%; border: 2px solid white;"></div>`,
                iconSize: [20, 20],
              })}
            >
              <Popup>
                <div>
                  <strong>{marker.element_type.replace(/_/g, ' ')}</strong><br />
                  Severity: {marker.severity}<br />
                  Confidence: {(marker.confidence * 100).toFixed(1)}%
                </div>
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>
    </div>
  )
}
