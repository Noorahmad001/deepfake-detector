import { useLocation, useNavigate } from 'react-router-dom'
import { AlertTriangle, CheckCircle } from 'lucide-react'

function ResultPage() {
  const location = useLocation()
  const navigate = useNavigate()
  const { result, fileType, preview } = location.state || {}

  if (!result) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-400 text-lg mb-4">No result found.</p>
          <button
            onClick={() => navigate('/upload')}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-xl"
          >
            Go to Upload
          </button>
        </div>
      </div>
    )
  }

  const isFake = result.prediction === 'FAKE'
  const confidencePercent = ((result.confidence || 0) * 100).toFixed(1)

  return (
    <div className="min-h-screen py-12 px-4">
      <div className="max-w-3xl mx-auto">

        <div className="text-center mb-10">
          <h1 className="text-4xl font-bold text-white mb-3">
            Detection Result
          </h1>
          <p className="text-gray-400">Analysis complete</p>
        </div>

        <div className={`
          border-2 rounded-2xl p-8 mb-6 text-center
          ${isFake
            ? 'bg-red-950 border-red-700'
            : 'bg-green-950 border-green-700'
          }
        `}>
          <div className="mb-4">
            {isFake ? <AlertTriangle className="w-16 h-16 mx-auto text-red-500" /> : <CheckCircle className="w-16 h-16 mx-auto text-green-500" />}
          </div>

          <div className={`
            text-5xl font-bold mb-4
            ${isFake ? 'text-red-400' : 'text-green-400'}
          `}>
            {result.prediction}
          </div>

          <p className="text-gray-300 text-lg mb-6">
            Confidence:{' '}
            <span className="font-bold text-white">
              {confidencePercent}%
            </span>
          </p>

          <div className="max-w-sm mx-auto">
            <div className="w-full bg-gray-800 rounded-full h-3">
              <div
                className={`h-3 rounded-full transition-all duration-1000 ${
                  isFake ? 'bg-red-500' : 'bg-green-500'
                }`}
                style={{ width: `${confidencePercent}%` }}
              ></div>
            </div>
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>0%</span>
              <span>50%</span>
              <span>100%</span>
            </div>
          </div>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 mb-6">
          <h2 className="text-white font-semibold text-lg mb-4">
            Analysis Details
          </h2>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-gray-800 rounded-xl p-4">
              <p className="text-gray-400 text-xs mb-1">File Name</p>
              <p className="text-white font-medium text-sm truncate">
                {result.file_name}
              </p>
            </div>
            <div className="bg-gray-800 rounded-xl p-4">
              <p className="text-gray-400 text-xs mb-1">File Type</p>
              <p className="text-white font-medium capitalize">
                {result.file_type}
              </p>
            </div>
            <div className="bg-gray-800 rounded-xl p-4">
              <p className="text-gray-400 text-xs mb-1">Verdict</p>
              <p className={`font-medium ${
                isFake ? 'text-red-400' : 'text-green-400'
              }`}>
                {result.prediction}
              </p>
            </div>
            <div className="bg-gray-800 rounded-xl p-4">
              <p className="text-gray-400 text-xs mb-1">Confidence</p>
              <p className="text-white font-medium">{confidencePercent}%</p>
            </div>
            {result.frames_analyzed && (
              <div className="bg-gray-800 rounded-xl p-4 col-span-2">
                <p className="text-gray-400 text-xs mb-1">Frames Analyzed</p>
                <p className="text-white font-medium">
                  {result.frames_analyzed} frames
                </p>
              </div>
            )}
          </div>

          <div className="mt-4 bg-gray-800 rounded-xl p-4">
            <p className="text-gray-400 text-xs mb-2">What this means</p>
            <p className="text-gray-300 text-sm leading-relaxed">
              {isFake
                ? `Our AI detected signs of manipulation in this ${fileType}. The model found deepfake artifacts with ${confidencePercent}% confidence. This content may have been generated or altered using AI tools.`
                : `Our AI found no signs of manipulation in this ${fileType}. The model determined this content appears authentic with ${confidencePercent}% confidence.`
              }
            </p>
          </div>
        </div>

        {preview && (
          <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 mb-6">
            <h2 className="text-white font-semibold text-lg mb-4">
              File Preview
            </h2>
            {fileType === 'image' ? (
              <img
                src={preview}
                alt="Analyzed"
                className="w-full max-h-64 object-contain rounded-xl"
              />
            ) : (
              <video
                src={preview}
                controls
                className="w-full max-h-64 rounded-xl"
              />
            )}
          </div>
        )}

        <div className="flex flex-col sm:flex-row gap-4">
          <button
            onClick={() => navigate('/upload')}
            className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-4 rounded-xl transition-all"
          >
            Analyze Another File
          </button>
          <button
            onClick={() => navigate('/')}
            className="flex-1 bg-gray-800 hover:bg-gray-700 text-white font-semibold py-4 rounded-xl transition-all"
          >
            Back to Home
          </button>
        </div>
      </div>
    </div>
  )
}

export default ResultPage