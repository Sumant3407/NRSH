import { useState, useEffect } from 'react'
import axios from 'axios'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function AnalysisDashboard({ analysisId }) {
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (analysisId) {
      fetchResults()
    }
  }, [analysisId])

  const fetchResults = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/v1/analysis/results/${analysisId}`)
      setResults(response.data)
    } catch (error) {
      console.error('Error fetching results:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-8 text-center">
        <p>Loading analysis results...</p>
      </div>
    )
  }

  if (!results) {
    return (
      <div className="bg-white rounded-lg shadow p-8 text-center text-red-500">
        <p>Error loading results</p>
      </div>
    )
  }

  const summary = results.summary || {}
  const aggregated = summary.aggregated_results || {}

  // Prepare chart data
  const chartData = Object.entries(aggregated).map(([element, data]) => ({
    name: element.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
    minor: data.by_severity?.minor || 0,
    moderate: data.by_severity?.moderate || 0,
    severe: data.by_severity?.severe || 0,
  }))

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-2xl font-bold mb-6">Analysis Results</h2>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-blue-50 p-4 rounded-lg">
          <div className="text-sm text-gray-600">Total Issues</div>
          <div className="text-3xl font-bold text-blue-600">{summary.total_issues || 0}</div>
        </div>
        <div className="bg-red-50 p-4 rounded-lg">
          <div className="text-sm text-gray-600">Severe Issues</div>
          <div className="text-3xl font-bold text-red-600">{summary.severe_issues || 0}</div>
        </div>
        <div className="bg-green-50 p-4 rounded-lg">
          <div className="text-sm text-gray-600">Element Types</div>
          <div className="text-3xl font-bold text-green-600">{summary.element_types || 0}</div>
        </div>
      </div>

      {/* Chart */}
      {chartData.length > 0 && (
        <div className="mt-6">
          <h3 className="text-lg font-semibold mb-4">Issues by Element Type</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="minor" fill="#fbbf24" stackId="a" />
              <Bar dataKey="moderate" fill="#f59e0b" stackId="a" />
              <Bar dataKey="severe" fill="#dc2626" stackId="a" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}
