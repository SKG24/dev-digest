# Dev Digest - Personalized Coding Digest Generator

A professional, self-service platform that generates personalized daily coding digests for developers.

## Features

- **GitHub Integration**: Track issues, pull requests, and trending repositories
- **Stack Overflow**: Get latest questions from your technology stack
- **Web Interface**: Clean, professional UI for easy configuration
- **Multi-User Support**: Scalable platform for multiple developers
- **Daily Automation**: Scheduled digest delivery at 8 PM
- **Fault Tolerance**: Comprehensive error handling and retry logic
- **Admin Panel**: System monitoring and user management

## Quick Start

### Prerequisites

- Python 3.9+
- GitHub Personal Access Token
- Email account with SMTP access (Gmail recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd dev-digest
   ```

2. **Run setup script**
   ```bash
   python setup.py
   ```

3. **Update environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

4. **Start the application**
   ```bash
   python -m app.main
   ```

5. **Access the application**
   - Web Interface: http://localhost:8000
   - Admin Panel: http://localhost:8000/admin/login

### Docker Deployment

```bash
# Copy environment file
cp .env.example .env
# Edit .env with your credentials

# Start with Docker Compose
docker-compose up -d
```

## Configuration

### Environment Variables

```bash
# Required
GITHUB_TOKEN=your_github_personal_access_token
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_FROM=your_email@gmail.com

# Optional
SECRET_KEY=your-secret-key-here
ADMIN_PASSWORD=your-admin-password
APP_URL=http://localhost:8000
```
## Usage

### For Users

1. **Sign Up**: Visit the homepage and click "Get Started"
2. **Configure**: Add your GitHub repositories, programming languages, and Stack Overflow tags
3. **Receive Digests**: Get daily emails at 8 PM with personalized content

### For Administrators

1. **Access Admin Panel**: Visit `/admin/login`
2. **Monitor System**: View user statistics and system health
3. **Manage Users**: Monitor active users and digest delivery status

## API Endpoints

### Public Routes
- `GET /` - Landing page
- `GET /signup` - Registration form
- `POST /signup` - Create new user
- `GET /dashboard` - User dashboard (authenticated)
- `GET /settings` - User settings (authenticated)
- `POST /settings` - Update preferences (authenticated)

### Admin Routes
- `GET /admin/login` - Admin login
- `GET /admin` - Admin dashboard (authenticated)

### Internal API
- `POST /api/trigger-digest/{user_id}` - Manual digest trigger

## Testing

Run the test suite:

```bash
# Run all tests
python run_tests.py

# Run specific test file
python -m pytest tests/test_services.py -v

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=html
```

**Test is not updated as per the latest file structure.**

### Project Structure
```
dev-digest/
├── app/
│   ├── main.py              # FastAPI application
│   ├── database.py          # Database models
│   ├── models.py            # Pydantic models
│   └── services/            # Business logic
├── static/                  # CSS, JS files
├── templates/               # HTML templates
├── tests/                   # Test suite
├── docker/                  # Docker configuration
└── requirements.txt         # Python dependencies
```

### Visuals

1. Client Dashboard

   ![screenshot](https://github.com/SKG24/dev-digest/blob/main/screenshot_results/Screenshot%202025-07-05%20at%205.47.39%20PM.png)

2. Client settings to change preferences

   ![screenshot](https://github.com/SKG24/dev-digest/blob/main/screenshot_results/Screenshot%202025-07-05%20at%205.47.51%20PM.png)
   ![screenshot](https://github.com/SKG24/dev-digest/blob/main/screenshot_results/Screenshot%202025-07-05%20at%205.47.59%20PM.png)

3. Main Dashboard

   ![screenshot](https://github.com/SKG24/dev-digest/blob/main/screenshot_results/Screenshot%202025-07-05%20at%205.48.16%20PM.png)

4. Admin Dashboard

   ![screenshot](https://github.com/SKG24/dev-digest/blob/main/screenshot_results/Screenshot%202025-07-05%20at%205.48.23%20PM.png)

5. Email sent to Client

   ![screenshot](https://github.com/SKG24/dev-digest/blob/main/screenshot_results/Screenshot%202025-07-05%20at%205.49.13%20PM.png)
   ![screenshot](https://github.com/SKG24/dev-digest/blob/main/screenshot_results/Screenshot%202025-07-05%20at%205.48.43%20PM.png)
   ![screenshot](https://github.com/SKG24/dev-digest/blob/main/screenshot_results/Screenshot%202025-07-05%20at%205.48.50%20PM.png)
   ![screenshot](https://github.com/SKG24/dev-digest/blob/main/screenshot_results/Screenshot%202025-07-05%20at%205.48.55%20PM.png)
   ![screenshot](https://github.com/SKG24/dev-digest/blob/main/screenshot_results/Screenshot%202025-07-05%20at%205.49.03%20PM.png)
   



   
