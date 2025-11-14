"""
Configuration settings for GitHub Action Executor
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration"""
    
    # GitHub OAuth settings
    GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
    GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
    GITHUB_CALLBACK_URL = os.getenv("GITHUB_CALLBACK_URL", "http://localhost:8000/auth/github/callback")
    
    # GitHub App settings
    GITHUB_APP_ID = os.getenv("GITHUB_APP_ID")
    GITHUB_APP_INSTALLATION_ID = os.getenv("GITHUB_APP_INSTALLATION_ID")
    GITHUB_APP_PRIVATE_KEY_PATH = os.getenv("GITHUB_APP_PRIVATE_KEY_PATH")
    
    # Session settings
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key-in-production")
    
    # Default repository settings
    DEFAULT_REPO_OWNER = os.getenv("DEFAULT_REPO_OWNER", "")
    DEFAULT_REPO_NAME = os.getenv("DEFAULT_REPO_NAME", "")
    DEFAULT_WORKFLOW_ID = os.getenv("DEFAULT_WORKFLOW_ID", "")
    
    # Permission check settings
    # If True, check if user is contributor or collaborator before allowing workflow trigger
    # If False, allow any authenticated user to trigger workflows
    CHECK_PERMISSIONS = os.getenv("CHECK_PERMISSIONS", "true").lower() == "true"
    
    # Branch filter patterns (for filtering branches in UI)
    BRANCH_FILTER_PATTERNS = os.getenv("BRANCH_FILTER_PATTERNS", "").split(",") if os.getenv("BRANCH_FILTER_PATTERNS") else None
    
    # Auto-open run link in new tab
    AUTO_OPEN_RUN = os.getenv("AUTO_OPEN_RUN", "false").lower() == "true"


# Create config instance
config = Config()
