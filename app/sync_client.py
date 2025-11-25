# app/sync_client.py
import requests
import json
from database import get_conn, init_db

from config import SERVER_BASE, API_TOKEN

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

def send_local_changes():
    """Send all local items to server"""
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT uuid, name, qty, updated_at FROM items")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()

    if not rows:
        return {"status": "empty", "message": "No local items to sync"}

    payload = {"items": rows}
    try:
        resp = requests.post(f"{SERVER_BASE}/sync/upload", json=payload, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

def fetch_server_data():
    """Fetch all items from server and overwrite local DB"""
    try:
        resp = requests.get(f"{SERVER_BASE}/sync/download", headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        items = data.get("items", [])

        # Overwrite local DB
        conn = get_conn()
        c = conn.cursor()
        c.execute("DELETE FROM items")
        for item in items:
            c.execute(
                "INSERT INTO items(uuid, name, qty, updated_at) VALUES (?, ?, ?, ?)",
                (item["uuid"], item["name"], item["qty"], item["updated_at"])
            )
        conn.commit()
        conn.close()
        return {"status": "success", "count": len(items)}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def sync_all():
    """Perform full sync: send local changes → fetch server data"""
    upload_result = send_local_changes()
    if upload_result.get("status") == "error":
        return upload_result

    download_result = fetch_server_data()
    return download_result
