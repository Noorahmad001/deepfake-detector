import { useState, useEffect } from 'react'
import { getHistory } from '../services/api'
import { Link } from 'react-router-dom'

function HistoryPage() {
  const [detections, setDetections] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchHistory()
  }, [])

  const fetchHistory = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await getHistory()
      console.log('History data:', data)
      setDetections(data.detections || [])
    } catch (err) {
      console.error('History error:', err)
      setError('Could not load history')
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateStr) => {
    if (!dateStr) return 'Unknown'
    try {
      return new Date(dateStr).toLocaleString()
    } catch (e) {
      return dateStr
    }
  }

  const formatConfidence = (confidence) => {
    if (!confidence) return '0%'
    const num = parseFloat(confidence) * 100
    return num.toFixed(1) + '%'
  }

  const getConfidenceWidth = (confidence) => {
    if (!confidence) return '0%'
    const num = parseFloat(confidence) * 100
    return num.toFixed(0) + '%'
  }

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#030712', padding: '48px 16px' }}>
      <div style={{ maxWidth: '900px', margin: '0 auto' }}>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
          <div>
            <h1 style={{ fontSize: '32px', fontWeight: '700', color: '#ffffff', marginBottom: '8px', letterSpacing: '-1px' }}>
              Detection History
            </h1>
            <p style={{ color: '#6b7280', fontSize: '15px' }}>
              Your recent deepfake detection results
            </p>
          </div>
          <button
            onClick={fetchHistory}
            style={{ background: 'rgba(59,130,246,0.1)', border: '1px solid rgba(59,130,246,0.3)', color: '#60a5fa', padding: '10px 20px', borderRadius: '10px', fontSize: '14px', fontWeight: '500', cursor: 'pointer' }}
          >
            Refresh
          </button>
        </div>

        {loading && (
          <div style={{ textAlign: 'center', padding: '60px', color: '#6b7280' }}>
            <div style={{ fontSize: '32px', marginBottom: '12px' }}>⏳</div>
            <p>Loading history...</p>
          </div>
        )}

        {error && !loading && (
          <div style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: '12px', padding: '20px', textAlign: 'center', color: '#f87171', marginBottom: '24px' }}>
            {error}
          </div>
        )}

        {!loading && !error && detections.length === 0 && (
          <div style={{ textAlign: 'center', padding: '80px 20px', background: '#0f172a', border: '1px solid #1f2937', borderRadius: '20px' }}>
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>📭</div>
            <h3 style={{ color: '#ffffff', fontSize: '20px', fontWeight: '600', marginBottom: '8px' }}>
              No detections yet
            </h3>
            <p style={{ color: '#6b7280', fontSize: '15px' }}>
              Upload an image or video to start detecting deepfakes
            </p>
            <Link
              to="/upload"
              style={{ display: 'inline-block', marginTop: '24px', background: 'linear-gradient(135deg, #2563eb, #1d4ed8)', color: 'white', padding: '12px 28px', borderRadius: '10px', fontWeight: '600', fontSize: '14px', textDecoration: 'none' }}
            >
              Start Detection
            </Link>
          </div>
        )}

        {!loading && detections.length > 0 && (
          <div>
            <p style={{ color: '#4b5563', fontSize: '13px', marginBottom: '16px' }}>
              {detections.length === 1 ? '1 detection' : detections.length + ' detections'}
            </p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {detections.map(function(detection, index) {
                const isFake = detection.prediction === 'FAKE'
                const isVideo = detection.file_type === 'video'
                return (
                  <div
                    key={detection.detection_id || index}
                    style={{ background: '#0f172a', border: '1px solid #1f2937', borderRadius: '16px', padding: '20px', display: 'flex', alignItems: 'center', gap: '16px' }}
                  >
                    <div style={{ width: '48px', height: '48px', borderRadius: '12px', background: isVideo ? 'rgba(139,92,246,0.1)' : 'rgba(59,130,246,0.1)', border: isVideo ? '1px solid rgba(139,92,246,0.2)' : '1px solid rgba(59,130,246,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '20px', flexShrink: 0 }}>
                      {isVideo ? '🎥' : '🖼️'}
                    </div>

                    <div style={{ flex: 1, minWidth: 0 }}>
                      <p style={{ color: '#ffffff', fontWeight: '500', fontSize: '15px', marginBottom: '4px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {detection.file_name || 'Unknown file'}
                      </p>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
                        <span style={{ color: '#4b5563', fontSize: '12px' }}>
                          {formatDate(detection.created_at)}
                        </span>
                        {isVideo && detection.frames_analyzed && (
                          <span style={{ color: '#4b5563', fontSize: '12px' }}>
                            {detection.frames_analyzed} frames
                          </span>
                        )}
                      </div>
                      <div style={{ marginTop: '8px' }}>
                        <div style={{ background: '#1f2937', borderRadius: '100px', height: '4px', width: '200px', maxWidth: '100%' }}>
                          <div style={{ background: isFake ? 'linear-gradient(90deg, #ef4444, #dc2626)' : 'linear-gradient(90deg, #22c55e, #16a34a)', height: '4px', borderRadius: '100px', width: getConfidenceWidth(detection.confidence), transition: 'width 0.3s' }} />
                        </div>
                      </div>
                    </div>

                    <div style={{ flexShrink: 0, textAlign: 'right' }}>
                      <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', padding: '6px 14px', borderRadius: '100px', fontSize: '13px', fontWeight: '700', background: isFake ? 'rgba(239,68,68,0.1)' : 'rgba(34,197,94,0.1)', border: isFake ? '1px solid rgba(239,68,68,0.3)' : '1px solid rgba(34,197,94,0.3)', color: isFake ? '#f87171' : '#4ade80' }}>
                        {isFake ? '⚠️' : '✅'} {detection.prediction || 'UNKNOWN'}
                      </div>
                      <p style={{ color: '#4b5563', fontSize: '12px', marginTop: '6px' }}>
                        {formatConfidence(detection.confidence)} confidence
                      </p>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        )}

      </div>
    </div>
  )
}

export default HistoryPage