from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import Product, Sale, SaleItem
from app.schemas import SaleCreate

MONEY = Decimal("0.01")

def money(value: Decimal) -> Decimal:
    return value.quantize(MONEY, rounding=ROUND_HALF_UP)

def create_sale(db: Session, payload: SaleCreate, seller_name: str) -> Sale:
    product_ids = [line.product_id for line in payload.items]
    products = {
        product.id: product
        for product in db.scalars(
            select(Product).where(Product.id.in_(product_ids), Product.active.is_(True))
        ).all()
    }
    if len(products) != len(set(product_ids)):
        raise ValueError("Uno o más productos no existen o están inactivos.")

    subtotal = Decimal("0")
    prepared_items: list[tuple[Product, int, Decimal]] = []
    for line in payload.items:
        product = products[line.product_id]
        if product.stock < line.quantity:
            raise ValueError(f"Stock insuficiente para: {product.name}.")
        line_total = money(Decimal(product.sale_price) * line.quantity)
        subtotal += line_total
        prepared_items.append((product, line.quantity, line_total))

    subtotal = money(subtotal)
    discount = money(Decimal(payload.discount))
    if discount > subtotal:
        raise ValueError("El descuento no puede superar el subtotal.")

    sale = Sale(
        invoice_number=f"V-{datetime.utcnow():%Y%m%d%H%M%S%f}",
        customer_name=payload.customer_name or None,
        seller_name=seller_name,
        payment_method=payload.payment_method,
        subtotal=subtotal,
        discount=discount,
        total=money(subtotal - discount),
    )
    db.add(sale)
    db.flush()

    for product, quantity, line_total in prepared_items:
        product.stock -= quantity
        db.add(SaleItem(
            sale_id=sale.id, product_id=product.id, product_name=product.name,
            quantity=quantity, unit_price=product.sale_price, line_total=line_total,
        ))

    db.commit()
    db.refresh(sale)
    return sale
