# Banking Management System — Phase 1 (Python + SQLite)

## Features
- Customer CRUD: add, view, search, update, delete
- Deposit, withdrawal, check balance, transaction history
- Branch create/view and customer-to-branch assignment
- SQL reports: customer-wise transaction history, daily report, total deposits,
  total withdrawals, branch-wise customer count
- Duplicate account prevention, positive transaction amount checks, insufficient
  balance protection, phone and email validation
- Parameterized SQL, foreign keys, exception handling, modular reusable functions

## Requirements
- Python 3.10+ (Python 3.14 is fine)
- DB Browser for SQLite (to inspect tables; optional for running the app)
- No Python database package is required: `sqlite3` is built into Python.

## Run
1. Extract the project ZIP.
2. Open a terminal in the `Banking_Management_System_SQLite` folder.
3. Run: `python main.py`
4. The app automatically creates `banking_management.db` in the same folder.

## View the database in DB Browser for SQLite
1. Open DB Browser for SQLite.
2. Click **Open Database**.
3. Select `banking_management.db` from this project folder.
4. Choose **Browse Data** and select `Customer`, `Branch`, or `Transaction`.
5. After running transactions, click **Refresh** to see updated data.

## Demonstration plan
1. Choose 10 to add a branch (e.g. Central Branch, Hyderabad).
2. Choose 1 to add a customer using a unique account number, valid 10-digit phone,
   and valid email. Opening balance starts at ₹0.
3. Choose 12 to assign the customer to the branch.
4. Choose 6 to deposit 5000.
5. Choose 8 to check balance.
6. Choose 7 and attempt to withdraw 6000: insufficient balance should be rejected.
7. Choose 7 to withdraw 1000, then choose 9 to show transaction history.
8. Choose 13 to demonstrate all four SQL reports.

## Tables
- `Customer`: customer profile, unique account number, balance and optional Branch_ID
- `Transaction`: deposit/withdrawal records with timestamp
- `Branch`: branch name and location

Deleting a customer also deletes their transaction history; the app asks for explicit confirmation.
This is an educational demo, not production banking software.
