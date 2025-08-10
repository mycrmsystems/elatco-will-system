import os
from fastapi import Request, HTTPException

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "change-me")

SESSION_ADMIN_KEY = "is_admin"

def set_admin_session(request: Request, email: str, password: str) -> bool:
    if email.strip().lower() == ADMIN_EMAIL.strip().lower() and password == ADMIN_PASSWORD:
        request.session[SESSION_ADMIN_KEY] = True
        return True
    return False

def is_admin(request: Request) -> bool:
    return bool(request.session.get(SESSION_ADMIN_KEY))

def require_admin(request: Request):
    if not is_admin(request):
        raise HTTPException(status_code=401, detail="Admin login required")

def clear_admin_session(request: Request):
    request.session.pop(SESSION_ADMIN_KEY, None)
