# Security Guide for Retail Insights API

## 🔐 Security Implementation

This document outlines the security measures implemented in the Retail Insights API and provides guidance for secure deployment.

## ✅ Implemented Security Features

### 1. Authentication & Authorization

- **JWT-based Authentication**: Secure token-based authentication system
- **Password Hashing**: Bcrypt hashing for password storage
- **Protected Endpoints**: All API endpoints require authentication except `/auth/*`
- **User Management**: Complete user registration and login system

### 2. Input Validation & Sanitization

- **Pydantic Models**: Automatic input validation and serialization
- **Type Safety**: Strong typing throughout the application
- **SQL Injection Prevention**: SQLAlchemy ORM prevents SQL injection attacks

### 3. Security Headers

- **X-Content-Type-Options**: Prevents MIME type sniffing
- **X-Frame-Options**: Prevents clickjacking attacks
- **X-XSS-Protection**: Enables XSS filtering
- **Strict-Transport-Security**: Enforces HTTPS
- **Referrer-Policy**: Controls referrer information

### 4. Environment Security

- **No Hardcoded Credentials**: All sensitive data in environment variables
- **Required Environment Variables**: Application fails if critical variables are missing
- **Secure Defaults**: Debug mode disabled by default

### 5. Dependency Security

- **Updated Dependencies**: All known vulnerabilities patched
- **Security Scanning**: Safety tool integration for vulnerability detection

## 🚀 Quick Start (Secure Setup)

### 1. Generate Secure Keys

```bash
python scripts/generate_keys.py
```

### 2. Configure Environment

Create a `.env` file with the generated keys:

```env
# Database Configuration (REQUIRED)
DB_USER=your_username
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database_name

# Security Configuration (REQUIRED)
SECRET_KEY=your_generated_secret_key
JWT_SECRET_KEY=your_generated_jwt_secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Configuration
APP_ENV=production
APP_DEBUG=false
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Initialize Database

```bash
python scripts/init_db.py
```

### 5. Create Admin User

```bash
# Register via API
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@example.com",
    "password": "secure_password",
    "is_admin": true
  }'
```

## 🔒 Security Best Practices

### 1. Production Deployment

- **Use HTTPS**: Always deploy with SSL/TLS certificates
- **Environment Variables**: Never commit `.env` files to version control
- **Database Security**: Use strong passwords and restrict database access
- **Firewall**: Configure proper firewall rules
- **Regular Updates**: Keep all dependencies updated

### 2. API Usage

- **Token Management**: Store JWT tokens securely
- **Token Expiration**: Implement token refresh mechanisms
- **Rate Limiting**: Consider implementing rate limiting for production
- **Logging**: Monitor authentication attempts and failures

### 3. Database Security

- **Connection Encryption**: Use SSL for database connections
- **User Permissions**: Create dedicated database users with minimal privileges
- **Backup Security**: Encrypt database backups

## 🛡️ Security Monitoring

### 1. Logging

Monitor these events:

- Failed authentication attempts
- Unauthorized access attempts
- Database connection errors
- API usage patterns

### 2. Regular Security Audits

- Run `safety check` regularly
- Update dependencies monthly
- Review access logs
- Test authentication flows

## 🚨 Security Incident Response

### 1. If Credentials are Compromised

1. Immediately rotate all secrets
2. Revoke all active tokens
3. Force password resets
4. Review access logs

### 2. If Database is Compromised

1. Isolate the database
2. Change all passwords
3. Review data integrity
4. Implement additional monitoring

## 📋 Security Checklist

- [ ] Environment variables configured
- [ ] Strong passwords generated
- [ ] HTTPS enabled in production
- [ ] Database access restricted
- [ ] Security headers configured
- [ ] Dependencies updated
- [ ] Authentication working
- [ ] Authorization tested
- [ ] Logging configured
- [ ] Backup strategy in place

## 🔧 Security Tools

### Vulnerability Scanning

```bash
# Install safety
pip install safety

# Scan for vulnerabilities
safety check
```

### Key Generation

```bash
# Generate secure keys
python scripts/generate_keys.py
```

## 📞 Security Contact

For security issues or questions, contact the development team.

---

**Remember**: Security is an ongoing process. Regularly review and update your security measures.
