import { Link } from 'react-router-dom'
import { UploadCloud, Cpu, BarChart3, Image as ImageIcon, Video, Zap, Lock, Folder } from 'lucide-react'

function HomePage() {
  return (
    <div style={{ backgroundColor: '#030712' }}>

      {/* Hero Section */}
      <section style={{
        background: 'linear-gradient(135deg, #0f172a 0%, #030712 50%, #0f172a 100%)',
        padding: '80px 16px',
        textAlign: 'center',
        position: 'relative',
        overflow: 'hidden'
      }}>
        {/* Glow effect */}
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          width: '600px',
          height: '600px',
          background: 'radial-gradient(circle, rgba(59,130,246,0.15) 0%, transparent 70%)',
          pointerEvents: 'none'
        }}></div>

        <div style={{ maxWidth: '800px', margin: '0 auto', position: 'relative' }}>

          {/* Badge */}
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            background: 'rgba(59,130,246,0.1)',
            border: '1px solid rgba(59,130,246,0.3)',
            color: '#60a5fa',
            padding: '6px 16px',
            borderRadius: '100px',
            fontSize: '13px',
            fontWeight: '500',
            marginBottom: '32px'
          }}>
            <span style={{
              width: '6px',
              height: '6px',
              background: '#3b82f6',
              borderRadius: '50%',
              display: 'inline-block',
              animation: 'pulse 2s infinite'
            }}></span>
            AI Powered Deepfake Detection
          </div>

          {/* Main Heading */}
          <h1 style={{
            fontSize: 'clamp(40px, 7vw, 80px)',
            fontWeight: '800',
            color: '#ffffff',
            lineHeight: '1.1',
            marginBottom: '24px',
            letterSpacing: '-2px'
          }}>
            Detect Deepfakes{' '}
            <span style={{
              background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}>
              Instantly
            </span>
          </h1>

          {/* Subtitle */}
          <p style={{
            fontSize: '18px',
            color: '#9ca3af',
            maxWidth: '560px',
            margin: '0 auto 40px',
            lineHeight: '1.7'
          }}>
            Upload any image or video. Our advanced EfficientNet AI model
            analyzes it and tells you if it is real or a deepfake — in seconds.
          </p>

          {/* CTA Buttons */}
          <div style={{
            display: 'flex',
            gap: '12px',
            justifyContent: 'center',
            flexWrap: 'wrap'
          }}>
            <Link to="/upload" style={{
              background: 'linear-gradient(135deg, #2563eb, #1d4ed8)',
              color: 'white',
              padding: '14px 32px',
              borderRadius: '12px',
              fontWeight: '600',
              fontSize: '16px',
              textDecoration: 'none',
              boxShadow: '0 0 30px rgba(37,99,235,0.4)',
              transition: 'all 0.2s'
            }}>
              Start Detection →
            </Link>
            <a href="#features" style={{
              background: 'rgba(255,255,255,0.05)',
              border: '1px solid rgba(255,255,255,0.1)',
              color: '#e5e7eb',
              padding: '14px 32px',
              borderRadius: '12px',
              fontWeight: '600',
              fontSize: '16px',
              textDecoration: 'none',
              transition: 'all 0.2s'
            }}>
              Learn More
            </a>
          </div>

          {/* Stats */}
          <div style={{
            display: 'flex',
            justifyContent: 'center',
            gap: '48px',
            marginTop: '64px',
            flexWrap: 'wrap'
          }}>
            {[
              { value: '99%', label: 'Accuracy' },
              { value: '< 2s', label: 'Per Image' },
              { value: 'Free', label: 'Forever' },
            ].map((stat) => (
              <div key={stat.label} style={{ textAlign: 'center' }}>
                <div style={{
                  fontSize: '32px',
                  fontWeight: '800',
                  color: '#ffffff',
                  letterSpacing: '-1px'
                }}>
                  {stat.value}
                </div>
                <div style={{ fontSize: '14px', color: '#6b7280', marginTop: '4px' }}>
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section style={{ padding: '80px 16px', maxWidth: '1100px', margin: '0 auto' }}>
        <div style={{ textAlign: 'center', marginBottom: '48px' }}>
          <h2 style={{
            fontSize: '36px',
            fontWeight: '700',
            color: '#ffffff',
            marginBottom: '12px'
          }}>
            How It Works
          </h2>
          <p style={{ color: '#6b7280', fontSize: '16px' }}>
            Three simple steps to detect deepfakes
          </p>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: '24px'
        }}>
          {[
            { step: '01', icon: <UploadCloud className="w-8 h-8 text-blue-400" />, title: 'Upload File', desc: 'Drag and drop or click to upload any image or video file from your device.' },
            { step: '02', icon: <Cpu className="w-8 h-8 text-blue-400" />, title: 'AI Analysis', desc: 'Our EfficientNet model scans the file for deepfake artifacts and manipulation signs.' },
            { step: '03', icon: <BarChart3 className="w-8 h-8 text-blue-400" />, title: 'Get Result', desc: 'Receive a clear REAL or FAKE verdict with a confidence percentage score.' },
          ].map((item) => (
            <div key={item.step} style={{
              background: 'linear-gradient(135deg, #111827, #0f172a)',
              border: '1px solid #1f2937',
              borderRadius: '20px',
              padding: '32px',
              transition: 'border-color 0.2s'
            }}>
              <div style={{
                fontSize: '48px',
                fontWeight: '900',
                color: 'rgba(59,130,246,0.15)',
                marginBottom: '16px',
                lineHeight: '1'
              }}>
                {item.step}
              </div>
              <div style={{ fontSize: '28px', marginBottom: '12px' }}>{item.icon}</div>
              <h3 style={{
                fontSize: '18px',
                fontWeight: '600',
                color: '#ffffff',
                marginBottom: '8px'
              }}>
                {item.title}
              </h3>
              <p style={{ color: '#6b7280', fontSize: '14px', lineHeight: '1.6' }}>
                {item.desc}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section id="features" style={{
        padding: '80px 16px',
        maxWidth: '1100px',
        margin: '0 auto'
      }}>
        <div style={{ textAlign: 'center', marginBottom: '48px' }}>
          <h2 style={{
            fontSize: '36px',
            fontWeight: '700',
            color: '#ffffff',
            marginBottom: '12px'
          }}>
            Features
          </h2>
          <p style={{ color: '#6b7280', fontSize: '16px' }}>
            Everything you need to detect deepfakes
          </p>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: '20px'
        }}>
          {[
            { icon: <ImageIcon className="w-8 h-8 text-blue-400" />, title: 'Image Detection', desc: 'Analyzes facial features and pixel patterns to detect manipulation with high accuracy.' },
            { icon: <Video className="w-8 h-8 text-blue-400" />, title: 'Video Detection', desc: 'Extracts multiple frames and analyzes each one for deepfake artifacts automatically.' },
            { icon: <Zap className="w-8 h-8 text-blue-400" />, title: 'Fast Results', desc: 'Get detection results in under 2 seconds for images and under a minute for videos.' },
            { icon: <BarChart3 className="w-8 h-8 text-blue-400" />, title: 'Confidence Score', desc: 'See exactly how confident our AI is with a detailed percentage confidence score.' },
            { icon: <Lock className="w-8 h-8 text-blue-400" />, title: 'Secure Processing', desc: 'Files are processed securely and permanently deleted immediately after analysis.' },
            { icon: <Folder className="w-8 h-8 text-blue-400" />, title: 'Detection History', desc: 'View all your previous detection results saved securely in one convenient place.' },
          ].map((f) => (
            <div key={f.title} style={{
              background: '#0f172a',
              border: '1px solid #1f2937',
              borderRadius: '16px',
              padding: '24px',
              transition: 'border-color 0.2s, transform 0.2s',
              cursor: 'default'
            }}>
              <div style={{ fontSize: '32px', marginBottom: '12px' }}>{f.icon}</div>
              <h3 style={{
                fontSize: '16px',
                fontWeight: '600',
                color: '#f9fafb',
                marginBottom: '8px'
              }}>
                {f.title}
              </h3>
              <p style={{ color: '#6b7280', fontSize: '14px', lineHeight: '1.6' }}>
                {f.desc}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA Banner */}
      <section style={{ padding: '80px 16px', maxWidth: '1100px', margin: '0 auto' }}>
        <div style={{
          background: 'linear-gradient(135deg, #1e3a8a, #1d4ed8)',
          borderRadius: '24px',
          padding: '64px 32px',
          textAlign: 'center',
          border: '1px solid rgba(59,130,246,0.3)',
          boxShadow: '0 0 60px rgba(37,99,235,0.2)'
        }}>
          <h2 style={{
            fontSize: '36px',
            fontWeight: '700',
            color: '#ffffff',
            marginBottom: '16px'
          }}>
            Ready to detect deepfakes?
          </h2>
          <p style={{
            color: '#bfdbfe',
            fontSize: '16px',
            marginBottom: '32px'
          }}>
            Upload your first image or video for free right now.
          </p>
          <Link to="/upload" style={{
            background: '#ffffff',
            color: '#1e3a8a',
            padding: '14px 36px',
            borderRadius: '12px',
            fontWeight: '700',
            fontSize: '16px',
            textDecoration: 'none',
            display: 'inline-block',
            transition: 'all 0.2s'
          }}>
            Try It Free →
          </Link>
        </div>
      </section>

    </div>
  )
}

export default HomePage