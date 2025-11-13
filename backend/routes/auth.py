"""
Authentication routes for GitHub OAuth
"""
import secrets
import logging
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse

from backend.services.github_oauth import get_oauth_url, get_access_token, get_user_info

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/github")
async def github_login(request: Request):
    """Initiate GitHub OAuth login"""
    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    request.session["oauth_state"] = state
    logger.info(f"OAuth login initiated, state generated: {state[:10]}...")
    
    # Redirect to GitHub OAuth
    oauth_url = get_oauth_url(state=state)
    logger.info(f"Redirecting to GitHub OAuth: {oauth_url[:100]}...")
    return RedirectResponse(url=oauth_url)


@router.get("/github/callback")
async def github_callback(request: Request, code: str = None, state: str = None):
    """Handle GitHub OAuth callback"""
    logger.info(f"OAuth callback received - code: {'present' if code else 'missing'}, state: {state[:20] if state else 'missing'}...")
    
    # Verify state
    session_state = request.session.get("oauth_state")
    logger.info(f"Session state: {session_state[:20] if session_state else 'missing'}...")
    
    if not session_state or session_state != state:
        logger.error(f"State mismatch! Session: {session_state[:20] if session_state else 'None'}, Received: {state[:20] if state else 'None'}")
        raise HTTPException(status_code=400, detail="Invalid state parameter")
    
    if not code:
        logger.error("Authorization code not provided in callback")
        raise HTTPException(status_code=400, detail="Authorization code not provided")
    
    try:
        logger.info("Exchanging authorization code for access token...")
        # Exchange code for access token
        access_token = await get_access_token(code)
        logger.info("Access token obtained successfully")
        
        logger.info("Fetching user info from GitHub...")
        # Get user info
        user_info = await get_user_info(access_token)
        logger.info(f"User info retrieved: {user_info.get('login', 'unknown')}")
        
        # Store in session
        request.session["access_token"] = access_token
        request.session["user"] = {
            "login": user_info["login"],
            "name": user_info.get("name"),
            "avatar_url": user_info.get("avatar_url")
        }
        request.session.pop("oauth_state", None)
        logger.info(f"Session updated for user: {user_info['login']}")
        
        # Redirect to main page
        return RedirectResponse(url="/", status_code=303)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")


@router.get("/logout")
async def logout(request: Request):
    """Logout user"""
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)


@router.get("/user")
async def get_current_user(request: Request):
    """Get current authenticated user"""
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user

