import { useState } from 'react'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function VideoUpload({ onAnalysisComplete }) {
  const [baseVideo, setBaseVideo] = useState(null)
  const [presentVideo, setPresentVideo] = useState(null)
  const [baseVideoId, setBaseVideoId] = useState(null)
  const [presentVideoId, setPresentVideoId] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [analyzing, setAnalyzing] = useState(false)
  const [message, setMessage] = useState('')

  const handleBaseVideoChange = (e) => {
    setBaseVideo(e.target.files[0])
  }

  const handlePresentVideoChange = (e) => {
    setPresentVideo(e.target.files[0])
  }

  const uploadVideo = async (file, videoType) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('video_type', videoType)

    const response = await axios.post(
      `${API_URL}/api/v1/video/upload`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )

    return response.data.video_id
  }

  const handleUpload = async () => {
    if (!baseVideo || !presentVideo) {
      setMessage('Please select both base and present videos')
      return
    }

    setUploading(true)
    setMessage('Uploading videos...')

    try {
      const baseId = await uploadVideo(baseVideo, 'base')
      setBaseVideoId(baseId)
      
      const presentId = await uploadVideo(presentVideo, 'present')
      setPresentVideoId(presentId)

      setMessage('Videos uploaded successfully!')
      
      // Start analysis
      await startAnalysis(baseId, presentId)
    } catch (error) {
      setMessage(`Error: ${error.response?.data?.detail || error.message}`)
    } finally {
      setUploading(false)
    }
  }

  const startAnalysis = async (baseId, presentId) => {
    setAnalyzing(true)
    setMessage('Starting analysis...')

    try {
      const response = await axios.post(`${API_URL}/api/v1/analysis/start`, {
        base_video_id: baseId,
        present_video_id: presentId,
      })

      const analysisId = response.data.analysis_id
      setMessage(`Analysis started: ${analysisId}`)
      
      // Poll for completion
      pollAnalysisStatus(analysisId)
    } catch (error) {
      setMessage(`Error starting analysis: ${error.response?.data?.detail || error.message}`)
      setAnalyzing(false)
    }
  }

  const pollAnalysisStatus = async (analysisId) => {
    const checkStatus = async () => {
      try {
        const response = await axios.get(`${API_URL}/api/v1/analysis/status/${analysisId}`)
        const status = response.data.status
        const progress = response.data.progress || 0

        setMessage(`Analysis in progress: ${progress}%`)

        if (status === 'completed') {
          setMessage('Analysis completed!')
          setAnalyzing(false)
          if (onAnalysisComplete) {
            onAnalysisComplete(analysisId)
          }
        } else if (status === 'failed') {
          setMessage(`Analysis failed: ${response.data.error || 'Unknown error'}`)
          setAnalyzing(false)
        } else {
          setTimeout(checkStatus, 2000) // Check again in 2 seconds
        }
      } catch (error) {
        setMessage(`Error checking status: ${error.message}`)
        setAnalyzing(false)
      }
    }

    checkStatus()
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-bold mb-4">Upload Videos</h2>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Base Video (Reference)
          </label>
          <input
            type="file"
            accept="video/*"
            onChange={handleBaseVideoChange}
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            disabled={uploading || analyzing}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Present Video (Current)
          </label>
          <input
            type="file"
            accept="video/*"
            onChange={handlePresentVideoChange}
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            disabled={uploading || analyzing}
          />
        </div>

        <button
          onClick={handleUpload}
          disabled={uploading || analyzing || !baseVideo || !presentVideo}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          {uploading ? 'Uploading...' : analyzing ? 'Analyzing...' : 'Upload & Analyze'}
        </button>

        {message && (
          <div className={`p-3 rounded ${message.includes('Error') ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700'}`}>
            {message}
          </div>
        )}
      </div>
    </div>
  )
}
