"""
demo_setup.py — Dagoretti Kitchen Incubator
Run this BEFORE your presentation to load clean sample data.
Uses 6-digit PINs (1,000,000 combinations)
"""
import sqlite3, hashlib, os, random
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "dagoretti.db")

def hash_pin(pin): return hashlib.sha256(pin.encode()).hexdigest()

def reset_and_seed():
    print("\n🍰 Dagoretti Kitchen Incubator — Demo Setup")
    print("=" * 50)

    # Delete old DB files
    for suffix in ["", "-wal", "-shm"]:
        p = DB_PATH + suffix if suffix else DB_PATH
        if os.path.exists(p): os.remove(p)
    print("✓ Old database cleared")

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS Bakers (
        BakerID INTEGER PRIMARY KEY AUTOINCREMENT,
        FullName TEXT NOT NULL, PIN_Hash TEXT NOT NULL,
        HourlyRate REAL NOT NULL DEFAULT 50.0,
        IsActive INTEGER NOT NULL DEFAULT 1,
        CreatedAt TEXT NOT NULL DEFAULT (datetime('now','localtime')))""")
    c.execute("""CREATE TABLE IF NOT EXISTS Sessions (
        SessionID INTEGER PRIMARY KEY AUTOINCREMENT,
        BakerID INTEGER NOT NULL, StartTime TEXT NOT NULL,
        EndTime TEXT, DurationMinutes REAL, AmountDue REAL, Month TEXT,
        FOREIGN KEY (BakerID) REFERENCES Bakers(BakerID))""")
    c.execute("""CREATE TABLE IF NOT EXISTS FailedAttempts (
        AttemptID INTEGER PRIMARY KEY AUTOINCREMENT,
        AttemptedAt TEXT NOT NULL DEFAULT (datetime('now','localtime')),
        Note TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS MonthlyBilling (
        BillingID INTEGER PRIMARY KEY AUTOINCREMENT,
        BakerID INTEGER NOT NULL, Month TEXT NOT NULL,
        TotalMinutes REAL NOT NULL DEFAULT 0,
        TotalHours REAL NOT NULL DEFAULT 0,
        TotalAmountKES REAL NOT NULL DEFAULT 0,
        GeneratedAt TEXT NOT NULL DEFAULT (datetime('now','localtime')),
        FOREIGN KEY (BakerID) REFERENCES Bakers(BakerID))""")

    # 6-digit PINs
    bakers = [
        ("Amina Wanjiku",  "123456", 50.0),
        ("Brian Otieno",   "234567", 50.0),
        ("Carol Njeri",    "345678", 50.0),
        ("David Kamau",    "456789", 50.0),
        ("Esther Achieng", "567890", 50.0),
        ("Felix Mwangi",   "678901", 50.0),
        ("Grace Moraa",    "789012", 50.0),
        ("Hassan Abdi",    "890123", 50.0),
        ("Irene Chebet",   "901234", 50.0),
        ("James Ndegwa",   "012345", 50.0),
    ]
    for name, pin, rate in bakers:
        c.execute("INSERT INTO Bakers (FullName,PIN_Hash,HourlyRate) VALUES (?,?,?)",
                  (name, hash_pin(pin), rate))
    print(f"✓ {len(bakers)} bakers seeded with 6-digit PINs")

    # Sample sessions this month
    now   = datetime.now()
    month = now.strftime("%Y-%m")
    base  = now.replace(day=1, hour=7, minute=0, second=0, microsecond=0)
    count = 0
    random.seed(42)
    for baker_id in range(1, 11):
        day_offset = 0
        for _ in range(random.randint(3, 6)):
            day_offset += random.randint(1, 2)
            if day_offset >= now.day: break
            start = base.replace(day=day_offset,
                                 hour=random.randint(7,16),
                                 minute=random.choice([0,15,30,45]))
            dur   = random.randint(45, 150)
            end   = start + timedelta(minutes=dur)
            amt   = round((dur/60)*50.0, 2)
            c.execute("INSERT INTO Sessions (BakerID,StartTime,EndTime,DurationMinutes,AmountDue,Month) VALUES (?,?,?,?,?,?)",
                      (baker_id, start.strftime("%Y-%m-%d %H:%M:%S"),
                       end.strftime("%Y-%m-%d %H:%M:%S"), round(dur,2), amt, month))
            count += 1

    print(f"✓ {count} demo sessions created for {month}")

    for i in range(3):
        c.execute("INSERT INTO FailedAttempts (Note) VALUES (?)",
                  (f"Wrong PIN entered | Attempt {i+1}/3 from 127.0.0.1",))
    print("✓ 3 failed attempts logged")

    conn.commit(); conn.close()

    print("\n" + "=" * 50)
    print("✅ Demo database ready!")
    print("=" * 50)
    print("\n📋 Baker 6-digit PINs:")
    print("  Amina Wanjiku  → 123456    Brian Otieno  → 234567")
    print("  Carol Njeri    → 345678    David Kamau   → 456789")
    print("  Esther Achieng → 567890    Felix Mwangi  → 678901")
    print("  Grace Moraa    → 789012    Hassan Abdi   → 890123")
    print("  Irene Chebet   → 901234    James Ndegwa  → 012345")
    print("\n🔐 Admin PIN: 0000")
    print("\n▶  Now run: python app.py")
    print("   Then open: http://127.0.0.1:5000\n")

if __name__ == "__main__":
    reset_and_seed()
