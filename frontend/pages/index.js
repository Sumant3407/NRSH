import { useState, useEffect } from 'react'
import Head from 'next/head'
import dynamic from 'next/dynamic'
import VideoUpload from '../components/VideoUpload'
import AnalysisDashboard from '../components/AnalysisDashboard'

// Dynamically import MapVisualization to disable SSR (Leaflet needs window)
const MapVisualization = dynamic(() => import('../components/MapVisualization'), { ssr: false })

export default function Home() {
  const [analyses, setAnalyses] = useState([])
  const [selectedAnalysis, setSelectedAnalysis] = useState(null)

  return (
    <div className="min-h-screen bg-gray-50">
      <Head>
        <title>Road Safety Infrastructure Analysis</title>
        <meta name="description" content="AI-powered road infrastructure analysis system" />
        <link rel="icon" href="/favicon.ico" />
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
      </Head>

      <header className="bg-blue-900 text-white shadow-lg">
        <div className="container mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold">Road Safety Infrastructure Analysis</h1>
          <p className="mt-2 text-blue-200">National Road Safety Hackathon 2025</p>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Upload Section */}
          <div className="lg:col-span-1">
            <VideoUpload 
              onAnalysisComplete={(analysisId) => {
                setSelectedAnalysis(analysisId)
              }}
            />
          </div>

          {/* Dashboard Section */}
          <div className="lg:col-span-2">
            {selectedAnalysis ? (
              <AnalysisDashboard analysisId={selectedAnalysis} />
            ) : (
              <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
                <p>Upload videos to start analysis</p>
              </div>
            )}
          </div>
        </div>

        {/* Map Visualization */}
        {selectedAnalysis && (
          <div className="mt-6">
            <MapVisualization analysisId={selectedAnalysis} />
          </div>
        )}
      </main>

      <footer className="bg-gray-800 text-white mt-12 py-6">
        <div className="container mx-auto px-4 text-center">
          <p>&copy; 2025 Road Safety Infrastructure Analysis System</p>
        </div>
      </footer>
    </div>
  )
}
