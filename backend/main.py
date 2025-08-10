import os
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.status import HTTP_303_SEE_OTHER

from .database import get_db, init_db
from .models import Will
from .pdf import build_will_pdf
from .security import require_admin, set_admin_session, clear_admin_session, is_admin
from .trust_clauses import TRUST_TYPES, make_trust_clause

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

DATA_DIR = Path(os.getenv("DATA_DIR", "/data"))
PDF_DIR = DATA_DIR / "pdfs"

app = FastAPI(title="ELATCO Will & Trust System")

# Session secret
SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY, same_site="lax")

# Static & templates
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

@app.on_event("startup")
def on_startup():
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    init_db()

# ---------- Public ----------
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "trust_types": TRUST_TYPES, "admin": is_admin(request)}
    )

@app.get("/client/start", response_class=HTMLResponse)
async def client_start(request: Request):
    return templates.TemplateResponse("client_will_form.html", {"request": request, "trust_types": TRUST_TYPES})

@app.post("/client/submit")
async def client_submit(
    request: Request,
    db = Depends(get_db),
    full_name: str = Form(...),
    dob: str = Form(""),
    address: str = Form(""),
    executors: str = Form(""),
    gifts: str = Form(""),
    residuary: str = Form("To my residuary beneficiaries equally."),
    trust_discretionary: str = Form(None),
    trust_life_interest: str = Form(None),
    trust_property: str = Form(None),
):
    # Map the simple checkboxes to one trust type (you can enhance later)
    trust_type = "None"
    if trust_discretionary: trust_type = "Discretionary Trust"
    if trust_life_interest: trust_type = "Life Interest Trust"
    if trust_property: trust_type = "Property Protection Trust"

    trust_text = make_trust_clause(
        trust_type=trust_type,
        trustees="the Trustees named in this Will",
        beneficiaries="the Beneficiaries named in this Will",
        age_of_access="18",
        special=""
    )

    will = Will(
        client_name=full_name.strip(),
        dob=dob.strip(),
        address=address.strip(),
        executors=executors.strip(),
        gifts=gifts.strip(),
        residuary=residuary.strip(),
        trust_type=trust_type,
        trust_text=trust_text,
        created_at=datetime.utcnow(),
    )

    db.add(will)
    db.commit()
    db.refresh(will)

    # Generate & store PDF bytes
    pdf_bytes = build_will_pdf(will)
    filename = f"will_{will.id}.pdf"
    file_path = PDF_DIR / filename
    with open(file_path, "wb") as f:
        f.write(pdf_bytes)

    will.pdf_filename = filename
    db.commit()

    return RedirectResponse(url=f"/admin/will/{will.id}", status_code=HTTP_303_SEE_OTHER)

# ---------- Admin ----------
@app.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})

@app.post("/admin/login")
async def admin_login(request: Request, email: str = Form(...), password: str = Form(...)):
    if set_admin_session(request, email, password):
        return RedirectResponse("/admin/dashboard", status_code=HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("admin_login.html", {"request": request, "error": "Invalid credentials"})

@app.get("/admin/logout")
async def admin_logout(request: Request):
    clear_admin_session(request)
    return RedirectResponse("/", status_code=HTTP_303_SEE_OTHER)

@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db = Depends(get_db)):
    require_admin(request)
    wills = db.query(Will).order_by(Will.created_at.desc()).all()
    return templates.TemplateResponse("admin_dashboard.html", {"request": request, "wills": wills})

@app.get("/admin/will/{will_id}", response_class=HTMLResponse)
async def admin_will_detail(request: Request, will_id: int, db = Depends(get_db)):
    require_admin(request)
    will = db.query(Will).get(will_id)
    if not will:
        raise HTTPException(status_code=404, detail="Will not found")
    return templates.TemplateResponse("will_detail.html", {"request": request, "will": will})

@app.get("/admin/will/{will_id}/download")
async def download_will_pdf(request: Request, will_id: int, db = Depends(get_db)):
    require_admin(request)
    will = db.query(Will).get(will_id)
    if not will or not will.pdf_filename:
        raise HTTPException(status_code=404, detail="PDF not found")
    file_path = PDF_DIR / will.pdf_filename
    if not file_path.exists():
        # Rebuild if missing
        pdf_bytes = build_will_pdf(will)
        with open(file_path, "wb") as f:
            f.write(pdf_bytes)
    return StreamingResponse(
        open(file_path, "rb"),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={will.pdf_filename}"}
    )
