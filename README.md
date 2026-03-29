# NexConflict - Movie Recommendation Platform

A full-stack movie recommendation system built for CT255H (Business Intelligence) course at HCMUS, implementing collaborative and content-based filtering algorithms on the MovieLens dataset.

## 🏗️ Architecture

**3-Tier Microservices:**
- **Frontend**: Next.js 15 (React 19, TypeScript, Tailwind CSS) - Port 3000
- **Backend**: Spring Boot 3.4.4 (Java 21, Spring Security, JWT) - Port 8080  
- **AI Service**: FastAPI (Python, scikit-learn, surprise) - Port 5000

**Data**: MovieLens 20M Dataset (20 million ratings, 27,000 movies)

## 🚀 Quick Start

### Prerequisites
- **Java 21** (for backend)
- **Node.js 18+** and **npm** (for frontend)
- **Python 3.10+** (for AI service)
- **Maven** (included as `mvnw` wrapper)

### 1. Clone Repository
```bash
git clone https://github.com/ngthtrong/CT255H-NexConflict.git
cd CT255H-NexConflict
```

### 2. Configure Environment Variables

Copy the example environment file and configure your secrets:
```bash
cp .env.example .env
```

Edit `.env` and set the following:
```env
# Required: Generate a secure JWT secret (at least 32 characters)
JWT_SECRET=your_generated_secret_here

# Optional: Get from https://www.themoviedb.org/settings/api
TMDB_API_KEY=your_tmdb_api_key_here
```

**⚠️ SECURITY:** See [SECURITY.md](SECURITY.md) for detailed setup instructions and best practices.

### 3. Start Backend (Spring Boot)

```bash
cd backend

# Set environment variables (choose one method):
# Option A: Windows PowerShell
$env:JWT_SECRET="your_secret"; $env:TMDB_API_KEY="your_key"

# Option B: Linux/Mac
export JWT_SECRET="your_secret"
export TMDB_API_KEY="your_key"

# Run the application
./mvnw spring-boot:run
# Windows: .\mvnw.cmd spring-boot:run
```

Backend will start at **http://localhost:8080**

**API Endpoints:**
- `/api/auth/register` - User registration
- `/api/auth/login` - User login (returns JWT token)
- `/api/movies` - Browse movies
- `/api/recommendations/trending` - Get trending movies
- `/api/ratings` - Submit movie ratings
- `/h2-console` - Database console (dev only)

### 4. Start Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```

Frontend will start at **http://localhost:3000**

### 5. Start AI Service (FastAPI)

```bash
cd ai-service

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Train models (first time only - takes several minutes)
python train.py

# Start API server
python main.py
```

AI Service will start at **http://localhost:5000**

**AI Endpoints:**
- `/recommend/collaborative/{user_id}` - Collaborative filtering recommendations
- `/recommend/content/{movie_id}` - Content-based similar movies
- `/recommend/hybrid/{user_id}` - Hybrid approach (collaborative + content)

### 6. Using Docker (Alternative)

Start all services with Docker Compose:

```bash
# Set environment variables first
export JWT_SECRET="your_secret"
export TMDB_API_KEY="your_key"

docker-compose up -d
```

## 📁 Project Structure

```
CT255H-NexConflict/
├── frontend/           # Next.js 15 (TypeScript + React 19)
│   ├── app/           # App router pages
│   ├── components/    # React components
│   └── lib/           # Utilities and API clients
├── backend/           # Spring Boot 3.4.4 (Java 21)
│   ├── src/main/
│   │   ├── java/com/example/backend/
│   │   │   ├── config/       # Security, CORS, DataLoader
│   │   │   ├── controller/   # REST endpoints
│   │   │   ├── dto/          # Data transfer objects
│   │   │   ├── entity/       # JPA entities
│   │   │   ├── repository/   # Data access layer
│   │   │   ├── security/     # JWT authentication
│   │   │   └── service/      # Business logic
│   │   └── resources/
│   │       └── application.properties  # Spring config
│   └── pom.xml        # Maven dependencies
├── ai-service/        # FastAPI (Python 3.10)
│   ├── main.py        # FastAPI server
│   ├── train.py       # Model training script
│   └── models/        # Trained ML models (generated)
├── data/              # MovieLens dataset (download separately)
│   ├── rating.csv     # User ratings (20M rows)
│   └── movie.csv      # Movie metadata (27K movies)
├── .env.example       # Environment variable template
└── SECURITY.md        # Security configuration guide
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
./mvnw test
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📊 Dataset Setup

Download the MovieLens 20M dataset:

1. Visit https://grouplens.org/datasets/movielens/20m/
2. Download `ml-20m.zip`
3. Extract `ratings.csv` and `movies.csv`
4. Place in the `data/` directory:
   ```
   data/
   ├── rating.csv   (rename from ratings.csv)
   └── movie.csv    (rename from movies.csv)
   ```

## 🔧 Development

### Database Access (H2 Console)

When backend is running, access H2 console at:
**http://localhost:8080/h2-console**

Connection settings:
- **JDBC URL**: `jdbc:h2:mem:cinestream`
- **Username**: `sa`
- **Password**: `password`

### API Documentation

Backend uses Spring Boot's built-in REST documentation. Once running, explore endpoints at:
- **Base URL**: http://localhost:8080/api

Example API call:
```bash
# Register a new user
curl -X POST http://localhost:8080/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123"}'

# Login and get JWT token
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'

# Use token to access protected endpoints
curl http://localhost:8080/api/user/profile \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 🛡️ Security

**⚠️ Important:**
- Never commit `.env` files with real credentials
- Rotate JWT secrets and API keys regularly
- See [SECURITY.md](SECURITY.md) for detailed security setup

## 📚 Tech Stack

### Frontend
- **Framework**: Next.js 15, React 19
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State**: React Context / Hooks
- **HTTP Client**: Fetch API

### Backend
- **Framework**: Spring Boot 3.4.4
- **Language**: Java 21 (Virtual Threads)
- **Security**: Spring Security, JWT
- **Database**: H2 (in-memory for dev), PostgreSQL support
- **ORM**: Spring Data JPA, Hibernate
- **Build**: Maven

### AI Service
- **Framework**: FastAPI
- **Language**: Python 3.10
- **ML Libraries**: scikit-learn, scikit-surprise
- **Data**: pandas, numpy
- **Algorithms**: 
  - Item-based KNN (Cosine Similarity)
  - SVD (Matrix Factorization)
  - Hybrid (Weighted KNN + SVD)

## 👥 Contributors

- **Nguyễn Thành Trọng** - Developer
- **[Team Member 2]** - Developer

## 📖 Course Information

- **Course**: CT255H - Ứng dụng và Máy học (Business Intelligence)
- **Institution**: University of Science, HCMUS
- **Academic Year**: 2024-2025

## 📄 License

This project is for educational purposes as part of CT255H course requirements.

## 🔗 Additional Resources

- [Architecture Documentation](docs/ARCHITECTURE.md)
- [Security Configuration](SECURITY.md)
- [API Reference](docs/API.md) (if available)
- [Deployment Guide](docs/DEPLOYMENT.md) (if available)