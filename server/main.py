# server/main.py
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from models import Item
from fastapi.middleware.cors import CORSMiddleware

# Create tables if they don’t exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Meeting Task Admin API")

# Allow CORS for your client apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or limit to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# Optional: admin can add/update items via API
@app.post("/admin/add")
def add_item(name: str, qty: int, db: Session = Depends(get_db)):
    import uuid
    new_item = Item(
        uuid=str(uuid.uuid4()),
        name=name,
        qty=qty,
        updated_at=int(func.now())
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return {"status": "success", "item": {
        "uuid": new_item.uuid,
        "name": new_item.name,
        "qty": new_item.qty
    }}
