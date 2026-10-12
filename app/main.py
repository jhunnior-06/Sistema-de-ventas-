from datetime import datetime, time
from decimal import Decimal
from pathlib import Path
from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db, init_db
from app.models import Product, Sale
from app.schemas import SaleCreate
from app.services import create_sale

BASE_DIR = Path(__file__).resolve().parent
app = FastAPI(title="Sistema de Ventas", version="1.0.0")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")
templates.env.filters["currency"] = lambda value: f"S/ {Decimal(value):,.2f}"

@app.on_event("startup")
def startup() -> None:
    init_db()

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    today_start = datetime.combine(datetime.utcnow().date(), time.min)
    sales_today = db.scalar(select(func.coalesce(func.sum(Sale.total), 0)).where(Sale.created_at >= today_start))
    low_stock = db.scalar(select(func.count(Product.id)).where(Product.active.is_(True), Product.stock <= Product.min_stock))
    product_count = db.scalar(select(func.count(Product.id)).where(Product.active.is_(True)))
    recent_sales = db.scalars(select(Sale).order_by(Sale.created_at.desc()).limit(8)).all()
    return templates.TemplateResponse("dashboard.html", {
        "request": request, "sales_today": sales_today, "low_stock": low_stock,
        "product_count": product_count, "recent_sales": recent_sales,
    })

@app.get("/productos", response_class=HTMLResponse)
def products_page(request: Request, db: Session = Depends(get_db)):
    products = db.scalars(select(Product).order_by(Product.active.desc(), Product.name)).all()
    return templates.TemplateResponse("products.html", {"request": request, "products": products})

@app.post("/productos")
def create_product(
    name: str = Form(...), sale_price: Decimal = Form(...), stock: int = Form(0),
    code: str | None = Form(None), description: str | None = Form(None),
    category: str | None = Form(None), cost_price: Decimal = Form(0),
    min_stock: int = Form(5), db: Session = Depends(get_db)
):
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
def toggle_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(404, "Producto no encontrado")
    product.active = not product.active
    db.commit()
    return RedirectResponse("/productos?ok=Estado actualizado", status_code=303)

@app.get("/ventas", response_class=HTMLResponse)
def sales_page(request: Request, db: Session = Depends(get_db)):
    products = db.scalars(select(Product).where(Product.active.is_(True), Product.stock > 0).order_by(Product.name)).all()
    return templates.TemplateResponse("sales.html", {"request": request, "products": products})

@app.post("/api/ventas")
def register_sale(payload: SaleCreate, db: Session = Depends(get_db)):
    try:
        sale = create_sale(db, payload)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return {"message": "Venta registrada correctamente", "invoice_number": sale.invoice_number, "total": float(sale.total)}

@app.get("/api/productos")
def product_api(db: Session = Depends(get_db)):
    products = db.scalars(select(Product).where(Product.active.is_(True), Product.stock > 0).order_by(Product.name)).all()
    return [{"id": p.id, "name": p.name, "sale_price": float(p.sale_price), "stock": p.stock} for p in products]

@app.get("/api/ventas-recientes")
def recent_sales_api(db: Session = Depends(get_db)):
    sales = db.scalars(select(Sale).options(selectinload(Sale.items)).order_by(Sale.created_at.desc()).limit(30)).all()
    return [{
        "invoice_number": sale.invoice_number, "customer_name": sale.customer_name,
        "payment_method": sale.payment_method, "total": float(sale.total),
        "created_at": sale.created_at.isoformat(),
        "items": [{"product": item.product_name, "quantity": item.quantity} for item in sale.items],
    } for sale in sales]
