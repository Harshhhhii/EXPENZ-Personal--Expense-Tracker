# EXPENZ - Personal Expense Tracker

## Requirements
- Windows 10/11
- Python 3.10 or newer
- Tkinter (normally included with Python)
- SQLite (included with Python)
- Matplotlib (for the expense pie chart)

## Setup
1. Extract the EXPENZ folder.
2. Open Command Prompt.
3. Change directory to the folder containing `main.py`, for example:
   `cd Desktop\EXPENZ`
4. Install the chart library:
   `python -m pip install matplotlib`
5. Run:
   `python main.py`

If `python` does not work, try `py main.py` and `py -m pip install matplotlib`.

## Features
- Dashboard with total income, expenses and balance
- Add income and expense transactions
- Transaction history
- Delete selected transaction
- Category-wise expense report
- SQLite database persistence

The database file `expenz.db` is created automatically in the same folder when the app runs.

## Notes
- Amounts are displayed in Indian Rupees (₹).
- Dates must use YYYY-MM-DD format.
- Login, registration and budget alerts are intentionally excluded from this emergency submission version to keep the core application reliable.
