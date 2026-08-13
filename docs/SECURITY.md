# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly:

1. **Do NOT** open a public GitHub issue
2. Email us at security@dktravel.com
3. Include a detailed description of the vulnerability
4. Allow up to 48 hours for an initial response

## Security Measures

- All API endpoints require authentication via JWT tokens
- Passwords are hashed using bcrypt
- HTTPS enforced in production
- SQL injection prevention via parameterized queries
- CORS configured for allowed origins only
- Rate limiting on authentication endpoints
- Input validation on all user-facing endpoints

## Dependencies

We regularly update dependencies and monitor for known vulnerabilities using Dependabot.
