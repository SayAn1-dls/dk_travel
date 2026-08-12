# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.x     | ✅ Active  |
| 0.x     | ⚠️ Critical fixes only |

## Reporting a Vulnerability

If you discover a security vulnerability in Wanderly, please report it responsibly.

### How to Report

1. **DO NOT** open a public GitHub issue for security vulnerabilities
2. Email the maintainers at `sayanbhatt2005@gmail.com` with:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact assessment
   - Suggested fix (if any)

### Response Timeline

- **Acknowledgment**: Within 48 hours
- **Initial Assessment**: Within 1 week
- **Fix & Disclosure**: Within 30 days (coordinated)

## Security Best Practices

### For Contributors

- Never commit secrets, API keys, or credentials to the repository
- Use environment variables for all sensitive configuration
- Validate and sanitize all user inputs
- Use parameterized queries for database operations
- Keep dependencies up to date

### For Deployment

- Enable HTTPS in production
- Set appropriate CORS origins (do not use wildcard in production)
- Use strong, unique passwords for database access
- Enable rate limiting on all API endpoints
- Regularly rotate API keys and tokens
- Monitor logs for suspicious activity

## Dependencies

We regularly audit our dependencies using:
- `pip audit` for Python packages
- `npm audit` for Node.js packages

## Acknowledgments

We appreciate the security research community and will acknowledge reporters (with permission) in our release notes.
