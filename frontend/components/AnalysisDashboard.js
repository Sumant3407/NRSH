import { useState, useEffect } from 'react';
import axios from 'axios';
import PropTypes from 'prop-types';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const AXIOS_TIMEOUT = parseInt(
  process.env.NEXT_PUBLIC_AXIOS_TIMEOUT_MS || '15000',
  10,
);

export default // Function: AnalysisDashboard
// Function: AnalysisDashboard
function AnalysisDashboard({ analysisId }) {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(false);
  const [downloadError, setDownloadError] = useState(null);

  useEffect(() => {
    if (analysisId) {
      setLoading(true);
      setResults(null);
      fetchResults();
    }
  }, [analysisId]);

  const fetchResults = async () => {
    try {
      const response = await axios.get(
        `${API_URL}/api/v1/analysis/results/${analysisId}`,
        { timeout: AXIOS_TIMEOUT },
      );
      setResults(response.data);
    } catch (error) {
      console.error('Error fetching results:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-8 text-center">
        <p>Loading analysis results...</p>
      </div>
    );
  }

  if (!results) {
    return (
      <div className="bg-white rounded-lg shadow p-8 text-center text-red-500">
        <p>Error loading results</p>
      </div>
    );
  }

  const summary = results.summary || {};
  const aggregated = summary.aggregated_results || {};

  const chartData = Object.entries(aggregated).map(([element, data]) => ({
    name: element.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase()),
    minor: data.by_severity?.minor || 0,
    moderate: data.by_severity?.moderate || 0,
    severe: data.by_severity?.severe || 0,
  }));

  const downloadReport = async () => {
    setDownloading(true);
    setDownloadError(null);

    try {
      const response = await axios.post(
        `${API_URL}/api/v1/reports/generate`,
        {
          analysis_id: analysisId,
          report_type: 'pdf',
          include_confidence_scores: true,
          include_heatmaps: false,
        },
        {
          responseType: 'blob',
          timeout: AXIOS_TIMEOUT,
          onDownloadProgress: (progressEvent) => {
            console.log('Download progress:', progressEvent);
          },
        },
      );

      if (
        response.data.type !== 'application/pdf' &&
        !response.data.type?.includes('pdf')
      ) {
        const text = await response.data.text();
        try {
          const errorData = JSON.parse(text);
          throw new Error(errorData.detail || 'Server returned an error');
        } catch (parseError) {
          throw new Error(text || 'Invalid response format');
        }
      }

      const contentDisposition = response.headers['content-disposition'];
      let filename = `NRSH_Report_${analysisId}_${new Date().toISOString().slice(0, 19).replace(/:/g, '')}.pdf`;

      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(
          /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/,
        );
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1].replace(/['"]/g, '');
        }
      }

      const url = window.URL.createObjectURL(
        new Blob([response.data], { type: 'application/pdf' }),
      );
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      alert('PDF report downloaded successfully!');
    } catch (error) {
      console.error('Error downloading report:', error);

      let errorMessage = 'Failed to download PDF report. Please try again.';

      if (error.response) {
        if (error.response.status === 404) {
          errorMessage =
            'Analysis not found. Please ensure the analysis has completed successfully.';
        } else if (error.response.status === 500) {
          errorMessage =
            'Server error occurred while generating the report. Please try again later.';
        } else if (error.response.data) {
          try {
            const reader = new FileReader();
            reader.onload = () => {
              try {
                const errorData = JSON.parse(reader.result);
                errorMessage = errorData.detail || errorMessage;
              } catch {
                errorMessage = reader.result || errorMessage;
              }
              setDownloadError(errorMessage);
            };
            reader.readAsText(error.response.data);
            return;
          } catch {
            errorMessage = `Server error (${error.response.status}): ${error.response.statusText}`;
          }
        }
      } else if (error.code === 'ECONNABORTED') {
        errorMessage =
          'Request timed out. The report might be large, please try again.';
      } else if (error.message) {
        errorMessage = error.message;
      }

      setDownloadError(errorMessage);
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Analysis Results</h2>
        <div className="flex flex-col items-end">
          <button
            onClick={downloadReport}
            disabled={downloading}
            className={`px-4 py-2 rounded-lg transition-colors flex items-center ${
              downloading
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-green-600 hover:bg-green-700 text-white'
            }`}
          >
            {downloading ? (
              <>
                <svg
                  className="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
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
                Generating PDF...
              </>
            ) : (
              <>
                <svg
                  className="w-4 h-4 mr-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
                Download PDF Report
              </>
            )}
          </button>
          {downloadError && (
            <div className="mt-2 text-sm text-red-600 max-w-xs text-right">
              {downloadError}
            </div>
          )}
        </div>
      </div>

      {}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-blue-50 p-4 rounded-lg">
          <div className="text-sm text-gray-600">Total Issues</div>
          <div className="text-3xl font-bold text-blue-600">
            {summary.total_issues || 0}
          </div>
        </div>
        <div className="bg-red-50 p-4 rounded-lg">
          <div className="text-sm text-gray-600">Severe Issues</div>
          <div className="text-3xl font-bold text-red-600">
            {summary.severe_issues || 0}
          </div>
        </div>
        <div className="bg-green-50 p-4 rounded-lg">
          <div className="text-sm text-gray-600">Element Types</div>
          <div className="text-3xl font-bold text-green-600">
            {summary.element_types || 0}
          </div>
        </div>
      </div>

      {}
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
  );
}

AnalysisDashboard.propTypes = {
  analysisId: PropTypes.string,
};

AnalysisDashboard.defaultProps = {
  analysisId: null,
};
