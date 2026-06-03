# Deepfake Detector

A full-stack web application that uses deep learning to detect deepfake images and videos. Upload any image or video and receive a real-time verdict with a confidence score.

---

## Live Demo

| Service | URL |
|---|---|
| Frontend | https://your-app.vercel.app |
| Backend API | https://your-api.onrender.com |
| API Documentation | https://your-api.onrender.com/docs |

---

## Screenshots

### Homepage
![Homepage](screenshots/homepage.png)

### Upload Page
![Upload](screenshots/upload.png)

### Detection Result
![Result](screenshots/result.png)

### Detection History
![History](screenshots/history.png)

---

## Features

- Image deepfake detection supporting JPG, PNG and WEBP formats
- Video deepfake detection supporting MP4, AVI and MOV formats
- Confidence score displayed with every result
- Per-session detection history stored in MongoDB
- Responsive dark interface built with React
- REST API with full Swagger documentation

---

## Tech Stack

### Frontend
- React 18
- Vite
- TailwindCSS
- Axios
- React Router

### Backend
- Python
- FastAPI
- PyTorch
- OpenCV
- Motor (async MongoDB driver)

### AI Model
- Model: dima806/deepfake_vs_real_image_detection
- Source: Hugging Face
- Architecture: EfficientNet
- Accuracy: 90%+

### Database
- MongoDB Atlas

### Deployment
- Frontend: Vercel
- Backend: Render
- Database: MongoDB Atlas

---

## How It Works

```
1. User uploads an image or video through the web interface
2. The file is sent to the FastAPI backend
3. The AI model analyzes the content for deepfake artifacts
4. A REAL or FAKE verdict is returned with a confidence score
5. The result is saved to MongoDB under the user session
6. The user sees the result on screen instantly
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | / | Health check |
| POST | /api/detect-image | Detect deepfake in an image |
| POST | /api/detect-video | Detect deepfake in a video |
| GET | /api/history | Get detection history for session |
| GET | /docs | Swagger API documentation |

---

## Project Structure

```
deepfake-detector/
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── Navbar.jsx
│       │   ├── Footer.jsx
│       │   └── LoadingSpinner.jsx
│       ├── pages/
│       │   ├── HomePage.jsx
│       │   ├── UploadPage.jsx
│       │   ├── ResultPage.jsx
│       │   └── HistoryPage.jsx
│       └── services/
│           └── api.js
├── backend/
│   └── app/
│       ├── routes/
│       │   ├── detect.py
│       │   └── history.py
│       ├── services/
│       │   └── file_service.py
│       ├── database/
│       │   └── connection.py
│       ├── config/
│       │   └── settings.py
│       └── main.py
├── model/
│   ├── hf_detector.py
│   └── detector.py
├── screenshots/
├── .gitignore
└── README.md
```

---

## Running Locally

### Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- MongoDB Atlas account (free tier works)

### Clone the Repository

```bash
git clone https://github.com/YOURUSERNAME/deepfake-detector.git
cd deepfake-detector
```

### Backend Setup

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Mac or Linux
source venv/bin/activate

pip install -r requirements.txt
```

Create a `.env` file inside the `backend` folder:

```
MONGODB_URL=your_mongodb_connection_string
APP_ENV=development
MAX_IMAGE_SIZE_MB=10
MAX_VIDEO_SIZE_MB=100
```

Start the backend server:

```bash
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

---

## Environment Variables

| Variable | Description | Example |
|---|---|---|
| MONGODB_URL | MongoDB Atlas connection string | mongodb+srv://user:pass@cluster.mongodb.net/db |
| APP_ENV | Application environment | development or production |
| MAX_IMAGE_SIZE_MB | Maximum image upload size | 10 |
| MAX_VIDEO_SIZE_MB | Maximum video upload size | 100 |

---

## Deployment

### Backend on Render

| Setting | Value |
|---|---|
| Root Directory | backend |
| Build Command | pip install -r requirements.txt |
| Start Command | uvicorn app.main:app --host 0.0.0.0 --port $PORT |

### Frontend on Vercel

| Setting | Value |
|---|---|
| Root Directory | frontend |
| Framework | Vite |
| Build Command | npm run build |
| Output Directory | dist |

---

## Contributing

Pull requests are welcome. For major changes please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License. Feel free to use it for learning and portfolio purposes.

---

## Author

Built by [Your Name]

- GitHub: [github.com/yourusername](https://github.com/yourusername)
- LinkedIn: [linkedin.com/in/yourprofile](https://linkedin.com/in/yourprofile)