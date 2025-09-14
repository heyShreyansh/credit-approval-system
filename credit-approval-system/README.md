# 🏦 Credit Approval System

A comprehensive Django-based credit approval system with a beautiful web dashboard, REST API, and advanced credit scoring algorithms.

## ✨ Features

### 🎯 Core Functionality
- **Customer Registration**: Register new customers with comprehensive validation
- **Loan Eligibility Checking**: Advanced credit scoring algorithm
- **Loan Creation**: Create loans with transaction safety
- **Loan Management**: View and manage customer loans
- **Real-time Dashboard**: Beautiful web interface for all operations

### 🔧 Technical Features
- **Django REST API**: 5 comprehensive endpoints
- **PostgreSQL Database**: Robust data storage
- **Redis Caching**: Background job processing
- **Docker Containerization**: Easy deployment
- **Security Hardened**: CSRF, XSS protection, input validation
- **Performance Optimized**: Single-query database operations
- **Comprehensive Logging**: Structured logging throughout
- **Error Handling**: Specific exception handling

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd credit-approval-system
   ```

2. **Start the application**
   ```bash
   docker-compose up --build
   ```

3. **Access the application**
   - **Dashboard**: http://localhost:8000/
   - **API Documentation**: http://localhost:8000/api-docs/
   - **Admin Panel**: http://localhost:8000/admin/
   - **RQ Dashboard**: http://localhost:8000/django-rq/

## 📱 Web Dashboard

The system includes a beautiful, responsive web dashboard with:

### 🎨 Interface Features
- **Modern Design**: Gradient backgrounds and professional styling
- **Responsive Layout**: Works on desktop, tablet, and mobile
- **Tabbed Interface**: Easy navigation between features
- **Real-time Results**: Instant feedback on all operations
- **Form Validation**: Client-side and server-side validation

### 📋 Dashboard Tabs
1. **Register Customer**: Add new customers to the system
2. **Check Eligibility**: Verify loan eligibility with credit scoring
3. **Create Loan**: Process new loan applications
4. **View Loans**: Browse customer loan history
5. **System Status**: Monitor service health

## 🔌 API Endpoints

### Customer Management
- `POST /register/` - Register a new customer
- `GET /view-loans/{customer_id}/` - View customer's loans

### Loan Operations
- `POST /check-eligibility/` - Check loan eligibility
- `POST /create-loan/` - Create a new loan
- `GET /view-loan/{loan_id}/` - View loan details

### Documentation
- `GET /` - Redirects to dashboard
- `GET /api/` - JSON API documentation
- `GET /api-docs/` - Beautiful HTML documentation

## 🏗️ Architecture

### Backend Stack
- **Django 4.2.7**: Web framework
- **Django REST Framework**: API development
- **PostgreSQL 15**: Primary database
- **Redis 7**: Caching and job queue
- **RQ**: Background job processing

### Frontend
- **HTML5/CSS3**: Modern responsive design
- **JavaScript**: Interactive functionality
- **Bootstrap-inspired**: Professional styling

### Infrastructure
- **Docker**: Containerization
- **Docker Compose**: Multi-service orchestration
- **Nginx-ready**: Production deployment ready

## 🧮 Credit Scoring Algorithm

The system uses a sophisticated credit scoring algorithm based on:

### Scoring Factors (100 points total)
1. **Payment History (30 points)**: Past loan payment performance
2. **Loan Count (20 points)**: Number of loans taken (diminishing returns)
3. **Current Year Activity (25 points)**: Loan activity in current year
4. **Volume vs Income (25 points)**: Total loan volume vs annual income

### Interest Rate Corrections
- **Score > 50**: No correction needed
- **Score 30-50**: Minimum 12% interest rate
- **Score 10-30**: Minimum 16% interest rate
- **Score ≤ 10**: Loan rejected

### Additional Checks
- **EMI Limit**: Total EMIs cannot exceed 50% of monthly salary
- **Approved Limit**: Current loans cannot exceed approved limit
- **Age Validation**: Customers must be 18-100 years old

## 🔒 Security Features

### Input Validation
- **Phone Numbers**: 10-15 digit validation
- **Names**: Character and length validation
- **Financial Data**: Range and format validation
- **Age**: 18-100 year range validation

### Security Headers
- **XSS Protection**: Browser XSS filtering
- **Content Type**: No-sniff protection
- **Frame Options**: Clickjacking protection
- **HSTS**: HTTP Strict Transport Security
- **CSRF**: Cross-site request forgery protection

### Database Security
- **Transaction Safety**: Atomic operations
- **SQL Injection**: Django ORM protection
- **Data Validation**: Model-level validation

## 📊 Database Schema

### Customer Model
- `customer_id`: Primary key
- `first_name`, `last_name`: Customer names
- `age`: Customer age (18-100)
- `phone_number`: Unique phone number
- `monthly_salary`: Monthly income
- `approved_limit`: Calculated credit limit
- `current_debt`: Current outstanding debt
- `created_at`, `updated_at`: Timestamps

### Loan Model
- `loan_id`: Primary key
- `customer`: Foreign key to Customer
- `loan_amount`: Loan principal
- `tenure`: Loan duration in months
- `interest_rate`: Annual interest rate
- `monthly_repayment`: Calculated EMI
- `emis_paid_on_time`: Payment history
- `start_date`, `end_date`: Loan period
- `is_active`: Loan status
- `created_at`, `updated_at`: Timestamps

## 🚀 Deployment

### Development
```bash
docker-compose up --build
```

### Production
1. Set environment variables:
   - `DEBUG=False`
   - `SECRET_KEY=your-secret-key`
   - `ALLOWED_HOSTS=your-domain.com`

2. Run migrations:
   ```bash
   docker-compose exec web python manage.py migrate
   ```

3. Collect static files:
   ```bash
   docker-compose exec web python manage.py collectstatic
   ```

## 📈 Performance Optimizations

### Database
- **Single Query Operations**: Optimized credit score calculation
- **Select Related**: Reduced N+1 query problems
- **Indexed Fields**: Optimized lookups

### Caching
- **Redis Integration**: Session and job caching
- **Background Jobs**: Asynchronous data processing

### Security
- **Input Sanitization**: Comprehensive validation
- **Rate Limiting**: Ready for production limits
- **Error Handling**: Graceful error responses

## 🧪 Testing

### Manual Testing
Use the web dashboard at http://localhost:8000/ to test all functionality:

1. **Register a customer**
2. **Check loan eligibility**
3. **Create a loan**
4. **View loan details**

### API Testing
```bash
# Register customer
curl -X POST http://localhost:8000/register/ \
  -H "Content-Type: application/json" \
  -d '{"first_name": "John", "last_name": "Doe", "age": 30, "monthly_income": 50000, "phone_number": "1234567890"}'

# Check eligibility
curl -X POST http://localhost:8000/check-eligibility/ \
  -H "Content-Type: application/json" \
  -d '{"customer_id": 1, "loan_amount": 100000, "interest_rate": 12.0, "tenure": 12}'
```

## 📝 Logging

The system includes comprehensive logging:
- **Application Logs**: `/logs/django.log`
- **Console Output**: Real-time debugging
- **Error Tracking**: Detailed error information
- **API Requests**: Request/response logging

## 🔧 Configuration

### Environment Variables
- `DEBUG`: Debug mode (default: False)
- `SECRET_KEY`: Django secret key
- `ALLOWED_HOSTS`: Allowed hostnames
- `DB_NAME`: Database name
- `DB_USER`: Database user
- `DB_PASSWORD`: Database password
- `DB_HOST`: Database host
- `DB_PORT`: Database port
- `REDIS_HOST`: Redis host
- `REDIS_PORT`: Redis port

### Docker Services
- **web**: Django application (port 8000)
- **db**: PostgreSQL database (port 5432)
- **redis**: Redis cache (port 6379)
- **worker**: Background job processor

## 📚 Documentation

- **API Documentation**: http://localhost:8000/api-docs/
- **Code Comments**: Comprehensive inline documentation
- **README**: This comprehensive guide
- **Git History**: Detailed commit history

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Check the API documentation
- Review the logs in `/logs/`
- Check Docker container status: `docker-compose ps`
- View application logs: `docker-compose logs web`

## 🎯 Future Enhancements

- [ ] User authentication and authorization
- [ ] Advanced reporting and analytics
- [ ] Email notifications
- [ ] Mobile app integration
- [ ] Advanced credit scoring models
- [ ] Integration with external credit bureaus
- [ ] Automated loan processing workflows
- [ ] Real-time notifications
- [ ] Advanced dashboard analytics
- [ ] Multi-tenant support

---

**Built with ❤️ using Django, PostgreSQL, Redis, and Docker**
