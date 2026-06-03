import { Link, useLocation } from 'react-router-dom'
import { useState } from 'react'

function Navbar() {
  const location = useLocation()
  const [menuOpen, setMenuOpen] = useState(false)

  const links = [
    { name: 'Home', path: '/' },
    { name: 'Detect', path: '/upload' },
    { name: 'History', path: '/history' },
  ]

  return (
    <nav style={{
      background: 'rgba(3,7,18,0.95)',
      backdropFilter: 'blur(20px)',
      borderBottom: '1px solid rgba(255,255,255,0.06)',
      position: 'sticky',
      top: 0,
      zIndex: 50
    }}>
      <div style={{
        maxWidth: '1100px',
        margin: '0 auto',
        padding: '0 16px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        height: '64px'
      }}>

        {/* Logo */}
        <Link to="/" style={{
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          textDecoration: 'none'
        }}>
          <div style={{
            width: '36px',
            height: '36px',
            background: 'linear-gradient(135deg, #2563eb, #7c3aed)',
            borderRadius: '10px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '16px',
            fontWeight: '800',
            color: 'white',
            boxShadow: '0 0 20px rgba(37,99,235,0.4)'
          }}>
            DD
          </div>
          <span style={{
            fontSize: '18px',
            fontWeight: '700',
            color: '#ffffff',
            letterSpacing: '-0.5px'
          }}>
            Deepfake<span style={{ color: '#3b82f6' }}>Detector</span>
          </span>
        </Link>

        {/* Desktop Links */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          {links.map((link) => (
            <Link
              key={link.name}
              to={link.path}
              style={{
                padding: '8px 16px',
                borderRadius: '8px',
                fontSize: '14px',
                fontWeight: '500',
                textDecoration: 'none',
                color: location.pathname === link.path ? '#3b82f6' : '#9ca3af',
                background: location.pathname === link.path
                  ? 'rgba(59,130,246,0.1)'
                  : 'transparent',
                transition: 'all 0.2s'
              }}
            >
              {link.name}
            </Link>
          ))}
          <Link
            to="/upload"
            style={{
              marginLeft: '8px',
              padding: '8px 20px',
              background: 'linear-gradient(135deg, #2563eb, #1d4ed8)',
              color: 'white',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: '600',
              textDecoration: 'none',
              boxShadow: '0 0 20px rgba(37,99,235,0.3)',
              transition: 'all 0.2s'
            }}
          >
            Try Now →
          </Link>
        </div>
      </div>
    </nav>
  )
}

export default Navbar