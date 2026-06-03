import { Link } from 'react-router-dom'

function Footer() {
  return (
    <footer style={{
      background: '#030712',
      borderTop: '1px solid rgba(255,255,255,0.06)',
      padding: '48px 16px 32px'
    }}>
      <div style={{ maxWidth: '1100px', margin: '0 auto' }}>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '32px',
          marginBottom: '40px'
        }}>

          <div>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              marginBottom: '12px'
            }}>
              <div style={{
                width: '32px',
                height: '32px',
                background: 'linear-gradient(135deg, #2563eb, #7c3aed)',
                borderRadius: '8px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '12px',
                fontWeight: '800',
                color: 'white'
              }}>DD</div>
              <span style={{
                fontSize: '16px',
                fontWeight: '700',
                color: '#ffffff'
              }}>
                Deepfake<span style={{ color: '#3b82f6' }}>Detector</span>
              </span>
            </div>
            <p style={{
              color: '#6b7280',
              fontSize: '14px',
              lineHeight: '1.6'
            }}>
              AI-powered deepfake detection built with EfficientNet and PyTorch.
            </p>
          </div>

          <div>
            <h3 style={{
              color: '#ffffff',
              fontWeight: '600',
              fontSize: '14px',
              marginBottom: '16px'
            }}>
              Quick Links
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {[
                { name: 'Home', path: '/' },
                { name: 'Detect', path: '/upload' },
                { name: 'History', path: '/history' },
              ].map((link) => (
                <Link
                  key={link.name}
                  to={link.path}
                  style={{
                    color: '#6b7280',
                    textDecoration: 'none',
                    fontSize: '14px',
                    transition: 'color 0.2s'
                  }}
                >
                  {link.name}
                </Link>
              ))}
            </div>
          </div>

          <div>
            <h3 style={{
              color: '#ffffff',
              fontWeight: '600',
              fontSize: '14px',
              marginBottom: '16px'
            }}>
              Tech Stack
            </h3>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              {['React', 'FastAPI', 'PyTorch', 'MongoDB', 'EfficientNet'].map((tech) => (
                <span key={tech} style={{
                  background: '#111827',
                  border: '1px solid #1f2937',
                  color: '#9ca3af',
                  fontSize: '12px',
                  padding: '4px 10px',
                  borderRadius: '6px'
                }}>
                  {tech}
                </span>
              ))}
            </div>
          </div>
        </div>

        <div style={{
          borderTop: '1px solid rgba(255,255,255,0.06)',
          paddingTop: '24px',
          textAlign: 'center',
          color: '#4b5563',
          fontSize: '13px'
        }}>
          © 2025 DeepfakeDetector. Built with AI for a safer internet.
        </div>
      </div>
    </footer>
  )
}

export default Footer