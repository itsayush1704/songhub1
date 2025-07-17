# 🔧 GitHub Repository Setup Guide

This guide provides step-by-step instructions for setting up your GitHub repository with all necessary configurations for the CI/CD pipeline.

## 📁 Repository Setup

### Option 1: Fork Existing Repository

1. **Navigate to the original repository**
   - Go to: https://github.com/itsayush1704/songhub1
   - Click the "Fork" button in the top-right corner
   - Select your GitHub account as the destination

2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/songhub1.git
   cd songhub1
   ```

3. **Set up upstream remote** (to sync with original)
   ```bash
   git remote add upstream https://github.com/itsayush1704/songhub1.git
   git remote -v  # Verify remotes
   ```

### Option 2: Create New Repository

1. **Create repository on GitHub**
   - Go to GitHub and click "New repository"
   - Name: `songhub1` (or your preferred name)
   - Description: "Learn CI/CD through music streaming application"
   - Make it Public (recommended for learning)
   - Don't initialize with README (we have our own)

2. **Push existing code**
   ```bash
   cd /path/to/your/songhub1
   git init
   git add .
   git commit -m "Initial commit: SongHub with CI/CD setup"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/songhub1.git
   git push -u origin main
   ```

## 🔐 GitHub Secrets Configuration

### Accessing Secrets Settings

1. Go to your repository on GitHub
2. Click **Settings** tab
3. In the left sidebar, click **Secrets and variables** → **Actions**
4. Click **New repository secret**

### Required Secrets

#### Docker Hub Integration
```
Secret Name: DOCKER_USERNAME
Value: your-dockerhub-username
Description: Your Docker Hub username for pushing images
```

```
Secret Name: DOCKER_PASSWORD
Value: your-dockerhub-password-or-token
Description: Docker Hub password or access token (recommended)
```

**💡 Tip**: Use Docker Hub Access Tokens instead of passwords:
1. Go to Docker Hub → Account Settings → Security
2. Create New Access Token
3. Use the token as DOCKER_PASSWORD

#### Server Deployment (Optional)

For staging server:
```
Secret Name: STAGING_SERVER_HOST
Value: staging.yourdomain.com
Description: Staging server hostname or IP
```

```
Secret Name: STAGING_SERVER_USER
Value: deploy
Description: Username for staging server SSH access
```

```
Secret Name: STAGING_SSH_KEY
Value: -----BEGIN OPENSSH PRIVATE KEY-----
...
-----END OPENSSH PRIVATE KEY-----
Description: SSH private key for staging server access
```

For production server:
```
Secret Name: PRODUCTION_SERVER_HOST
Value: yourdomain.com
Description: Production server hostname or IP
```

```
Secret Name: PRODUCTION_SERVER_USER
Value: deploy
Description: Username for production server SSH access
```

```
Secret Name: PRODUCTION_SSH_KEY
Value: -----BEGIN OPENSSH PRIVATE KEY-----
...
-----END OPENSSH PRIVATE KEY-----
Description: SSH private key for production server access
```

### Optional Secrets (Advanced Features)

#### Slack Notifications
```
Secret Name: SLACK_WEBHOOK_URL
Value: https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX
Description: Slack webhook URL for CI/CD notifications
```

#### Telegram Notifications
```
Secret Name: TELEGRAM_BOT_TOKEN
Value: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz
Description: Telegram bot token for notifications
```

```
Secret Name: TELEGRAM_CHAT_ID
Value: -1001234567890
Description: Telegram chat ID for notifications
```

#### Code Quality Tools
```
Secret Name: SONARQUBE_TOKEN
Value: your-sonarqube-token
Description: SonarQube token for code quality analysis
```

```
Secret Name: CODECOV_TOKEN
Value: your-codecov-token
Description: Codecov token for coverage reporting
```

## 🌍 Environment Variables

### Repository Variables

Go to **Settings** → **Secrets and variables** → **Actions** → **Variables** tab

```
Variable Name: DOCKER_REGISTRY
Value: docker.io
Description: Docker registry URL
```

```
Variable Name: IMAGE_NAME
Value: songhub
Description: Docker image name
```

```
Variable Name: STAGING_URL
Value: https://staging.yourdomain.com
Description: Staging environment URL
```

```
Variable Name: PRODUCTION_URL
Value: https://yourdomain.com
Description: Production environment URL
```

## 🔧 Branch Protection Rules

### Setting Up Branch Protection

1. Go to **Settings** → **Branches**
2. Click **Add rule**
3. Branch name pattern: `main`
4. Configure the following:

#### Required Settings
- ✅ **Require a pull request before merging**
  - ✅ Require approvals: 1
  - ✅ Dismiss stale PR approvals when new commits are pushed
  - ✅ Require review from code owners

- ✅ **Require status checks to pass before merging**
  - ✅ Require branches to be up to date before merging
  - Add required status checks:
    - `test`
    - `lint`
    - `security-scan`
    - `build`

- ✅ **Require conversation resolution before merging**
- ✅ **Include administrators**

#### Optional Settings
- ✅ **Restrict pushes that create files**
- ✅ **Require linear history**
- ✅ **Require deployments to succeed before merging**

## 🏷️ Environment Setup

### Creating Environments

1. Go to **Settings** → **Environments**
2. Click **New environment**

#### Staging Environment
- **Name**: `staging`
- **Protection rules**:
  - ✅ Required reviewers: (leave empty for auto-deploy)
  - ✅ Wait timer: 0 minutes
  - ✅ Deployment branches: Selected branches → `main`

#### Production Environment
- **Name**: `production`
- **Protection rules**:
  - ✅ Required reviewers: Add yourself and team members
  - ✅ Wait timer: 5 minutes (optional cooling period)
  - ✅ Deployment branches: Selected branches → `main`

### Environment Secrets

For each environment, you can add specific secrets:

1. Click on the environment name
2. Add environment secrets:

**Staging Environment Secrets:**
```
DATABASE_URL=postgresql://user:pass@staging-db:5432/songhub
REDIS_URL=redis://staging-redis:6379
DEBUG=true
```

**Production Environment Secrets:**
```
DATABASE_URL=postgresql://user:pass@prod-db:5432/songhub
REDIS_URL=redis://prod-redis:6379
DEBUG=false
```

## 📊 GitHub Actions Permissions

### Repository Permissions

1. Go to **Settings** → **Actions** → **General**
2. Configure:

#### Actions permissions
- ✅ **Allow all actions and reusable workflows**

#### Workflow permissions
- ✅ **Read and write permissions**
- ✅ **Allow GitHub Actions to create and approve pull requests**

#### Fork pull request workflows
- ✅ **Run workflows from fork pull requests**
- ✅ **Send write tokens to workflows from fork pull requests**
- ✅ **Send secrets to workflows from fork pull requests**

## 🔍 Monitoring Setup

### GitHub Insights

1. Go to **Insights** → **Actions**
2. Monitor:
   - Workflow runs
   - Job duration
   - Success rates
   - Resource usage

### Notifications

1. Go to your **GitHub Settings** (not repository settings)
2. Click **Notifications**
3. Under **Actions**:
   - ✅ Email notifications for failed workflows
   - ✅ Web notifications for workflow runs

## 🧪 Testing Your Setup

### 1. Verify Secrets

Create a test workflow to verify secrets are working:

```yaml
# .github/workflows/test-secrets.yml
name: Test Secrets
on:
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Test Docker Hub Access
        run: |
          echo "Docker username: ${{ secrets.DOCKER_USERNAME }}"
          echo "Docker password length: ${#DOCKER_PASSWORD}"
        env:
          DOCKER_PASSWORD: ${{ secrets.DOCKER_PASSWORD }}
```

### 2. Test Branch Protection

1. Create a new branch:
   ```bash
   git checkout -b test/branch-protection
   echo "test" > test.txt
   git add test.txt
   git commit -m "test: branch protection"
   git push -u origin test/branch-protection
   ```

2. Create a Pull Request
3. Try to merge without approval (should be blocked)
4. Get approval and merge

### 3. Test CI/CD Pipeline

1. Make a change to trigger CI:
   ```bash
   git checkout main
   git pull
   echo "# CI/CD Test" >> README.md
   git add README.md
   git commit -m "test: trigger CI/CD pipeline"
   git push
   ```

2. Go to **Actions** tab and watch the workflow run

## 🚨 Security Best Practices

### Secret Management

1. **Use least privilege principle**
   - Only add secrets that are actually needed
   - Use read-only tokens when possible

2. **Rotate secrets regularly**
   - Set calendar reminders to update tokens
   - Use short-lived tokens when available

3. **Audit secret usage**
   - Regularly review which secrets are being used
   - Remove unused secrets

### Access Control

1. **Limit repository access**
   - Only give write access to trusted collaborators
   - Use teams for organization-wide access

2. **Enable two-factor authentication**
   - Required for all organization members
   - Use authenticator apps, not SMS

3. **Monitor repository activity**
   - Enable security alerts
   - Review audit logs regularly

## 🔧 Troubleshooting

### Common Issues

#### Secrets Not Working
```bash
# Check secret names (case-sensitive)
# Verify no trailing spaces
# Ensure secrets are at repository level, not organization
```

#### Workflow Permissions
```bash
# Error: "Resource not accessible by integration"
# Solution: Enable "Read and write permissions" in Actions settings
```

#### Branch Protection Bypass
```bash
# Error: "Required status check is not passing"
# Solution: Ensure all required checks are defined in workflow
```

### Debug Commands

```bash
# Test GitHub CLI access
gh auth status
gh repo view

# Test SSH access
ssh -T git@github.com

# Verify git configuration
git config --list
```

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Managing Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Branch Protection Rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches)
- [Environment Protection Rules](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment)

---

**✅ Checklist**

- [ ] Repository created/forked
- [ ] All required secrets added
- [ ] Branch protection rules configured
- [ ] Environments set up
- [ ] Workflow permissions enabled
- [ ] Test workflow runs successfully
- [ ] Notifications configured
- [ ] Security settings reviewed

**🎉 You're ready to start learning CI/CD with SongHub!**