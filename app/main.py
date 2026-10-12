import os
from datetime import datetime, time
from decimal import Decimal
from pathlib import Path

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload
from starlette.middleware.sessions import SessionMiddleware

from app.database import SessionLocal, get_db, init_db
from app.models import Product, Sale, User
from app.schemas import SaleCreate
from app.security import get_initial_admin, hash_password, verify_password
from app.services import create_sale

BASE_DIR = Path(__file__).resolve().parent
secret_key = os.getenv("SECRET_KEY")
if not secret_key and os.getenv("VERCEL"):
    raise RuntimeError("Configura SECRET_KEY en Vercel.")
secret_key = secret_key or "solo-para-desarrollo-local"

app = FastAPI(title="Sistema de Ventas", version="1.1.0")
app.add_middleware(SessionMiddleware, secret_key=secret_key, same_site="lax", https_only=bool(os.getenv("VERCEL")))
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")
templates.env.filters["currency"] = lambda value: f"S/ {Decimal(value):,.2f}"

def session_user(request: Request, db: Session) -> User | None:
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    user = db.get(User, user_id)
    if not user or not user.active:
        request.session.clear()
        return None
    return user

def login_redirect() -> RedirectResponse:
    return RedirectResponse("/login", status_code=303)

def admin_or_redirect(request: Request, db: Session) -> User | RedirectResponse:
    user = session_user(request, db)
    if not user:
        return login_redirect()
    if user.role != "admin":
        return RedirectResponse("/ventas", status_code=303)
    return user

def require_api_user(request: Request, db: Session) -> User:
    user = session_user(request, db)
    if not user:
        raise HTTPException(401, "Inicia sesión para continuar.")
    return user

def create_initial_admin() -> None:
    username, display_name, password = get_initial_admin()
    with SessionLocal() as db:
        if not db.scalar(select(User).where(User.username == username)):
            db.add(User(
                username=username,
                display_name=display_name,
                password_hash=hash_password(password),
                role="admin",
            ))
            db.commit()

@app.on_event("startup")
def startup() -> None:
    init_db()
    create_initial_admin()

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request, db: Session = Depends(get_db)):
    user = session_user(request, db)
    if user:
        return RedirectResponse("/" if user.role == "admin" else "/ventas", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login(
    request: Request, username: str = Form(...), password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.scalar(select(User).where(User.username == username.strip().lower()))
    if not user or not user.active or not verify_password(password, user.password_hash):
        return RedirectResponse("/login?error=Credenciales incorrectas", status_code=303)
    request.session.clear()
    request.session["user_id"] = user.id
    return RedirectResponse("/" if user.role == "admin" else "/ventas", status_code=303)

@app.post("/salir")
def logout(request: Request):
    request.session.clear()
    return login_redirect()

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    current_user = admin_or_redirect(request, db)
    if isinstance(current_user, RedirectResponse):
        return current_user
    today_start = datetime.combine(datetime.utcnow().date(), time.min)
    sales_today = db.scalar(select(func.coalesce(func.sum(Sale.total), 0)).where(Sale.created_at >= today_start))
    low_stock = db.scalar(select(func.count(Product.id)).where(Product.active.is_(True), Product.stock <= Product.min_stock))
    product_count = db.scalar(select(func.count(Product.id)).where(Product.active.is_(True)))
    recent_sales = db.scalars(select(Sale).order_by(Sale.created_at.desc()).limit(8)).all()
    return templates.TemplateResponse("dashboard.html", {
        "request": request, "current_user": current_user, "sales_today": sales_today,
        "low_stock": low_stock, "product_count": product_count, "recent_sales": recent_sales,
    })

@app.get("/productos", response_class=HTMLResponse)
def products_page(request: Request, db: Session = Depends(get_db)):
    current_user = admin_or_redirect(request, db)
    if isinstance(current_user, RedirectResponse):
        return current_user
    products = db.scalars(select(Product).order_by(Product.active.desc(), Product.name)).all()
    return templates.TemplateResponse("products.html", {
        "request": request, "current_user": current_user, "products": products,
    })

@app.post("/productos")
def create_product(
    request: Request, name: str = Form(...), sale_price: Decimal = Form(...), stock: int = Form(0),
    code: str | None = Form(None), description: str | None = Form(None),
    category: str | None = Form(None), cost_price: Decimal = Form(0),
    min_stock: int = Form(5), db: Session = Depends(get_db)
):
    current_user = admin_or_redirect(request, db)
    if isinstance(current_user, RedirectResponse):
        return current_user
    if sale_price < 0 or cost_price < 0 or stock < 0 or min_stock < 0:
        return RedirectResponse("/productos?error=Los valores no pueden ser negativos", status_code=303)
    if code and db.scalar(select(Product).where(Product.code == code.strip())):
        return RedirectResponse("/productos?error=El código ya está registrado", status_code=303)
    db.add(Product(name=name.strip(), code=code.strip() if code else None,
        description=description.strip() if description else None,
        category=category.strip() if category else None, cost_price=cost_price,
        sale_price=sale_price, stock=stock, min_stock=min_stock))
    db.commit()
    return RedirectResponse("/productos?ok=Producto guardado", status_code=303)

@app.post("/productos/{product_id}/estado")
def toggle_product(product_id: int, request: Request, db: Session = Depends(get_db)):
    current_user = admin_or_redirect(request, db)
    if isinstance(current_user, RedirectResponse):
        return current_user
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(404, "Producto no encontrado")
    product.active = not product.active
    db.commit()
    return RedirectResponse("/productos?ok=Estado actualizado", status_code=303)

@app.get("/usuarios", response_class=HTMLResponse)
def users_page(request: Request, db: Session = Depends(get_db)):
    current_user = admin_or_redirect(request, db)
    if isinstance(current_user, RedirectResponse):
        return current_user
    users = db.scalars(select(User).order_by(User.role, User.display_name)).all()
    return templates.TemplateResponse("users.html", {
        "request": request, "current_user": current_user, "users": users,
    })

@app.post("/usuarios")
def create_user(
    request: Request, display_name: str = Form(...), username: str = Form(...),
    password: str = Form(...), role: str = Form("user"), db: Session = Depends(get_db)
):
    current_user = admin_or_redirect(request, db)
    if isinstance(current_user, RedirectResponse):
        return current_user
    username = username.strip().lower()
    if len(username) < 3 or not username.replace("_", "").replace(".", "").isalnum():
        return RedirectResponse("/usuarios?error=Usuario inválido", status_code=303)
    if len(password) < 8:
        return RedirectResponse("/usuarios?error=La contraseña debe tener al menos 8 caracteres", status_code=303)
    if role not in {"admin", "user"}:
        return RedirectResponse("/usuarios?error=Rol inválido", status_code=303)
    if db.scalar(select(User).where(User.username == username)):
        return RedirectResponse("/usuarios?error=El usuario ya existe", status_code=303)
    db.add(User(display_name=display_name.strip(), username=username,
                password_hash=hash_password(password), role=role))
    db.commit()
    return RedirectResponse("/usuarios?ok=Usuario creado", status_code=303)

@app.post("/usuarios/{user_id}/estado")
def toggle_user(user_id: int, request: Request, db: Session = Depends(get_db)):
    current_user = admin_or_redirect(request, db)
    if isinstance(current_user, RedirectResponse):
        return current_user
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "Usuario no encontrado")
    if user.id == current_user.id:
        return RedirectResponse("/usuarios?error=No puedes desactivar tu propia cuenta", status_code=303)
    user.active = not user.active
    db.commit()
    return RedirectResponse("/usuarios?ok=Estado actualizado", status_code=303)

@app.get("/ventas", response_class=HTMLResponse)
def sales_page(request: Request, db: Session = Depends(get_db)):
    current_user = session_user(request, db)
    if not current_user:
        return login_redirect()
    products = db.scalars(select(Product).where(Product.active.is_(True), Product.stock > 0).order_by(Product.name)).all()
    return templates.TemplateResponse("sales.html", {
        "request": request, "current_user": current_user, "products": products,
    })

@app.post("/api/ventas")
def register_sale(request: Request, payload: SaleCreate, db: Session = Depends(get_db)):
    current_user = require_api_user(request, db)
    try:
        sale = create_sale(db, payload, current_user.display_name)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return {"message": "Venta registrada correctamente", "invoice_number": sale.invoice_number, "total": float(sale.total)}

@app.get("/api/productos")
def product_api(request: Request, db: Session = Depends(get_db)):
    require_api_user(request, db)
    products = db.scalars(select(Product).where(Product.active.is_(True), Product.stock > 0).order_by(Product.name)).all()
    return [{"id": p.id, "name": p.name, "sale_price": float(p.sale_price), "stock": p.stock} for p in products]

@app.get("/api/ventas-recientes")
def recent_sales_api(request: Request, db: Session = Depends(get_db)):
    current_user = require_api_user(request, db)
    if current_user.role != "admin":
        raise HTTPException(403, "Solo el administrador puede consultar el historial.")
    sales = db.scalars(select(Sale).options(selectinload(Sale.items)).order_by(Sale.created_at.desc()).limit(30)).all()
    return [{
        "invoice_number": sale.invoice_number, "customer_name": sale.customer_name,
        "seller_name": sale.seller_name, "payment_method": sale.payment_method,
        "total": float(sale.total), "created_at": sale.created_at.isoformat(),
        "items": [{"product": item.product_name, "quantity": item.quantity} for item in sale.items],
    } for sale in sales]
