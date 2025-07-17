# 🚀 CI/CD Deployment Guide

This guide will walk you through setting up the complete CI/CD pipeline for SongHub on GitHub.

## 📋 Prerequisites

- GitHub account
- Docker Hub account (or other container registry)
- Basic understanding of Git and GitHub

## 🔧 Initial Setup

### 1. Fork or Upload to GitHub

1. **Option A: Fork the existing repository**
   - Go to https://github.com/itsayush1704/songhub1
   - Click "Fork" to create your own copy

2. **Option B: Create a new repository**
   ```bash
   # Initialize git in your project directory
   cd songhub1
   git init
   
   # Add all files
   git add .
   
   # Make initial commit
   git commit -m "Initial commit: SongHub with CI/CD setup"
   
   # Add your GitHub repository as origin
   git remote add origin https://github.com/YOUR_USERNAME/songhub1.git
   
   # Push to GitHub
   git branch -M main
   git push -u origin main
   ```

### 2. Configure GitHub Secrets

Go to your repository → Settings → Secrets and variables → Actions

Add the following secrets:

#### Required Secrets
```
DOCKER_USERNAME          # Your Docker Hub username
DOCKER_PASSWORD          # Your Docker Hub password/token
STAGING_SERVER_HOST      # Staging server IP/hostname (optional)
STAGING_SERVER_USER      # Staging server username (optional)
STAGING_SSH_KEY          # SSH private key for staging (optional)
PRODUCTION_SERVER_HOST   # Production server IP/hostname (optional)
PRODUCTION_SERVER_USER   # Production server username (optional)
PRODUCTION_SSH_KEY       # SSH private key for production (optional)
```

#### Optional Secrets (for advanced features)
```
SLACK_WEBHOOK_URL        # For Slack notifications
TELEGRAM_BOT_TOKEN       # For Telegram notifications
TELEGRAM_CHAT_ID         # Telegram chat ID
SONARQUBE_TOKEN          # For code quality analysis
```

### 3. Set Up Docker Hub Repository

1. Log in to Docker Hub
2. Create a new repository named `songhub`
3. Make it public or private as needed
4. Note your Docker Hub username for the secrets

## 🔄 CI/CD Pipeline Overview

The pipeline consists of 4 main stages:

### Stage 1: Code Quality & Testing
- **Triggers**: Push to any branch, Pull requests
- **Actions**: Linting, security scanning, unit tests
- **Duration**: ~3-5 minutes

### Stage 2: Build & Integration
- **Triggers**: Successful tests
- **Actions**: Docker build, vulnerability scanning, integration tests
- **Duration**: ~5-8 minutes

### Stage 3: Staging Deployment
- **Triggers**: Push to `main` branch
- **Actions**: Deploy to staging, smoke tests, performance tests
- **Duration**: ~3-5 minutes

### Stage 4: Production Deployment
- **Triggers**: Manual approval
- **Actions**: Deploy to production, health checks, monitoring
- **Duration**: ~2-3 minutes

## 🧪 Testing the Pipeline

### 1. Test Basic CI

1. Make a small change to any file:
   ```bash
   echo "# Test change" >> README.md
   git add README.md
   git commit -m "test: trigger CI pipeline"
   git push
   ```

2. Go to GitHub → Actions tab
3. Watch the "CI/CD Pipeline" workflow run
4. Verify all tests pass

### 2. Test Pull Request Workflow

1. Create a new branch:
   ```bash
   git checkout -b feature/test-pr
   ```

2. Make changes and push:
   ```bash
   echo "console.log('PR test');" >> templates/index.html
   git add templates/index.html
   git commit -m "feat: add test console log"
   git push -u origin feature/test-pr
   ```

3. Create a Pull Request on GitHub
4. Verify CI runs on the PR
5. Merge the PR to trigger staging deployment

### 3. Test Production Deployment

1. Go to GitHub → Actions
2. Find the "Deploy to Production" workflow
3. Click "Run workflow" manually
4. Approve the deployment when prompted
5. Monitor the deployment process

## 🔧 Customizing the Pipeline

### Adding New Tests

1. **Unit Tests**: Add to `tests/test_app.py`
2. **Integration Tests**: Add to `tests/test_integration.py`
3. **Performance Tests**: Modify `tests/performance/locustfile.py`

### Modifying Deployment Targets

Edit `.github/workflows/ci-cd.yml`:

```yaml
# Change deployment commands
- name: Deploy to Staging
  run: |
    # Your custom deployment commands
    docker-compose -f docker-compose.staging.yml up -d
```

### Adding Notifications

Add to the workflow file:

```yaml
- name: Notify Slack
  if: failure()
  uses: 8398a7/action-slack@v3
  with:
    status: failure
    webhook_url: ${{ secrets.SLACK_WEBHOOK_URL }}
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Docker Build Fails
```bash
# Check Dockerfile syntax
docker build -t test .

# Verify requirements.txt
pip install -r requirements.txt
```

#### 2. Tests Fail in CI but Pass Locally
```bash
# Run tests in same environment as CI
docker run --rm -v $(pwd):/app python:3.10-slim bash -c \
  "cd /app && pip install -r requirements.txt && pytest"
```

#### 3. Deployment Fails
- Check server connectivity
- Verify SSH keys are correct
- Ensure Docker is installed on target servers

#### 4. Secrets Not Working
- Verify secret names match exactly
- Check for trailing spaces in secret values
- Ensure secrets are set at repository level

### Debug Commands

```bash
# Test Docker build locally
docker build -t songhub:test .
docker run -p 8002:8002 songhub:test

# Run security scans locally
pip install bandit safety
bandit -r app.py
safety check

# Test with different Python versions
docker run --rm -v $(pwd):/app python:3.10-slim bash -c \
  "cd /app && pip install -r requirements.txt && python app.py"
```

## 📊 Monitoring Your Pipeline

### GitHub Actions Insights

1. Go to repository → Insights → Actions
2. Monitor:
   - Workflow run frequency
   - Success/failure rates
   - Average run duration
   - Most failing workflows

### Setting Up Alerts

1. **Email Notifications**:
   - Go to GitHub → Settings → Notifications
   - Enable "Actions" notifications

2. **Slack Integration**:
   ```yaml
   - name: Slack Notification
     uses: 8398a7/action-slack@v3
     with:
       status: ${{ job.status }}
       webhook_url: ${{ secrets.SLACK_WEBHOOK_URL }}
   ```

## 🚀 Advanced Features

### 1. Multi-Environment Deployments

Create separate workflow files:
- `.github/workflows/deploy-dev.yml`
- `.github/workflows/deploy-staging.yml`
- `.github/workflows/deploy-prod.yml`

### 2. Database Migrations

Add to deployment steps:
```yaml
- name: Run Migrations
  run: |
    python manage.py migrate
```

### 3. Blue-Green Deployment

```yaml
- name: Blue-Green Deploy
  run: |
    # Deploy to green environment
    docker-compose -f docker-compose.green.yml up -d
    
    # Health check
    curl -f http://green.example.com/health
    
    # Switch traffic
    # Update load balancer configuration
```

### 4. Rollback Strategy

```yaml
- name: Rollback on Failure
  if: failure()
  run: |
    # Rollback to previous version
    docker-compose -f docker-compose.blue.yml up -d
```

## 📚 Next Steps

1. **Learn More**:
   - [GitHub Actions Documentation](https://docs.github.com/en/actions)
   - [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
   - [CI/CD Best Practices](https://docs.github.com/en/actions/guides/about-continuous-integration)

2. **Extend the Project**:
   - Add database integration
   - Implement caching strategies
   - Add monitoring and logging
   - Set up infrastructure as code

3. **Practice Scenarios**:
   - Simulate production incidents
   - Practice rollback procedures
   - Test disaster recovery
   - Implement feature flags

---

**🎉 Congratulations!** You now have a fully functional CI/CD pipeline. Start experimenting with different features and see how the automation helps maintain code quality and deployment reliability!