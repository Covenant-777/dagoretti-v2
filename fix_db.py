"""
fix_db.py — Run this ONCE to clear stuck PIN change requests
Run: python fix_db.py
"""
import psycopg

DATABASE_URL = "postgresql://dagoretti_db_user:WwRfDK9joeJPF1GxUzYPPBrjvHj4rM8X@dpg-d91eqirsq97s738fr60g-a.oregon-postgres.render.com/dagoretti_db"

conn = psycopg.connect(DATABASE_URL)
c = conn.cursor()

# Check pending requests
c.execute("SELECT * FROM pinchangerequests WHERE status='pending'")
pending = c.fetchall()
print(f"Found {len(pending)} pending PIN change request(s)")

# Clear them
c.execute("UPDATE pinchangerequests SET status='rejected' WHERE status='pending'")
conn.commit()
print(f"Cleared {c.rowcount} stuck request(s)")

# Verify
c.execute("SELECT COUNT(*) FROM pinchangerequests WHERE status='pending'")
print(f"Remaining pending: {c.fetchone()[0]}")
conn.close()
print("Done! Bakers can now submit new PIN change requests.")
