"""Console-based Banking Management System - Python + SQLite."""
import re
import sqlite3
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from database import get_connection, initialize_database


def read_nonempty(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("This field cannot be empty.")


def read_phone():
    while True:
        phone = input("Phone number (10 digits): ").strip()
        if re.fullmatch(r"[6-9]\d{9}", phone):
            return phone
        print("Enter a valid 10-digit Indian mobile number.")


def read_email():
    while True:
        email = input("Email: ").strip()
        if re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            return email
        print("Enter a valid email address.")


def read_amount(prompt="Amount: "):
    while True:
        raw = input(prompt).strip()
        try:
            amount = Decimal(raw)
            if amount.is_finite() and amount > 0 and amount <= Decimal("9999999999.99"):
                return amount.quantize(Decimal("0.01"))
        except (InvalidOperation, ValueError):
            pass
        print("Enter a valid amount greater than zero.")


def print_rows(rows):
    if not rows:
        print("No records found.")
        return
    for row in rows:
        print("-" * 65)
        for key in row.keys():
            print(f"{key}: {row[key]}")


def add_customer():
    print("\n--- Add Customer ---")
    name = read_nonempty("Customer name: ")
    account = read_nonempty("Account number: ")
    while True:
        account_type = input("Account type (Savings/Current): ").strip().title()
        if account_type in ("Savings", "Current"):
            break
        print("Choose Savings or Current.")
    phone = read_phone()
    email = read_email()
    try:
        with get_connection() as conn:
            conn.execute("""
                INSERT INTO Customer
                (Customer_Name, Account_Number, Account_Type, Phone_Number, Email, Balance)
                VALUES (?, ?, ?, ?, ?, 0)
            """, (name, account, account_type, phone, email))
        print("Customer added successfully. Opening balance: ₹0.00")
    except sqlite3.IntegrityError as exc:
        if "Account_Number" in str(exc) or "UNIQUE" in str(exc):
            print("That account number already exists. Use a unique account number.")
        else:
            print(f"Unable to add customer: {exc}")
    except sqlite3.Error as exc:
        print(f"Database error: {exc}")


def view_customers():
    try:
        with get_connection() as conn:
            rows = conn.execute("""
                SELECT c.Customer_ID, c.Customer_Name, c.Account_Number,
                       c.Account_Type, c.Phone_Number, c.Email, c.Balance,
                       b.Branch_Name
                FROM Customer c LEFT JOIN Branch b ON c.Branch_ID = b.Branch_ID
                ORDER BY c.Customer_ID
            """).fetchall()
        print_rows(rows)
    except sqlite3.Error as exc:
        print(f"Database error: {exc}")


def search_customer():
    key = read_nonempty("Enter account number, customer name, or phone: ")
    try:
        with get_connection() as conn:
            rows = conn.execute("""
                SELECT Customer_ID, Customer_Name, Account_Number, Account_Type,
                       Phone_Number, Email, Balance, Branch_ID
                FROM Customer
                WHERE Account_Number = ? OR Phone_Number = ? OR Customer_Name LIKE ?
                ORDER BY Customer_ID
            """, (key, key, f"%{key}%")).fetchall()
        print_rows(rows)
    except sqlite3.Error as exc:
        print(f"Database error: {exc}")


def update_customer():
    account = read_nonempty("Account number to update: ")
    try:
        with get_connection() as conn:
            row = conn.execute("SELECT * FROM Customer WHERE Account_Number = ?",
                               (account,)).fetchone()
        if not row:
            print("Customer not found.")
            return
        print("Press Enter to keep the current value.")
        name = input(f"Name [{row['Customer_Name']}]: ").strip() or row["Customer_Name"]
        phone = input(f"Phone [{row['Phone_Number']}]: ").strip() or row["Phone_Number"]
        if not re.fullmatch(r"[6-9]\d{9}", phone):
            print("Invalid phone number.")
            return
        email = input(f"Email [{row['Email']}]: ").strip() or row["Email"]
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            print("Invalid email.")
            return
        with get_connection() as conn:
            conn.execute("""UPDATE Customer
                            SET Customer_Name = ?, Phone_Number = ?, Email = ?
                            WHERE Account_Number = ?""", (name, phone, email, account))
        print("Customer details updated.")
    except sqlite3.Error as exc:
        print(f"Database error: {exc}")


def delete_customer():
    account = read_nonempty("Account number to delete: ")
    confirm = input("This also deletes transaction history. Type YES to confirm: ").strip()
    if confirm != "YES":
        print("Deletion cancelled.")
        return
    try:
        with get_connection() as conn:
            cursor = conn.execute("DELETE FROM Customer WHERE Account_Number = ?", (account,))
            deleted = cursor.rowcount
        print("Customer deleted." if deleted else "Customer not found.")
    except sqlite3.Error as exc:
        print(f"Database error: {exc}")


def transact(kind):
    account = read_nonempty("Account number: ")
    try:
        with get_connection() as conn:
            conn.execute("BEGIN IMMEDIATE")
            customer = conn.execute(
                "SELECT Balance FROM Customer WHERE Account_Number = ?", (account,)
            ).fetchone()
            if not customer:
                print("Account not found.")
                return
            amount = read_amount()
            balance = Decimal(str(customer["Balance"]))
            new_balance = balance + amount if kind == "Deposit" else balance - amount
            if kind == "Withdrawal" and amount > balance:
                print(f"Insufficient funds. Available balance: ₹{balance:.2f}")
                return
            conn.execute("UPDATE Customer SET Balance = ? WHERE Account_Number = ?",
                         (str(new_balance), account))
            conn.execute("""INSERT INTO "Transaction"
                            (Account_Number, Transaction_Type, Amount)
                            VALUES (?, ?, ?)""", (account, kind, str(amount)))
        print(f"{kind} successful. New balance: ₹{new_balance:.2f}")
    except sqlite3.Error as exc:
        print(f"Database error: {exc}")


def check_balance():
    account = read_nonempty("Account number: ")
    try:
        with get_connection() as conn:
            row = conn.execute("""SELECT Customer_Name, Account_Number, Balance
                                  FROM Customer WHERE Account_Number = ?""",
                               (account,)).fetchone()
        if row:
            print(f"{row['Customer_Name']} | Account: {row['Account_Number']} | "
                  f"Balance: ₹{Decimal(str(row['Balance'])):.2f}")
        else:
            print("Account not found.")
    except sqlite3.Error as exc:
        print(f"Database error: {exc}")


def transaction_history():
    account = read_nonempty("Account number: ")
    try:
        with get_connection() as conn:
            rows = conn.execute("""
                SELECT Transaction_ID, Account_Number, Transaction_Type,
                       Amount, Transaction_Date
                FROM "Transaction"
                WHERE Account_Number = ?
                ORDER BY Transaction_Date DESC, Transaction_ID DESC
            """, (account,)).fetchall()
        print_rows(rows)
    except sqlite3.Error as exc:
        print(f"Database error: {exc}")


def add_branch():
    name = read_nonempty("Branch name: ")
    location = read_nonempty("Branch location: ")
    try:
        with get_connection() as conn:
            conn.execute("INSERT INTO Branch (Branch_Name, Branch_Location) VALUES (?, ?)",
                         (name, location))
        print("Branch added.")
    except sqlite3.Error as exc:
        print(f"Database error: {exc}")


def view_branches():
    try:
        with get_connection() as conn:
            rows = conn.execute("SELECT * FROM Branch ORDER BY Branch_ID").fetchall()
        print_rows(rows)
    except sqlite3.Error as exc:
        print(f"Database error: {exc}")


def assign_branch():
    account = read_nonempty("Customer account number: ")
    try:
        with get_connection() as conn:
            customer = conn.execute("SELECT Customer_ID FROM Customer WHERE Account_Number = ?",
                                    (account,)).fetchone()
            if not customer:
                print("Customer not found.")
                return
            branches = conn.execute("SELECT * FROM Branch ORDER BY Branch_ID").fetchall()
            print_rows(branches)
            if not branches:
                print("Add a branch first.")
                return
            raw = input("Enter Branch_ID to assign (0 to unassign): ").strip()
            if not raw.isdigit():
                print("Branch ID must be a number.")
                return
            branch_id = int(raw)
            if branch_id == 0:
                conn.execute("UPDATE Customer SET Branch_ID = NULL WHERE Account_Number = ?",
                             (account,))
                print("Customer unassigned from branch.")
                return
            exists = conn.execute("SELECT Branch_ID FROM Branch WHERE Branch_ID = ?",
                                  (branch_id,)).fetchone()
            if not exists:
                print("Branch ID not found.")
                return
            conn.execute("UPDATE Customer SET Branch_ID = ? WHERE Account_Number = ?",
                         (branch_id, account))
        print("Customer assigned to branch.")
    except sqlite3.Error as exc:
        print(f"Database error: {exc}")


def customer_transaction_report():
    try:
        with get_connection() as conn:
            rows = conn.execute("""
                SELECT c.Customer_Name, t.Account_Number, t.Transaction_Type,
                       t.Amount, t.Transaction_Date
                FROM "Transaction" t
                JOIN Customer c ON c.Account_Number = t.Account_Number
                ORDER BY c.Customer_Name, t.Transaction_Date DESC
            """).fetchall()
        print_rows(rows)
    except sqlite3.Error as exc:
        print(f"Database error: {exc}")


def daily_transaction_report():
    day = input(f"Date (YYYY-MM-DD, Enter for today {date.today()}): ").strip()
    if not day:
        day = date.today().isoformat()
    try:
        datetime.strptime(day, "%Y-%m-%d")
    except ValueError:
        print("Use a valid YYYY-MM-DD date.")
        return
    try:
        with get_connection() as conn:
            rows = conn.execute("""
                SELECT date(Transaction_Date) AS Report_Date,
                       COUNT(*) AS Transaction_Count,
                       SUM(CASE WHEN Transaction_Type = 'Deposit' THEN Amount ELSE 0 END)
                           AS Total_Deposits,
                       SUM(CASE WHEN Transaction_Type = 'Withdrawal' THEN Amount ELSE 0 END)
                           AS Total_Withdrawals
                FROM "Transaction"
                WHERE date(Transaction_Date) = ?
                GROUP BY date(Transaction_Date)
            """, (day,)).fetchall()
        print_rows(rows)
    except sqlite3.Error as exc:
        print(f"Database error: {exc}")


def deposit_withdrawal_totals():
    try:
        with get_connection() as conn:
            rows = conn.execute("""
                SELECT Transaction_Type, COUNT(*) AS Transaction_Count,
                       COALESCE(SUM(Amount), 0) AS Total_Amount
                FROM "Transaction"
                GROUP BY Transaction_Type
                ORDER BY Transaction_Type
            """).fetchall()
        print_rows(rows)
    except sqlite3.Error as exc:
        print(f"Database error: {exc}")


def branch_customer_count():
    try:
        with get_connection() as conn:
            rows = conn.execute("""
                SELECT b.Branch_ID, b.Branch_Name, b.Branch_Location,
                       COUNT(c.Customer_ID) AS Customer_Count
                FROM Branch b LEFT JOIN Customer c ON b.Branch_ID = c.Branch_ID
                GROUP BY b.Branch_ID, b.Branch_Name, b.Branch_Location
                ORDER BY b.Branch_ID
            """).fetchall()
        print_rows(rows)
    except sqlite3.Error as exc:
        print(f"Database error: {exc}")


def reports_menu():
    while True:
        print("""
--- SQL Reports ---
1. Customer-wise transaction history (all customers)
2. Daily transaction report
3. Total deposits and withdrawals
4. Branch-wise customer count
0. Back
""")
        choice = input("Choose: ").strip()
        if choice == "1":
            customer_transaction_report()
        elif choice == "2":
            daily_transaction_report()
        elif choice == "3":
            deposit_withdrawal_totals()
        elif choice == "4":
            branch_customer_count()
        elif choice == "0":
            return
        else:
            print("Invalid option.")


def main():
    initialize_database()
    actions = {
        "1": add_customer, "2": view_customers, "3": search_customer,
        "4": update_customer, "5": delete_customer,
        "6": lambda: transact("Deposit"), "7": lambda: transact("Withdrawal"),
        "8": check_balance, "9": transaction_history,
        "10": add_branch, "11": view_branches, "12": assign_branch,
        "13": reports_menu
    }
    while True:
        print("""
========== BANKING MANAGEMENT SYSTEM ==========
CUSTOMER MODULE
1. Add Customer
2. View Customers
3. Search Customer
4. Update Customer Details
5. Delete Customer

BANKING MODULE
6. Deposit Amount
7. Withdraw Amount
8. Check Balance
9. View Transaction History

BRANCH MODULE
10. Add Branch
11. View Branches
12. Assign Customer to Branch

SQL REPORTS
13. Reports Menu
0. Exit
""")
        choice = input("Enter your choice: ").strip()
        if choice == "0":
            print("Thank you for using Banking Management System.")
            break
        action = actions.get(choice)
        if action:
            try:
                action()
            except (sqlite3.Error, ValueError) as exc:
                print(f"Operation failed: {exc}")
            except KeyboardInterrupt:
                print("\nOperation cancelled.")
        else:
            print("Invalid choice. Select a menu number from 0 to 13.")


if __name__ == "__main__":
    main()
