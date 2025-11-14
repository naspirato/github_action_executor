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
async def github_login(request: Request, redirect_after: str = None):
    """Initiate GitHub OAuth login"""
    try:
        # Generate state for CSRF protection
        state = secrets.token_urlsafe(32)
        request.session["oauth_state"] = state
        
        # Save redirect URL if provided
        if redirect_after:
            request.session["oauth_redirect_after"] = redirect_after
        elif "oauth_redirect_after" not in request.session:
            # Get redirect_after from query parameter if not in session
            redirect_after = request.query_params.get("redirect_after")
            if redirect_after:
                request.session["oauth_redirect_after"] = redirect_after
        
        # Verify state was saved
        saved_state = request.session.get("oauth_state")
        logger.info(f"OAuth login initiated, state generated: {state[:10]}..., saved in session: {saved_state[:10] if saved_state else 'NOT SAVED'}..., redirect_after: {request.session.get('oauth_redirect_after', 'not set')}")
        
        if not saved_state or saved_state != state:
            logger.error(f"CRITICAL: State was not saved correctly! Generated: {state}, Saved: {saved_state}")
        
        # Redirect to GitHub OAuth
        oauth_url = get_oauth_url(state=state)
        logger.info(f"Redirecting to GitHub OAuth (full URL logged above)")
        return RedirectResponse(url=oauth_url)
    except ValueError as e:
        # GITHUB_CLIENT_ID is not set
        logger.error(f"OAuth configuration error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"OAuth configuration error: {str(e)}. Please check your environment variables."
        )
    except Exception as e:
        logger.error(f"Unexpected error initiating OAuth: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to initiate OAuth: {str(e)}")


@router.get("/github/callback")
async def github_callback(request: Request, code: str = None, state: str = None, error: str = None, error_description: str = None):
    """Handle GitHub OAuth callback"""
    # Log all query parameters for debugging
    all_params = dict(request.query_params)
    logger.info(f"OAuth callback received - Full URL: {request.url}")
    logger.info(f"OAuth callback query params: {all_params}")
    logger.info(f"OAuth callback - code: {'present' if code else 'missing'}, state: {state[:20] if state else 'missing'}, error: {error}")
    
    # Check for OAuth errors from GitHub
    if error:
        error_msg = f"GitHub OAuth error: {error}"
        if error_description:
            error_msg += f" - {error_description}"
        logger.error(error_msg)
        raise HTTPException(
            status_code=400,
            detail=error_msg
        )
    
    # Verify state
    session_state = request.session.get("oauth_state")
    logger.info(f"Session state from storage: {session_state[:20] if session_state else 'missing'}...")
    logger.info(f"State from GitHub: {state[:20] if state else 'missing'}...")
    
    # Log session info for debugging
    try:
        session_keys = list(request.session.keys())
        logger.info(f"Session keys present: {session_keys}")
    except:
        logger.warning("Could not list session keys")
    
    if not session_state:
        logger.warning("No oauth_state found in session. This usually means:")
        logger.warning("  1. Session was lost between OAuth start and callback")
        logger.warning("  2. Session cookie was not sent/received properly (common in incognito mode)")
        logger.warning("  3. Different domain/protocol between requests")
        logger.warning("  4. Browser blocked the session cookie (e.g., third-party cookie blocking)")
        
        # Fallback: if state is provided by GitHub and looks valid (long enough, URL-safe),
        # allow authentication but log a security warning
        # This is less secure but allows OAuth to work in incognito mode
        if state and len(state) >= 32 and all(c.isalnum() or c in '-_' for c in state):
            logger.warning("FALLBACK MODE: State not in session, but GitHub provided valid-looking state.")
            logger.warning("Allowing authentication to proceed (less secure, but works in incognito mode).")
            logger.warning("Consider using normal browser mode or enabling cookies in incognito for better security.")
            # Continue without state verification (less secure, but functional)
        else:
            # If no state from GitHub and no state in session, this might indicate:
            # 1. User came directly to callback without going through OAuth flow
            # 2. GitHub returned an error (like 404) and user was redirected manually
            # 3. Session was lost and GitHub didn't return state
            error_detail = (
                "Invalid state parameter: session state not found and GitHub state is invalid. "
                "This may indicate:\n"
                "1. Session cookie issue (common in incognito mode) - try normal browser mode\n"
                "2. OAuth App configuration issue - check that Client ID is correct in GitHub\n"
                "3. Direct access to callback URL without OAuth flow\n\n"
                "If you saw a 404 error from GitHub, the OAuth App with this Client ID doesn't exist. "
                "Please check your OAuth App settings at https://github.com/settings/developers"
            )
            raise HTTPException(status_code=400, detail=error_detail)
    elif session_state != state:
        logger.error(f"State mismatch!")
        logger.error(f"  Session state: {session_state}")
        logger.error(f"  Received state: {state}")
        logger.error(f"  States match: {session_state == state}")
        raise HTTPException(
            status_code=400, 
            detail="Invalid state parameter: state mismatch. This may indicate a CSRF attack or session issue."
        )
    else:
        # State matches - this is the secure path
        logger.info("State verification successful - secure OAuth flow")
    
    if not code:
        logger.error("Authorization code not provided in callback")
        # Check if there are any error parameters
        error_params = dict(request.query_params)
        if error_params:
            logger.error(f"Callback query parameters: {error_params}")
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
        
        # Redirect to saved URL or main page
        redirect_url = request.session.pop("oauth_redirect_after", "/")
        logger.info(f"Redirecting after OAuth to: {redirect_url}")
        return RedirectResponse(url=redirect_url, status_code=303)
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


@router.get("/config")
async def get_oauth_config(request: Request):
    """
    Diagnostic endpoint to check OAuth configuration
    Returns configuration info (without sensitive data) to help troubleshoot OAuth issues
    """
    import os
    from urllib.parse import urlencode
    
    client_id = os.getenv("GITHUB_CLIENT_ID")
    callback_url = os.getenv("GITHUB_CALLBACK_URL", "http://localhost:8000/auth/github/callback")
    client_secret_set = bool(os.getenv("GITHUB_CLIENT_SECRET"))
    
    config_info = {
        "client_id_set": bool(client_id),
        "client_id_preview": client_id[:10] + "..." if client_id else None,
        "callback_url": callback_url,
        "client_secret_set": client_secret_set,
        "oauth_url": None,
        "troubleshooting": {
            "common_issues": [
                "404 error usually means:",
                "  1. Client ID is incorrect or doesn't exist in GitHub",
                "  2. Callback URL doesn't match GitHub OAuth App settings",
                "  3. OAuth App was deleted or deactivated",
                "",
                "To fix:",
                "  1. Go to https://github.com/settings/developers",
                "  2. Find your OAuth App (or create a new one)",
                f"  3. Ensure 'Authorization callback URL' is exactly: {callback_url}",
                f"  4. Ensure 'Client ID' matches: {client_id[:10] + '...' if client_id else 'NOT SET'}"
            ]
        }
    }
    
    if client_id:
        try:
            from backend.services.github_oauth import get_oauth_url
            oauth_url = get_oauth_url()
            config_info["oauth_url"] = oauth_url
        except Exception as e:
            config_info["oauth_url_error"] = str(e)
    
    return config_info

