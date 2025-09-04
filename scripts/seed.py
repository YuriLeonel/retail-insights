import pandas as pd
from decimal import Decimal
from pathlib import Path
from typing import Dict, Optional

from app.database import SessionLocal, init_db
from app.models import Customer, Product, Order, OrderItem


def decimal_from_value(value) -> Optional[Decimal]:
    if pd.isna(value):
        return None
    try:
        return Decimal(str(value))
    except Exception:
        return None


def int_from_value(value) -> Optional[int]:
    if pd.isna(value):
        return None
    try:
        return int(value)
    except Exception:
        return None


def seed_from_excel() -> None:
    init_db()

    excel_path = Path(__file__).resolve().parents[1] / "data" / "Online Retail.xlsx"
    df = pd.read_excel(str(excel_path))

    # Basic cleaning
    df = df.dropna(subset=["InvoiceNo", "StockCode"])  # ensure required identifiers
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")

    session = SessionLocal()

    # Simple caches to avoid duplicate lookups/inserts
    customer_cache: Dict[int, Customer] = {}
    product_cache: Dict[str, Product] = {}
    order_cache: Dict[str, Order] = {}

    rows_since_commit = 0
    BATCH_SIZE = 1000

    try:
        for _, row in df.iterrows():
            invoice_no = str(row["InvoiceNo"]).strip()
            stock_code = str(row["StockCode"]).strip()
            description = None if pd.isna(row.get("Description")) else str(row.get("Description"))
            quantity = int_from_value(row.get("Quantity")) or 0
            unit_price = decimal_from_value(row.get("UnitPrice")) or Decimal("0")
            customer_id_val = int_from_value(row.get("CustomerID"))
            country = None if pd.isna(row.get("Country")) else str(row.get("Country"))
            invoice_date = row.get("InvoiceDate")  # pandas Timestamp or NaT

            # Customer (optional)
            customer_obj: Optional[Customer] = None
            if customer_id_val is not None:
                customer_obj = customer_cache.get(customer_id_val)
                if customer_obj is None:
                    customer_obj = Customer(
                        customer_id=customer_id_val,
                        customer_name=None,  # not available in dataset
                        country=country,
                    )
                    session.add(customer_obj)
                    customer_cache[customer_id_val] = customer_obj

            # Product
            product_obj = product_cache.get(stock_code)
            if product_obj is None:
                product_obj = Product(
                    stock_code=stock_code,
                    description=description,
                )
                session.add(product_obj)
                product_cache[stock_code] = product_obj

            # Order
            order_obj = order_cache.get(invoice_no)
            if order_obj is None:
                order_obj = Order(
                    invoice_no=invoice_no,
                    customer_id=customer_obj.customer_id if customer_obj else None,
                    invoice_date=invoice_date.to_pydatetime() if hasattr(invoice_date, "to_pydatetime") else invoice_date,
                    country=country,
                )
                session.add(order_obj)
                order_cache[invoice_no] = order_obj

            # Order item
            order_item = OrderItem(
                order=order_obj,
                product=product_obj,
                quantity=quantity,
                unit_price=unit_price,
            )
            session.add(order_item)

            rows_since_commit += 1
            if rows_since_commit >= BATCH_SIZE:
                session.commit()
                rows_since_commit = 0

        # final commit
        if rows_since_commit > 0:
            session.commit()
        print("Seeding completed ✅")
    except Exception as exc:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_from_excel()
