from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from models import Item
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.sql import func
import uuid

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# -----------------------
# FastAPI instance
# -----------------------
app = FastAPI(title="Meeting Task Admin API")

# -----------------------
# CORS (allow your client app)
# -----------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # replace with your frontend URL if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------
# Download endpoint for clients
# -----------------------
@app.get("/sync/download")
def download_items(db: Session = Depends(get_db)):
    """Return all items to client apps"""
    items = db.query(Item).all()
    result = []
    for i in items:
        result.append({
            "uuid": i.uuid,
            "name": i.name,
            "qty": i.qty,
            "updated_at": i.updated_at
        })
    return {"items": result}


# -----------------------
# Admin add endpoint (optional)
# -----------------------
@app.post("/admin/add")
def add_item(name: str, qty: int, db: Session = Depends(get_db)):
    """Admin can add a new task/item"""
    new_item = Item(
        uuid=str(uuid.uuid4()),
        name=name,
        qty=qty,
        updated_at=int(func.now())
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return {
        "status": "success",
        "item": {
            "uuid": new_item.uuid,
            "name": new_item.name,
            "qty": new_item.qty,
            "updated_at": new_item.updated_at
        }
    }
