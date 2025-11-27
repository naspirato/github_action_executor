# Quick Start

## 1. Install Dependencies

```bash
pip install -r requirements.txt
```

## 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill it in:

```bash
cp .env.example .env
```

Minimum required variables:
- `SECRET_KEY` - any random secret key
- `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET` - from OAuth App
- `GITHUB_APP_ID` and `GITHUB_APP_INSTALLATION_ID` - from GitHub App
- `GITHUB_APP_PRIVATE_KEY_PATH` - path to private key file

## 3. Create GitHub App Private Key

Download the private key from GitHub App settings and save it as `github-app-private-key.pem`:

```bash
# File should be in format:
# -----BEGIN RSA PRIVATE KEY-----
# ...
# -----END RSA PRIVATE KEY-----
```

## 4. Run the Application

```bash
python app.py
```

Or with hot-reload:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

## 5. Open in Browser

http://localhost:8000

## Testing

1. Click "Sign in with GitHub"
2. Authorize
3. Fill in the form with repository and workflow
4. Select tests
5. Run the workflow

## Example Workflow for Testing

Create a `.github/workflows/test.yml` file in your repository:

```yaml
name: Test Workflow

on:
  workflow_dispatch:
    inputs:
      tests:
        description: 'Tests to run (comma-separated)'
        required: false
        type: string
        default: 'unit'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3
      
      - name: Run tests
        run: |
          echo "Running tests: ${{ inputs.tests }}"
          # Your commands to run tests
```

## Troubleshooting

### Error "Not authenticated"
- Make sure you've authorized through GitHub OAuth
- Check that `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET` are correct

### Error "Failed to trigger workflow"
- Check that GitHub App is installed in the repository
- Make sure the App has Actions permissions (Read and write)
- Check that `workflow_id` matches the workflow file name

### Error "User is not a collaborator"
- Make sure you are actually a repository collaborator (have access to the repository)
- Check that OAuth token has permissions to read the repository

### Error 403 "Resource not accessible by integration"
If you see an error in GitHub Actions workflow:
```
HttpError: Resource not accessible by integration
status: 403
```

This means that the GitHub App doesn't have the necessary permissions to perform the operation (e.g., creating comments in issues or PRs).

**Solution:**

1. **If the error is related to creating comments in issues/PRs:**
   - Go to GitHub App settings: `https://github.com/settings/apps`
   - Open your application
   - Go to **Permissions & events** section
   - In **Repository permissions** section, find **Issues**
   - Set permissions to **Read and write** (or **Write**)
   - Click **Save changes**

2. **After changing permissions, you MUST update the installation:**
   
   **For repository:**
   - Go to: `https://github.com/YOUR_USERNAME/YOUR_REPO/settings/installations`
   - Or: Settings → Integrations → GitHub Apps → find your application
   - Click **Configure** next to your GitHub App
   - On the installation page, click **Update installation** (or **Save**)
   
   **For organization:**
   - Go to: `https://github.com/organizations/YOUR_ORG/settings/installations`
   - Or: Organization Settings → GitHub Apps → find your application
   - Click **Configure** → **Update installation**
   
   **Important:** Without updating the installation, new permissions won't be applied!

3. **Check other necessary permissions:**
   - If workflow uses other operations (e.g., creating PRs), make sure the App has corresponding permissions
   - **Actions**: Read and write (for running workflows)
   - **Contents**: Read-only or Read and write (depending on needs)
   - **Issues**: Write (for creating comments)
   - **Pull requests**: Write (for creating comments in PRs)
   - **Workflows**: Write (for modifying workflow files during backport)

**Note:** After changing GitHub App permissions, all installations need to be updated manually. Without updating the installation, new permissions won't work!

### Error "OAuth App access restrictions"
If you see an error:
```
Although you appear to have the correct authorization credentials, 
the `organization-name` organization has enabled OAuth App access restrictions
```

This means that the organization has enabled access restrictions for OAuth applications. To resolve the issue:

1. **If you are the organization owner or have administrator rights:**
   - Go to organization settings: `https://github.com/organizations/ORGANIZATION_NAME/settings/oauth_application_policy`
   - Find your OAuth App in the "Third-party access" list
   - Click "Grant" or "Approve" for your application
   - More details: https://docs.github.com/articles/restricting-access-to-your-organization-s-data/

2. **If you are not an organization administrator:**
   - Contact the organization administrator
   - Ask them to approve the OAuth App in organization settings
   - The administrator should go to: `Settings → Third-party access → OAuth Apps`
   - And approve your application

3. **Alternative solution:**
   - If you don't have access to organization settings, you can use GitHub App instead of OAuth App
   - GitHub Apps don't require organization approval (if installed in the repository)
