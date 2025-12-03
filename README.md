# CryptoAlert - Cryptocurrency Price Monitoring System

CryptoAlert is a web-based automated price monitoring and alert service designed for individual cryptocurrency investors.

## Features

- User registration, login, and password management
- Real-time cryptocurrency price display (BTC, ETH, BNB, XRP, ADA, SOL, DOGE)
- Custom price alert rules (trigger when price goes above/below threshold)
- Email notification system (automatic alerts when triggered)
- Scheduled data collection and analysis (updates every minute)

## Tech Stack

- **Backend**: Python 3, Flask
- **Database**: PostgreSQL
- **Price API**: CoinGecko
- **Email Service**: 163 Mail SMTP
- **Deployment**: Vercel

## Local Development

### 1. Start PostgreSQL Database

```bash
docker run --name cryptoalert-db \
  -e POSTGRES_PASSWORD=mysecretpassword \
  -e POSTGRES_USER=myuser \
  -e POSTGRES_DB=cryptoalert_dev \
  -p 5432:5432 \
  -d postgres
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy `.env.example` to `.env` and fill in the configuration:

```bash
cp .env.example .env
```

### 4. Initialize Database

```bash
python init_db.py
```

### 5. Start Development Server

```bash
python run.py
```

Visit http://localhost:5001

## Running Tests

```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/test_alert_logic.py

# Run integration tests
pytest tests/test_integration.py
```

## API Endpoints

### Public Endpoints
- `GET /` - Homepage/Dashboard
- `GET /health` - Health check

### User Authentication
- `GET/POST /register` - User registration
- `GET/POST /login` - User login
- `GET /logout` - User logout
- `GET/POST /profile` - Profile/Password change

### Alert Management (Login Required)
- `GET /alerts/` - View all alerts
- `GET/POST /alerts/create` - Create alert
- `GET/POST /alerts/edit/<id>` - Edit alert
- `POST /alerts/delete/<id>` - Delete alert
- `POST /alerts/toggle/<id>` - Toggle alert status

### Cron Jobs (Triggered by Vercel)
- `GET/POST /api/cron/collect-data` - Collect price data
- `GET/POST /api/cron/analyze-data` - Analyze and trigger alerts

## Project Structure

```
CryptoAlertFinalProject/
├── api/
│   └── index.py          # Vercel entry point
├── app/
│   ├── __init__.py       # Flask application factory
│   ├── config.py         # Configuration
│   ├── models/           # Data models
│   │   ├── user.py
│   │   ├── alert_rule.py
│   │   └── price_history.py
│   ├── services/         # Service layer
│   │   ├── db.py
│   │   ├── coingecko.py
│   │   ├── email.py
│   │   └── alert.py
│   ├── views/            # Views/Routes
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── alerts.py
│   │   ├── cron.py
│   │   └── health.py
│   └── templates/        # HTML templates
├── tests/                # Tests
├── .env.example          # Environment variable template
├── requirements.txt      # Python dependencies
├── vercel.json          # Vercel configuration
└── README.md
```

## License

MIT License
