import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Navbar from './components/navbar.jsx'
import Footer from './components/footer.jsx'
import HomePage from './pages/homepage.jsx'
import UploadPage from './pages/uploadpage.jsx'
import ResultPage from './pages/resultpage.jsx'
import HistoryPage from './pages/historypage.jsx'

function App() {
  return (
    <BrowserRouter>
      <div style={{ backgroundColor: '#030712', minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
        <Navbar />
        <div style={{ flex: 1 }}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/result" element={<ResultPage />} />
            <Route path="/history" element={<HistoryPage />} />
          </Routes>
        </div>
        <Footer />
      </div>
    </BrowserRouter>
  )
}

export default App
