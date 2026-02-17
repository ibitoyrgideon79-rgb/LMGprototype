from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from models import Product, User
from auth import create_access_token, require_admin, verify_password

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory="templates")


@router.get("/login")
def admin_login_page(request: Request):
    return templates.TemplateResponse("admin/login.html", {"request": request, "error": None})


@router.post("/login")
def admin_login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == email, User.is_admin.is_(True)).first()
    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            "admin/login.html",
            {"request": request, "error": "Invalid admin credentials"},
            status_code=400,
        )

    token = create_access_token({"sub": str(user.id)})
    response = RedirectResponse(url="/admin/dashboard", status_code=302)
    response.set_cookie("access_token", token, httponly=True, samesite="lax")
    return response


@router.get("/dashboard")
def admin_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    users = db.query(User).order_by(User.created_at.desc()).all()
    products = db.query(Product).order_by(Product.id.desc()).limit(5).all()
    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "current_user": current_user,
            "users": users,
            "products": products,
        },
    )


@router.get("/products")
def admin_products(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    products = db.query(Product).order_by(Product.id.desc()).all()
    return templates.TemplateResponse(
        "admin/products.html",
        {
            "request": request,
            "current_user": current_user,
            "products": products,
            "editing": None,
        },
    )


@router.post("/products/add")
def admin_products_add(
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    category: str = Form(...),
    image_url: str = Form(...),
    stock: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    product = Product(
        name=name,
        description=description,
        price=price,
        category=category,
        image_url=image_url,
        stock=stock,
    )
    db.add(product)
    db.commit()
    return RedirectResponse(url="/admin/products", status_code=302)


@router.post("/products/{product_id}/edit")
def admin_products_edit(
    product_id: int,
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    category: str = Form(...),
    image_url: str = Form(...),
    stock: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if product:
        product.name = name
        product.description = description
        product.price = price
        product.category = category
        product.image_url = image_url
        product.stock = stock
        db.commit()
    return RedirectResponse(url="/admin/products", status_code=302)


@router.post("/products/{product_id}/delete")
def admin_products_delete(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if product:
        db.delete(product)
        db.commit()
    return RedirectResponse(url="/admin/products", status_code=302)
