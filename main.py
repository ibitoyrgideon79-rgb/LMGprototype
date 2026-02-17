from datetime import datetime
from fastapi import Depends, FastAPI, Form, Request, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from auth import create_access_token, get_current_user, get_current_user_optional, get_password_hash, verify_password
from database import Base, SessionLocal, engine, get_db
from models import CartItem, Product, Review, User
from admin import router as admin_router

app = FastAPI(title="Luminous Glow Cosmetics")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

templates.env.globals["now"] = datetime.utcnow


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        ensure_admin_user(db)
        seed_products_and_reviews(db)
    finally:
        db.close()


def ensure_admin_user(db: Session) -> None:
    admin = db.query(User).filter(User.email == "admin@luminous.com").first()
    if admin:
        if not admin.is_admin:
            admin.is_admin = True
            db.commit()
        return
    admin = User(
        username="Admin",
        email="admin@luminous.com",
        password_hash=get_password_hash("admin123"),
        is_admin=True,
    )
    db.add(admin)
    db.commit()


def seed_products_and_reviews(db: Session) -> None:
    if db.query(Product).count() == 0:
        products = [
            Product(
                name="Rose Glow Perfume",
                description="A romantic floral fragrance with a luminous finish.",
                price=49999.00,
                category="Perfumes",
                image_url="/static/images/rose-glow.svg",
                stock=25,
            ),
            Product(
                name="Luminous Lip Gloss",
                description="High-shine gloss with a glassy, hydrating feel.",
                price=19999.00,
                category="Lip Gloss",
                image_url="/static/images/lip-gloss.svg",
                stock=60,
            ),
            Product(
                name="Pink Lip Balm",
                description="Soft, cushiony balm for all-day comfort.",
                price=14999.00,
                category="Lip Care",
                image_url="/static/images/lip-balm.svg",
                stock=80,
            ),
            Product(
                name="Radiance Face Cream",
                description="Silky cream that leaves skin dewy and radiant.",
                price=39999.00,
                category="Creams",
                image_url="/static/images/face-cream.svg",
                stock=40,
            ),
            Product(
                name="Silk Hair Serum",
                description="Gloss-boosting serum with a smooth finish.",
                price=29999.00,
                category="Hair Products",
                image_url="/static/images/hair-serum.svg",
                stock=35,
            ),
            Product(
                name="Glow Setting Spray",
                description="Mist that locks makeup with a soft glow.",
                price=24999.00,
                category="Makeup",
                image_url="/static/images/setting-spray.svg",
                stock=50,
            ),
        ]
        db.add_all(products)
        db.commit()

    if db.query(Review).count() == 0:
        reviews = [
            Review(
                user_name="Sarah M.",
                rating=5,
                comment="Absolutely love the lip gloss! So glossy and long-lasting",
            ),
            Review(
                user_name="Jessica R.",
                rating=4,
                comment="The perfume smells amazing, subtle and elegant",
            ),
            Review(
                user_name="Emily K.",
                rating=5,
                comment="Best skincare products I've ever used. My skin feels amazing",
            ),
            Review(
                user_name="Michael T.",
                rating=4,
                comment="Great customer service and quick delivery",
            ),
            Review(
                user_name="Amanda P.",
                rating=5,
                comment="The cream transformed my skin, highly recommend",
            ),
        ]
        db.add_all(reviews)
        db.commit()


@app.get("/")
def index(request: Request, db: Session = Depends(get_db)):
    products = db.query(Product).limit(6).all()
    reviews = db.query(Review).order_by(Review.created_at.desc()).limit(5).all()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "products": products,
            "reviews": reviews,
            "current_user": get_current_user_optional(request, db),
        },
    )


@app.get("/products")
def product_list(request: Request, category: str | None = None, db: Session = Depends(get_db)):
    query = db.query(Product)
    if category:
        query = query.filter(Product.category == category)
    products = query.order_by(Product.id.desc()).all()
    categories = [row[0] for row in db.query(Product.category).distinct().all()]
    return templates.TemplateResponse(
        "products.html",
        {
            "request": request,
            "products": products,
            "categories": categories,
            "selected_category": category,
            "current_user": get_current_user_optional(request, db),
        },
    )


@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "error": None})


@app.post("/register")
def register_user(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Email already registered"},
            status_code=400,
        )
    user = User(
        username=username,
        email=email,
        password_hash=get_password_hash(password),
        is_admin=False,
    )
    db.add(user)
    db.commit()
    token = create_access_token({"sub": str(user.id)})
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie("access_token", token, httponly=True, samesite="lax")
    return response


@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@app.post("/login")
def login_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid credentials"},
            status_code=400,
        )
    token = create_access_token({"sub": str(user.id)})
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie("access_token", token, httponly=True, samesite="lax")
    return response


@app.post("/logout")
def logout_user():
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("access_token")
    return response


@app.get("/cart")
def view_cart(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user_optional(request, db)
    items = []
    if current_user:
        items = (
            db.query(CartItem)
            .filter(CartItem.user_id == current_user.id)
            .join(Product)
            .all()
        )
    total = sum(item.product.price * item.quantity for item in items)
    return templates.TemplateResponse(
        "cart.html",
        {
            "request": request,
            "items": items,
            "total": total,
            "current_user": current_user,
        },
    )


@app.post("/cart/add/{product_id}")
def add_to_cart(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = (
        db.query(CartItem)
        .filter(CartItem.user_id == current_user.id, CartItem.product_id == product_id)
        .first()
    )
    if item:
        item.quantity += 1
    else:
        item = CartItem(user_id=current_user.id, product_id=product_id, quantity=1)
        db.add(item)
    db.commit()
    return RedirectResponse(url="/cart", status_code=302)


@app.post("/cart/update/{item_id}")
def update_cart_item(
    item_id: int,
    quantity: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = (
        db.query(CartItem)
        .filter(CartItem.id == item_id, CartItem.user_id == current_user.id)
        .first()
    )
    if item:
        item.quantity = max(1, quantity)
        db.commit()
    return RedirectResponse(url="/cart", status_code=302)


@app.post("/cart/remove/{item_id}")
def remove_cart_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = (
        db.query(CartItem)
        .filter(CartItem.id == item_id, CartItem.user_id == current_user.id)
        .first()
    )
    if item:
        db.delete(item)
        db.commit()
    return RedirectResponse(url="/cart", status_code=302)


app.include_router(admin_router)
