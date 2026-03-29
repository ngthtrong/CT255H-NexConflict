# Security Configuration Guide

## Environment Variables Setup

This project uses environment variables to protect sensitive credentials. **Never commit API keys or secrets to version control.**

### Required Environment Variables

#### 1. JWT_SECRET
Used for signing and verifying JWT authentication tokens.

**Generate a secure secret:**
```bash
# Using OpenSSL (recommended)
openssl rand -base64 32

# Using Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Using Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"
```

**Set the environment variable:**
```bash
# Linux/Mac
export JWT_SECRET="your_generated_secret_here"

# Windows (PowerShell)
$env:JWT_SECRET="your_generated_secret_here"

# Windows (CMD)
set JWT_SECRET=your_generated_secret_here
```

#### 2. TMDB_API_KEY
Required for fetching movie posters and metadata from The Movie Database (TMDB).

**Get your API key:**
1. Create a free account at https://www.themoviedb.org/
2. Go to Settings → API
3. Request an API key (choose "Developer" option)
4. Copy your API Key (v3 auth)

**Set the environment variable:**
```bash
# Linux/Mac
export TMDB_API_KEY="your_tmdb_api_key_here"

# Windows (PowerShell)
$env:TMDB_API_KEY="your_tmdb_api_key_here"

# Windows (CMD)
set TMDB_API_KEY=your_tmdb_api_key_here
```

### Local Development Setup

#### Option 1: Using .env file (Recommended)

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and fill in your actual values:
   ```env
   JWT_SECRET=your_generated_secret_here
   JWT_EXPIRATION=86400000
   TMDB_API_KEY=your_tmdb_api_key_here
   ```

3. **Spring Boot will NOT automatically load .env files.** You need to use a tool like:
   - **direnv** (Linux/Mac): https://direnv.net/
   - **dotenv-java** library (add to pom.xml)
   - Or manually export variables before running

#### Option 2: Manual Environment Variables

Export variables in your terminal before starting the application:

```bash
# Linux/Mac
export JWT_SECRET="your_secret"
export TMDB_API_KEY="your_key"
./mvnw spring-boot:run

# Windows PowerShell
$env:JWT_SECRET="your_secret"
$env:TMDB_API_KEY="your_key"
.\mvnw.cmd spring-boot:run
```

#### Option 3: IntelliJ IDEA / Eclipse

**IntelliJ IDEA:**
1. Run → Edit Configurations
2. Select your Spring Boot run configuration
3. Add to "Environment variables":
   ```
   JWT_SECRET=your_secret;TMDB_API_KEY=your_key
   ```

**Eclipse:**
1. Run → Run Configurations
2. Select your application
3. Go to "Environment" tab
4. Add the variables

### Production Deployment

**Never use default values in production.** Configure environment variables through:

- **AWS**: Elastic Beanstalk environment properties / ECS task definitions
- **Heroku**: `heroku config:set JWT_SECRET="..." TMDB_API_KEY="..."`
- **Docker**: Use `docker run -e JWT_SECRET="..." -e TMDB_API_KEY="..."`
- **Kubernetes**: ConfigMap or Secrets (prefer Secrets for sensitive data)
- **Azure**: Application Settings
- **Google Cloud**: Environment variables in App Engine / Cloud Run

### Security Best Practices

1. **Rotate secrets regularly** - Change JWT_SECRET and TMDB_API_KEY periodically
2. **Use different secrets per environment** - Dev/staging/production should have unique values
3. **Never log secrets** - Ensure secrets don't appear in application logs
4. **Revoke compromised keys immediately**:
   - JWT_SECRET: Generate a new one and redeploy (users will need to re-login)
   - TMDB_API_KEY: Go to TMDB settings and regenerate your key

### Verification

Run this command to verify environment variables are set:

```bash
# Linux/Mac/Windows PowerShell
echo $env:JWT_SECRET
echo $env:TMDB_API_KEY

# Windows CMD
echo %JWT_SECRET%
echo %TMDB_API_KEY%
```

### Troubleshooting

**Error: "JWT secret is too short"**
- Ensure JWT_SECRET is at least 32 characters (256 bits)

**Error: "TMDB API key invalid"**
- Verify you copied the correct key from TMDB settings
- Ensure there are no extra spaces or quotes

**Error: "Could not resolve placeholder 'JWT_SECRET'"**
- Environment variable is not set
- Spring Boot cannot read .env files by default - use one of the methods above

## Incident Response

**If a secret is accidentally committed to Git:**

1. **Immediately revoke the exposed credential**:
   - JWT_SECRET: Generate a new one
   - TMDB_API_KEY: Regenerate in TMDB settings

2. **Remove from Git history** (if pushed to remote):
   ```bash
   # WARNING: This rewrites history - coordinate with team
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch backend/src/main/resources/application.properties" \
     --prune-empty --tag-name-filter cat -- --all
   
   git push origin --force --all
   ```

3. **Update all environments** with new secrets

4. **Document the incident** for security audit trail
