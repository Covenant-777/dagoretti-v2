"""
database.py — Dagoretti Kitchen Incubator
PostgreSQL database — data persists forever on Render
"""
import psycopg, hashlib, os
from datetime import datetime

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://dagoretti_db_user:WwRfDK9joeJPF1GxUzYPPBrjvHj4rM8X@dpg-d91eqirsq97s738fr60g-a/dagoretti_db"
)

def get_db():
    conn = psycopg.connect(DATABASE_URL, row_factory=psycopg.rows.dict_row)
    return conn

def hash_pin(pin: str) -> str:
    return hashlib.sha256(pin.encode()).hexdigest()

def init_db():
    conn = get_db(); c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS Bakers (
        BakerID    SERIAL PRIMARY KEY,
        FullName   TEXT NOT NULL,
        PIN_Hash   TEXT NOT NULL,
        HourlyRate REAL NOT NULL DEFAULT 50.0,
        IsActive   INTEGER NOT NULL DEFAULT 1,
        CreatedAt  TEXT NOT NULL DEFAULT (to_char(now(), 'YYYY-MM-DD HH24:MI:SS')))""")

    c.execute("""CREATE TABLE IF NOT EXISTS Sessions (
        SessionID       SERIAL PRIMARY KEY,
        BakerID         INTEGER NOT NULL REFERENCES Bakers(BakerID),
        StartTime       TEXT NOT NULL,
        EndTime         TEXT,
        DurationMinutes REAL,
        AmountDue       REAL,
        Month           TEXT)""")

    c.execute("""CREATE TABLE IF NOT EXISTS FailedAttempts (
        AttemptID   SERIAL PRIMARY KEY,
        AttemptedAt TEXT NOT NULL DEFAULT (to_char(now(), 'YYYY-MM-DD HH24:MI:SS')),
        Note        TEXT)""")

    c.execute("""CREATE TABLE IF NOT EXISTS MonthlyBilling (
        BillingID      SERIAL PRIMARY KEY,
        BakerID        INTEGER NOT NULL REFERENCES Bakers(BakerID),
        Month          TEXT NOT NULL,
        TotalMinutes   REAL NOT NULL DEFAULT 0,
        TotalHours     REAL NOT NULL DEFAULT 0,
        TotalAmountKES REAL NOT NULL DEFAULT 0,
        GeneratedAt    TEXT NOT NULL DEFAULT (to_char(now(), 'YYYY-MM-DD HH24:MI:SS')))""")

    c.execute("""CREATE TABLE IF NOT EXISTS AdminSettings (
        SettingID    SERIAL PRIMARY KEY,
        SettingKey   TEXT NOT NULL UNIQUE,
        SettingValue TEXT NOT NULL,
        UpdatedAt    TEXT NOT NULL DEFAULT (to_char(now(), 'YYYY-MM-DD HH24:MI:SS')))""")

    c.execute("""CREATE TABLE IF NOT EXISTS PINChangeRequests (
        RequestID   SERIAL PRIMARY KEY,
        BakerID     INTEGER NOT NULL REFERENCES Bakers(BakerID),
        NewPIN_Hash TEXT NOT NULL,
        Status      TEXT NOT NULL DEFAULT 'pending',
        RequestedAt TEXT NOT NULL DEFAULT (to_char(now(), 'YYYY-MM-DD HH24:MI:SS')),
        ApprovedAt  TEXT)""")

    c.execute("SELECT COUNT(*) FROM AdminSettings WHERE SettingKey='admin_pin_hash'")
    if c.fetchone()['count'] == 0:
        c.execute("INSERT INTO AdminSettings (SettingKey, SettingValue) VALUES (%s,%s)",
                  ('admin_pin_hash', hash_pin('0000')))

    c.execute("SELECT COUNT(*) FROM Bakers")
    if c.fetchone()['count'] == 0:
        for name, pin, rate in [
            ("Amina Wanjiku","123456",50.0),("Brian Otieno","234567",50.0),
            ("Carol Njeri","345678",50.0),("David Kamau","456789",50.0),
            ("Esther Achieng","567890",50.0),("Felix Mwangi","678901",50.0),
            ("Grace Moraa","789012",50.0),("Hassan Abdi","890123",50.0),
            ("Irene Chebet","901234",50.0),("James Ndegwa","012345",50.0),
        ]:
            c.execute("INSERT INTO Bakers (FullName,PIN_Hash,HourlyRate) VALUES (%s,%s,%s)",
                      (name,hash_pin(pin),rate))

    conn.commit(); conn.close()
    print("[DB] PostgreSQL ready — data persists forever!")

if __name__ == "__main__":
    init_db()
