import { useState, useRef, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { FolderUp, AlertTriangle, Image as ImageIcon, Video, Search } from 'lucide-react'
import LoadingSpinner from '../components/LoadingSpinner'
import { detectImage, detectVideo } from '../services/api'

function UploadPage() {
  const navigate = useNavigate()
  const fileInputRef = useRef(null)
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [fileType, setFileType] = useState(null)
  const [isDragging, setIsDragging] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [error, setError] = useState(null)

  const handleFile = (selectedFile) => {
    setError(null)
    if (!selectedFile) return
    const isImage = selectedFile.type.startsWith('image/')
    const isVideo = selectedFile.type.startsWith('video/')
    if (!isImage && !isVideo) {
      setError('Please upload an image or video file.')
      return
    }
    const maxSize = isImage ? 10 : 100
    if (selectedFile.size > maxSize * 1024 * 1024) {
      setError(`File too large. Max ${maxSize}MB.`)
      return
    }
    setFile(selectedFile)
    setFileType(isImage ? 'image' : 'video')
    setPreview(URL.createObjectURL(selectedFile))
  }

  const handleDragOver = useCallback((e) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    setIsDragging(false)
    handleFile(e.dataTransfer.files[0])
  }, [])

  const handleDetect = async () => {
    if (!file) return
    setIsLoading(true)
    setError(null)
    setUploadProgress(0)
    try {
      const result = fileType === 'image'
        ? await detectImage(file, setUploadProgress)
        : await detectVideo(file, setUploadProgress)
      navigate('/result', { state: { result, fileType, preview } })
    } catch (err) {
      setError(
        err.code === 'ERR_NETWORK'
          ? 'Cannot connect to backend. Make sure it is running.'
          : err.response?.data?.detail || 'Detection failed. Please try again.'
      )
      setIsLoading(false)
    }
  }

  const handleReset = () => {
    setFile(null)
    setPreview(null)
    setFileType(null)
    setError(null)
    setUploadProgress(0)
    setIsLoading(false)
  }

  return (
    <div style={{
      minHeight: '100vh',
      padding: '48px 16px',
      backgroundColor: '#030712'
    }}>
      <div style={{ maxWidth: '600px', margin: '0 auto' }}>

        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <h1 style={{
            fontSize: '32px',
            fontWeight: '700',
            color: '#ffffff',
            marginBottom: '8px',
            letterSpacing: '-1px'
          }}>
            Detect Deepfake
          </h1>
          <p style={{ color: '#6b7280', fontSize: '15px' }}>
            Upload an image or video to analyze with AI
          </p>
        </div>

        {/* Upload Area */}
        {!file && !isLoading && (
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            style={{
              border: `2px dashed ${isDragging ? '#3b82f6' : '#1f2937'}`,
              borderRadius: '16px',
              padding: '40px 24px',
              textAlign: 'center',
              cursor: 'pointer',
              background: isDragging
                ? 'rgba(59,130,246,0.05)'
                : '#0f172a',
              transition: 'all 0.2s'
            }}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*,video/*"
              style={{ display: 'none' }}
              onChange={(e) => handleFile(e.target.files[0])}
            />

            <div style={{
              width: '56px',
              height: '56px',
              background: 'rgba(59,130,246,0.1)',
              border: '1px solid rgba(59,130,246,0.2)',
              borderRadius: '14px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 16px',
            }}>
              <FolderUp className="w-8 h-8 text-blue-400" />
            </div>

            <p style={{
              color: '#ffffff',
              fontWeight: '600',
              fontSize: '16px',
              marginBottom: '6px'
            }}>
              {isDragging ? 'Drop your file here' : 'Drop file or click to browse'}
            </p>
            <p style={{ color: '#4b5563', fontSize: '13px', marginBottom: '16px' }}>
              Images up to 10MB • Videos up to 100MB
            </p>

            <div style={{ display: 'flex', justifyContent: 'center', gap: '8px', flexWrap: 'wrap' }}>
              {['JPG', 'PNG', 'MP4', 'AVI', 'MOV'].map((fmt) => (
                <span key={fmt} style={{
                  background: '#1f2937',
                  color: '#9ca3af',
                  fontSize: '11px',
                  padding: '3px 10px',
                  borderRadius: '6px',
                  fontWeight: '500'
                }}>
                  {fmt}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div style={{
            marginTop: '12px',
            background: 'rgba(239,68,68,0.1)',
            border: '1px solid rgba(239,68,68,0.3)',
            color: '#f87171',
            padding: '12px 16px',
            borderRadius: '10px',
            fontSize: '14px',
            display: 'flex',
            alignItems: 'center'
          }}>
            <AlertTriangle className="w-5 h-5 mr-2" /> {error}
          </div>
        )}

        {/* Preview */}
        {file && !isLoading && (
          <div style={{
            background: '#0f172a',
            border: '1px solid #1f2937',
            borderRadius: '16px',
            padding: '20px'
          }}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '16px'
            }}>
              <div>
                <p style={{
                  color: '#ffffff',
                  fontWeight: '500',
                  fontSize: '15px'
                }}>
                  {file.name}
                </p>
                <p style={{ color: '#4b5563', fontSize: '13px' }}>
                  {(file.size / (1024 * 1024)).toFixed(2)} MB •{' '}
                  <span style={{ color: '#3b82f6', textTransform: 'capitalize' }}>
                    {fileType}
                  </span>
                </p>
              </div>
              <button
                onClick={handleReset}
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#4b5563',
                  cursor: 'pointer',
                  fontSize: '13px'
                }}
              >
                ✕ Remove
              </button>
            </div>

            {fileType === 'image' && preview && (
              <div style={{
                borderRadius: '10px',
                overflow: 'hidden',
                background: '#1f2937',
                marginBottom: '16px',
                maxHeight: '200px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <img
                  src={preview}
                  alt="Preview"
                  style={{ maxHeight: '200px', maxWidth: '100%', objectFit: 'contain' }}
                />
              </div>
            )}

            {fileType === 'video' && preview && (
              <div style={{
                borderRadius: '10px',
                overflow: 'hidden',
                marginBottom: '16px'
              }}>
                <video
                  src={preview}
                  controls
                  style={{ width: '100%', maxHeight: '200px' }}
                />
              </div>
            )}

            <button
              onClick={handleDetect}
              style={{
                width: '100%',
                background: 'linear-gradient(135deg, #2563eb, #1d4ed8)',
                color: 'white',
                border: 'none',
                padding: '14px',
                borderRadius: '10px',
                fontSize: '15px',
                fontWeight: '600',
                cursor: 'pointer',
                boxShadow: '0 0 20px rgba(37,99,235,0.3)',
                transition: 'all 0.2s',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px'
              }}
            >
              <Search className="w-5 h-5" /> Analyze for Deepfake
            </button>
          </div>
        )}

        {/* Loading */}
        {isLoading && (
          <div style={{
            background: '#0f172a',
            border: '1px solid #1f2937',
            borderRadius: '16px',
            padding: '32px'
          }}>
            {uploadProgress > 0 && uploadProgress < 100 && (
              <div style={{ marginBottom: '24px' }}>
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  fontSize: '13px',
                  color: '#6b7280',
                  marginBottom: '8px'
                }}>
                  <span>Uploading...</span>
                  <span>{uploadProgress}%</span>
                </div>
                <div style={{
                  background: '#1f2937',
                  borderRadius: '100px',
                  height: '6px'
                }}>
                  <div style={{
                    background: 'linear-gradient(90deg, #2563eb, #7c3aed)',
                    height: '6px',
                    borderRadius: '100px',
                    width: `${uploadProgress}%`,
                    transition: 'width 0.3s'
                  }}></div>
                </div>
              </div>
            )}
            <LoadingSpinner
              message={
                uploadProgress < 100
                  ? 'Uploading file...'
                  : fileType === 'video'
                  ? 'Extracting frames and analyzing...'
                  : 'Analyzing with AI model...'
              }
            />
          </div>
        )}

        {/* Info Cards */}
        {!file && !isLoading && (
          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '12px',
            marginTop: '16px'
          }}>
            {[
              { icon: <ImageIcon className="w-6 h-6 text-blue-400" />, title: 'Images', desc: 'JPG, PNG, WEBP up to 10MB' },
              { icon: <Video className="w-6 h-6 text-blue-400" />, title: 'Videos', desc: 'MP4, AVI, MOV up to 100MB' },
            ].map((card) => (
              <div key={card.title} style={{
                background: '#0f172a',
                border: '1px solid #1f2937',
                borderRadius: '12px',
                padding: '16px'
              }}>
                <div style={{ fontSize: '20px', marginBottom: '6px' }}>{card.icon}</div>
                <p style={{
                  color: '#ffffff',
                  fontSize: '14px',
                  fontWeight: '500',
                  marginBottom: '4px'
                }}>
                  {card.title}
                </p>
                <p style={{ color: '#4b5563', fontSize: '12px' }}>{card.desc}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default UploadPage