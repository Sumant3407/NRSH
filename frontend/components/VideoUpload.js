import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import PropTypes from 'prop-types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const AXIOS_TIMEOUT = parseInt(
  process.env.NEXT_PUBLIC_AXIOS_TIMEOUT_MS || '15000',
  10,
);
const POLL_INTERVAL_MS = parseInt(
  process.env.NEXT_PUBLIC_POLL_INTERVAL_MS || '2000',
  10,
);
const POLL_MAX_RETRIES = parseInt(
  process.env.NEXT_PUBLIC_POLL_MAX_RETRIES || '60',
  10,
);

export default // Function: VideoUpload
// Function: VideoUpload
function VideoUpload({ onAnalysisComplete }) {
  const [baseVideo, setBaseVideo] = useState(null);
  const [presentVideo, setPresentVideo] = useState(null);
  const [baseVideoId, setBaseVideoId] = useState(null);
  const [presentVideoId, setPresentVideoId] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [message, setMessage] = useState('');
  const [singleDetection, setSingleDetection] = useState(false);

  const [activeAnalysisId, setActiveAnalysisId] = useState(null);
  const pollTimeoutRef = useRef(null);
  const pollRetryRef = useRef(0);

  // Function: handleBaseVideoChange
  const handleBaseVideoChange = (e) => {
    setBaseVideo(e.target.files[0]);
  };

  // Function: handlePresentVideoChange
  const handlePresentVideoChange = (e) => {
    setPresentVideo(e.target.files[0]);
  };

  const uploadVideo = async (file, videoType) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('video_type', videoType);

    const response = await axios.post(
      `${API_URL}/api/v1/video/upload`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: AXIOS_TIMEOUT,
      },
    );

    return response.data.video_id;
  };

  const handleUpload = async () => {
    if (singleDetection) {
      if (!baseVideo) {
        setMessage('Please select a media file for single detection');
        return;
      }
    } else {
      if (!baseVideo || !presentVideo) {
        setMessage('Please select both base and present media files');
        return;
      }
    }

    setUploading(true);
    setMessage('Uploading media...');

    try {
      if (singleDetection) {
        const mediaId = await uploadVideo(baseVideo, 'present');
        setBaseVideoId(mediaId);
        setPresentVideoId(null);
        setMessage('Media uploaded successfully!');
        await startSingleDetection(mediaId);
      } else {
        const baseId = await uploadVideo(baseVideo, 'base');
        setBaseVideoId(baseId);

        const presentId = await uploadVideo(presentVideo, 'present');
        setPresentVideoId(presentId);

        setMessage('Media uploaded successfully!');

        await startAnalysis(baseId, presentId);
      }
    } catch (error) {
      setMessage(`Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setUploading(false);
    }
  };

  const startSingleDetection = async (mediaId) => {
    setAnalyzing(true);
    setMessage('Running single-media detection...');

    try {
      const response = await axios.post(
        `${API_URL}/api/v1/analysis/detect`,
        {
          video_id: mediaId,
        },
        { timeout: AXIOS_TIMEOUT },
      );

      const analysisId = response.data.analysis_id;
      setMessage('Single-media detection completed!');
      setAnalyzing(false);
      if (onAnalysisComplete) {
        onAnalysisComplete(analysisId);
      }
    } catch (error) {
      setMessage(
        `Error running detection: ${error.response?.data?.detail || error.message}`,
      );
      setAnalyzing(false);
    }
  };

  const startAnalysis = async (baseId, presentId) => {
    setAnalyzing(true);
    setMessage('Starting analysis...');

    try {
      const response = await axios.post(
        `${API_URL}/api/v1/analysis/start`,
        {
          base_video_id: baseId,
          present_video_id: presentId,
        },
        { timeout: AXIOS_TIMEOUT },
      );

      const analysisId = response.data.analysis_id;
      setMessage(`Analysis started: ${analysisId}`);

      pollRetryRef.current = 0;

      setActiveAnalysisId(analysisId);
    } catch (error) {
      setMessage(
        `Error starting analysis: ${error.response?.data?.detail || error.message}`,
      );
      setAnalyzing(false);
    }
  };

  useEffect(() => {
    if (!activeAnalysisId) return;

    let cancelled = false;

    const checkStatus = async () => {
      try {
        const response = await axios.get(
          `${API_URL}/api/v1/analysis/status/${activeAnalysisId}`,
          { timeout: AXIOS_TIMEOUT },
        );
        const status = response.data.status;
        const progress = response.data.progress || 0;

        if (cancelled) return;

        setMessage(`Analysis in progress: ${progress}%`);

        if (status === 'completed') {
          if (pollTimeoutRef.current) {
            clearTimeout(pollTimeoutRef.current);
            pollTimeoutRef.current = null;
          }
          setMessage('Analysis completed!');
          setAnalyzing(false);
          const aId = activeAnalysisId;
          setActiveAnalysisId(null);
          if (onAnalysisComplete) {
            onAnalysisComplete(aId);
          }
        } else if (status === 'failed') {
          if (pollTimeoutRef.current) {
            clearTimeout(pollTimeoutRef.current);
            pollTimeoutRef.current = null;
          }
          setMessage(
            `Analysis failed: ${response.data.error || 'Unknown error'}`,
          );
          setAnalyzing(false);
          setActiveAnalysisId(null);
        } else {
          pollRetryRef.current = (pollRetryRef.current || 0) + 1;
          if (pollRetryRef.current > POLL_MAX_RETRIES) {
            setMessage('Analysis polling timed out');
            setAnalyzing(false);
            setActiveAnalysisId(null);
            return;
          }

          pollTimeoutRef.current = setTimeout(() => {
            checkStatus();
          }, POLL_INTERVAL_MS);
        }
      } catch (error) {
        if (pollTimeoutRef.current) {
          clearTimeout(pollTimeoutRef.current);
          pollTimeoutRef.current = null;
        }
        if (!cancelled) {
          setMessage(`Error checking status: ${error.message}`);
          setAnalyzing(false);
          setActiveAnalysisId(null);
        }
      }
    };

    checkStatus();

    return () => {
      cancelled = true;
      if (pollTimeoutRef.current) {
        clearTimeout(pollTimeoutRef.current);
        pollTimeoutRef.current = null;
      }
    };
  }, [activeAnalysisId]);

  useEffect(() => {
    if (!analyzing) {
      if (pollTimeoutRef.current) {
        clearTimeout(pollTimeoutRef.current);
        pollTimeoutRef.current = null;
      }
      if (activeAnalysisId) {
        setActiveAnalysisId(null);
      }
    }
  }, [analyzing]);

  return (
    <div className="bg-gradient-to-br from-blue-50 to-indigo-100 rounded-xl shadow-lg p-8 border border-blue-200">
      <div className="flex items-center mb-6">
        <div className="bg-blue-600 rounded-full p-3 mr-4">
          <svg
            className="w-6 h-6 text-white"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
            />
          </svg>
        </div>
        <h2 className="text-2xl font-bold text-gray-800">Upload Media</h2>
      </div>

      <div className="flex items-center mb-6">
        <input
          id="single-detection"
          type="checkbox"
          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          checked={singleDetection}
          onChange={(e) => setSingleDetection(e.target.checked)}
          disabled={uploading || analyzing}
        />
        <label
          htmlFor="single-detection"
          className="ml-3 block text-sm font-medium text-gray-700"
        >
          Single-media detection (no comparison)
        </label>
      </div>

      <div className="space-y-6">
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-3 flex items-center">
            <svg
              className="w-4 h-4 mr-2 text-blue-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
              />
            </svg>
            Base Media (Reference)
          </label>
          <input
            type="file"
            accept="video/*,image/*"
            onChange={handleBaseVideoChange}
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-3 file:px-6 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 transition-colors"
            disabled={uploading || analyzing}
          />
        </div>

        {!singleDetection && (
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-3 flex items-center">
              <svg
                className="w-4 h-4 mr-2 text-green-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
                />
              </svg>
              Present Media (Current)
            </label>
            <input
              type="file"
              accept="video/*,image/*"
              onChange={handlePresentVideoChange}
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-3 file:px-6 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-green-50 file:text-green-700 hover:file:bg-green-100 transition-colors"
              disabled={uploading || analyzing}
            />
          </div>
        )}

        <button
          onClick={handleUpload}
          disabled={
            uploading ||
            analyzing ||
            (singleDetection ? !baseVideo : !baseVideo || !presentVideo)
          }
          className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center font-semibold"
        >
          {(uploading || analyzing) && (
            <svg
              className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              ></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
          )}
          {uploading
            ? 'Uploading...'
            : analyzing
              ? 'Analyzing...'
              : 'Upload & Analyze'}
        </button>

        {message && (
          <div
            className={`p-4 rounded-lg border-l-4 flex items-start ${
              message.includes('Error')
                ? 'bg-red-50 border-red-400 text-red-800'
                : message.includes('completed') ||
                    message.includes('successfully')
                  ? 'bg-green-50 border-green-400 text-green-800'
                  : 'bg-blue-50 border-blue-400 text-blue-800'
            }`}
          >
            <div className="flex-shrink-0 mr-3">
              {message.includes('Error') ? (
                <svg
                  className="w-5 h-5 text-red-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              ) : message.includes('completed') ||
                message.includes('successfully') ? (
                <svg
                  className="w-5 h-5 text-green-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              ) : (
                <svg
                  className="w-5 h-5 text-blue-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              )}
            </div>
            <div className="text-sm font-medium">{message}</div>
          </div>
        )}
      </div>
    </div>
  );
}

VideoUpload.propTypes = {
  onAnalysisComplete: PropTypes.func,
};

VideoUpload.defaultProps = {
  onAnalysisComplete: null,
};
