# app/sync_client.py
import requests
from database import get_conn
from config import SERVER_BASE, API_TOKEN

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

def fetch_server_data():
    """
    Fetch latest tasks from server and update local DB incrementally.
    """
    try:
        resp = requests.get(f"{SERVER_BASE}/sync/download", headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        items = data.get("items", [])

        conn = get_conn()
        c = conn.cursor()
        for item in items:
            # Insert new or update existing based on uuid
            c.execute("""
                INSERT INTO items (uuid, name, qty, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(uuid) DO UPDATE SET
                    name = excluded.name,
                    qty = excluded.qty,
                    updated_at = excluded.updated_at
            """, (item["uuid"], item["name"], item["qty"], item["updated_at"]))
        conn.commit()
        conn.close()

        return {"status": "success", "count": len(items)}
    except Exception as e:
        return {"status": "error", "message": str(e)}

