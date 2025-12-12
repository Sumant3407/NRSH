import { useState, useEffect } from 'react';
import Head from 'next/head';
import dynamic from 'next/dynamic';
import VideoUpload from '../components/VideoUpload';
import AnalysisDashboard from '../components/AnalysisDashboard';

const MapVisualization = dynamic(
  () => import('../components/MapVisualization'),
  { ssr: false },
);

export default // Function: Home
// Function: Home
function Home() {
  const [analyses, setAnalyses] = useState([]);
  const [selectedAnalysis, setSelectedAnalysis] = useState(null);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      <Head>
        <title>Road Safety Infrastructure Analysis</title>
        <meta
          name="description"
          content="AI-powered road infrastructure analysis system"
        />
        <link rel="icon" href="/favicon.ico" />
        <link
          rel="stylesheet"
          href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
        />
      </Head>

      <header className="bg-gradient-to-r from-blue-900 to-indigo-900 text-white shadow-xl">
        <div className="container mx-auto px-6 py-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold tracking-tight">
                Road Safety Analysis
              </h1>
              <p className="mt-2 text-blue-200 text-lg">
                AI-Powered Infrastructure Monitoring
              </p>
              <p className="text-blue-300 text-sm">
                National Road Safety Hackathon 2025
              </p>
            </div>
            <div className="hidden md:block">
              <svg
                className="w-16 h-16 text-blue-300"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                />
              </svg>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-12">
        <div className="mb-8 text-center">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">
            Analyze Road Infrastructure Changes
          </h2>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Upload reference and current media to detect infrastructure changes,
            identify safety hazards, and generate comprehensive analysis reports
            using advanced AI technology.
          </p>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-4 gap-8">
          {}
          <div className="xl:col-span-1">
            <VideoUpload
              onAnalysisComplete={(analysisId) => {
                setSelectedAnalysis(analysisId);
              }}
            />
          </div>

          {}
          <div className="xl:col-span-3">
            {selectedAnalysis ? (
              <AnalysisDashboard analysisId={selectedAnalysis} />
            ) : (
              <div className="bg-white rounded-xl shadow-lg p-12 text-center">
                <div className="mb-6">
                  <svg
                    className="w-16 h-16 text-gray-300 mx-auto"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={1.5}
                      d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                    />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-gray-700 mb-2">
                  Ready to Analyze
                </h3>
                <p className="text-gray-500">
                  Upload videos or images to start detecting infrastructure
                  changes and safety improvements
                </p>
              </div>
            )}
          </div>
        </div>

        {}
        {selectedAnalysis && (
          <div className="mt-8">
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
  );
}
