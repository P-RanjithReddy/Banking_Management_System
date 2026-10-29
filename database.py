"""SQLite database helpers for Banking Management System."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "banking_management.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_database():
    """Create database tables if they do not exist."""
    with get_connection() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS Branch (
            Branch_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Branch_Name TEXT NOT NULL,
            Branch_Location TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS Customer (
            Customer_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Customer_Name TEXT NOT NULL,
            Account_Number TEXT NOT NULL UNIQUE,
            Account_Type TEXT NOT NULL CHECK (Account_Type IN ('Savings', 'Current')),
            Phone_Number TEXT NOT NULL,
            Email TEXT NOT NULL,
            Balance NUMERIC NOT NULL DEFAULT 0 CHECK (Balance >= 0),
            Branch_ID INTEGER,
            FOREIGN KEY (Branch_ID) REFERENCES Branch(Branch_ID)
                ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS "Transaction" (
            Transaction_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Account_Number TEXT NOT NULL,
            Transaction_Type TEXT NOT NULL
                CHECK (Transaction_Type IN ('Deposit', 'Withdrawal')),
            Amount NUMERIC NOT NULL CHECK (Amount > 0),
            Transaction_Date TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (Account_Number) REFERENCES Customer(Account_Number)
                ON UPDATE CASCADE ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_transaction_date
            ON "Transaction"(Transaction_Date);
        CREATE INDEX IF NOT EXISTS idx_transaction_account
            ON "Transaction"(Account_Number);
        """)
    print(f"SQLite database ready: {DB_PATH.name}")


if __name__ == "__main__":
    initialize_database()
