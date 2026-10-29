-- Banking Management System Phase 1 (SQLite)
PRAGMA foreign_keys = ON;

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
    FOREIGN KEY (Branch_ID) REFERENCES Branch(Branch_ID) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS "Transaction" (
    Transaction_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Account_Number TEXT NOT NULL,
    Transaction_Type TEXT NOT NULL CHECK (Transaction_Type IN ('Deposit', 'Withdrawal')),
    Amount NUMERIC NOT NULL CHECK (Amount > 0),
    Transaction_Date TEXT NOT NULL DEFAULT (datetime('now','localtime')),
    FOREIGN KEY (Account_Number) REFERENCES Customer(Account_Number)
        ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_transaction_date ON "Transaction"(Transaction_Date);
CREATE INDEX IF NOT EXISTS idx_transaction_account ON "Transaction"(Account_Number);

-- Required report examples:
-- Customer-wise transaction history
SELECT c.Customer_Name, t.Account_Number, t.Transaction_Type, t.Amount, t.Transaction_Date
FROM "Transaction" t JOIN Customer c ON c.Account_Number = t.Account_Number
ORDER BY c.Customer_Name, t.Transaction_Date DESC;

-- Daily transaction report (replace date as needed)
SELECT date(Transaction_Date) AS Report_Date,
       COUNT(*) AS Transaction_Count,
       SUM(CASE WHEN Transaction_Type='Deposit' THEN Amount ELSE 0 END) AS Total_Deposits,
       SUM(CASE WHEN Transaction_Type='Withdrawal' THEN Amount ELSE 0 END) AS Total_Withdrawals
FROM "Transaction"
WHERE date(Transaction_Date) = date('now','localtime')
GROUP BY date(Transaction_Date);

-- Total deposits
SELECT COALESCE(SUM(Amount),0) AS Total_Deposits
FROM "Transaction" WHERE Transaction_Type='Deposit';

-- Total withdrawals
SELECT COALESCE(SUM(Amount),0) AS Total_Withdrawals
FROM "Transaction" WHERE Transaction_Type='Withdrawal';

-- Branch-wise customer count
SELECT b.Branch_ID, b.Branch_Name, b.Branch_Location, COUNT(c.Customer_ID) AS Customer_Count
FROM Branch b LEFT JOIN Customer c ON b.Branch_ID=c.Branch_ID
GROUP BY b.Branch_ID, b.Branch_Name, b.Branch_Location;
