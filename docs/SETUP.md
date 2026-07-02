# Setup Guide

## Development Environment Setup

### Prerequisites

1. **Python 3.13+**
   ```bash
   python --version
   # Python 3.13.x
   ```

2. **Node.js 22+**
   ```bash
   node --version
   # v22.x.x
   ```

3. **Docker Desktop**
   - Required for PostgreSQL and Redis

4. **Git**

### 1. Clone Repository

```bash
git clone https://github.com/Sahadat516/TSBL.git
cd TSBL
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment config
cp .env.dev .env

# Start infrastructure (PostgreSQL + Redis)
docker compose up -d postgres redis

# Run database migrations
alembic upgrade head

# Start backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 4. Verify Installation

- Backend: http://localhost:8000/docs
- Frontend: http://localhost:3000
- Health: http://localhost:8000/api/v1/health
- Readiness: http://localhost:8000/api/v1/ready
- Liveness: http://localhost:8000/api/v1/live

### 5. Docker Compose (Full Stack)

```bash
# Start all services
docker compose up --build

# Start specific services
docker compose up -d postgres redis backend frontend

# View logs
docker compose logs -f backend
docker compose logs -f frontend

# Stop all services
docker compose down

# Stop and remove volumes (DESTROYS DATA)
docker compose down -v
```

## Testing Setup

### Backend Tests

```bash
cd backend

# Install test dependencies
pip install pytest pytest-asyncio pytest-cov httpx

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=term --cov-report=html

# Run specific test file
pytest tests/unit/test_security.py -v
```

## Common Issues

### PostgreSQL Connection Refused
Ensure Docker containers are running:
```bash
docker compose up -d postgres redis
```

### Module Not Found Errors
Ensure virtual environment is activated and dependencies are installed:
```bash
.venv\Scripts\activate
pip install -r requirements.txt
```

### Alembic Migrations Not Found
```bash
cd backend
alembic upgrade head
alembic revision --autogenerate -m "description"
```

## Environment Configuration

The application supports three environments:

- **Development** (`.env.dev`): Local development with debugging enabled
- **Testing** (`.env.test`): CI/CD and automated tests
- **Production** (`.env.prod`): Production deployment with security hardening
