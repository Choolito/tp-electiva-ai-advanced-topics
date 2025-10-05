# init_db.py
from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parent
db_dir = BASE_DIR / "db"
db_path = db_dir / "hotel.db"
schema_path = db_dir / "schema.sql"
seed_path = db_dir / "seed.sql"

assert schema_path.exists(), f"No existe {schema_path}"
assert seed_path.exists(), f"No existe {seed_path}"

db_dir.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(db_path)
try:
    with open(schema_path, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    with open(seed_path, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    print(f"OK: creada/actualizada {db_path}")
finally:
    conn.commit()
    conn.close()
