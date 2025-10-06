# SeatDuty Backend - Environment Setup

## 🚀 Quick Start

### Development Environment
```bash
# Start development environment
./start.sh development
# or
./start.sh dev
# or
./start.sh
```

### Production Environment
```bash
# Start production environment
./start.sh production
# or
./start.sh prod
```

### Run Tests
```bash
# Run tests (development only)
./start.sh test
```

## 👑 Admin User Setup

### Default Admin User
The system automatically creates a default admin user on first startup:

**Development:**
- Email: `admin@seatduty.com`
- Password: `admin123`
- Name: `System Administrator`

**Production:**
- Email: `admin@yourdomain.com` (configurable)
- Password: `your_secure_admin_password_here` (configurable)
- Name: `System Administrator`

### Admin Management

#### Via API (after login):
```bash
# Login as admin first
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@seatduty.com", "password": "admin123"}'

# Create new admin
curl -X POST http://localhost:8001/admin/create-admin \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"email": "newadmin@example.com", "password": "password123", "name": "New Admin"}'

# List all admins
curl -X GET http://localhost:8001/admin/list-admins \
  -H "Authorization: Bearer <token>"
```

#### Via Scripts:
```bash
# Create admin user
./scripts/admin-docker.sh create admin@example.com password123 "Admin Name"

# Reset admin password
./scripts/admin-docker.sh reset-password admin@example.com newpassword123

# List admin users
./scripts/admin-docker.sh list
```

## 📁 Environment Files

### Development (`env.development`)
- **Database**: PostgreSQL on port 5433
- **API**: FastAPI with hot reload on port 8001
- **Testing**: Full test suite with test database
- **Debug**: Enabled with detailed logging
- **Security**: Relaxed for development

### Production (`env.production`)
- **Database**: PostgreSQL on port 5432
- **API**: Gunicorn with multiple workers on port 8000
- **Testing**: Disabled (security)
- **Debug**: Disabled
- **Security**: Strict with Nginx reverse proxy

## 🐳 Docker Compose Files

### Development (`docker-compose.yaml`)
- API with hot reload
- Development database
- Test database and test runner
- Volume mounting for live code changes

### Production (`docker-compose.prod.yml`)
- Optimized API with Gunicorn
- Production database
- Nginx reverse proxy
- Security headers
- No test services

## 🔧 Environment Variables

| Variable | Development | Production |
|----------|-------------|------------|
| `ENVIRONMENT` | development | production |
| `DATABASE_URL` | postgresql://postgres:postgres@localhost:5433/seatduty | postgresql://postgres:password@localhost:5432/seatduty |
| `JWT_SECRET_KEY` | dev-secret-key-change-in-production | your_super_secure_jwt_secret_key_here |
| `DEBUG` | true | false |
| `LOG_LEVEL` | DEBUG | INFO |

## 🧪 Testing

### Development Testing
```bash
# Run all tests
./start.sh test

# Run specific test file
docker compose run test pytest tests/test_auth.py -v

# Run with coverage
docker compose run test pytest --cov=app tests/ -v
```

### API Testing (Development Only)
```bash
# Start development environment
./start.sh development

# Test endpoints
curl http://localhost:8001/test/health-check
curl -X POST http://localhost:8001/test/run-all
curl -X POST http://localhost:8001/test/cleanup
```

## 🔒 Security Features

### Development
- Test endpoints enabled (`/test/*`)
- Debug logging enabled
- Relaxed CORS settings
- Default JWT secret (change for production)

### Production
- Test endpoints disabled
- Nginx reverse proxy
- Security headers
- Strict CORS settings
- Secure JWT secrets required

## 📊 Ports

| Service | Development | Production |
|---------|-------------|------------|
| API | 8001 | 8000 |
| Database | 5433 | 5432 |
| Test DB | 5434 | - |
| Nginx | - | 80, 443 |

## 🚀 Deployment

### Local Production
```bash
# 1. Create production environment file
cp env.production.example env.production
# Edit env.production with your secure values

# 2. Start production environment
./start.sh production
```

### Production Checklist
- [ ] Set secure `POSTGRES_PASSWORD`
- [ ] Set secure `JWT_SECRET_KEY`
- [ ] Configure SSL certificates in `nginx/ssl/`
- [ ] Update `nginx/nginx.prod.conf` for your domain
- [ ] Set up database backups
- [ ] Configure monitoring and logging

## 🛠️ Development Workflow

1. **Start Development**: `./start.sh development`
2. **Make Changes**: Code changes auto-reload
3. **Run Tests**: `./start.sh test`
4. **Test API**: Use `/test/*` endpoints
5. **Deploy**: `./start.sh production`

## 📝 Notes

- Test endpoints are **only available in development**
- Production uses Gunicorn for better performance
- Development uses Uvicorn for hot reload
- All environments use health checks for reliable startup
- Production includes Nginx for reverse proxy and security
