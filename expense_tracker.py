import pandas as pd
import os
import bcrypt
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

USERS_FILE = "users.csv"

# Ensure users file exists
if not os.path.exists(USERS_FILE):
    pd.DataFrame(columns=["Username", "Password"]).to_csv(USERS_FILE, index=False)

def hash_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode("utf-8"), hashed)

def signup():
    users = pd.read_csv(USERS_FILE)
    username = input("Enter a username: ").strip()

    if username in users["Username"].values:
        print("❌ Username already exists. Try logging in.")
        return None

    password = input("Enter a password: ").strip()
    hashed_pw = hash_password(password)

    new_user = pd.DataFrame([[username, hashed_pw.decode("utf-8")]], columns=["Username", "Password"])
    users = pd.concat([users, new_user], ignore_index=True)
    users.to_csv(USERS_FILE, index=False)

    # Create personal expense file
    user_file = f"{username}_expenses.csv"
    pd.DataFrame(columns=["Date", "Category", "Amount", "Note"]).to_csv(user_file, index=False)

    print("✅ Account created successfully! Please log in now.\n")
    return None

def login():
    users = pd.read_csv(USERS_FILE)
    username = input("Username: ").strip()
    password = input("Password: ").strip()

    if username not in users["Username"].values:
        print("❌ User not found.")
        return None

    stored_hash = users.loc[users["Username"] == username, "Password"].values[0].encode("utf-8")
    if verify_password(password, stored_hash):
        print(f"✅ Welcome, {username}!\n")
        return username
    else:
        print("❌ Incorrect password.")
        return None

def load_user_data(username):
    file = f"{username}_expenses.csv"
    if os.path.exists(file):
        return pd.read_csv(file), file
    else:
        df = pd.DataFrame(columns=["Date", "Category", "Amount", "Note"])
        df.to_csv(file, index=False)
        return df, file

def save_data(df, file):
    df.to_csv(file, index=False)

# -------- Expense Tracker Core -------- #
def add_expense(df, file):
    amount = float(input("Enter amount: "))
    category = input("Enter category (food, travel, bills, etc): ")
    note = input("Enter note (optional): ")
    date = datetime.now().strftime("%Y-%m-%d")

    new_data = pd.DataFrame([[date,category, amount, note]], columns=df.columns)
    df = pd.concat([df, new_data], ignore_index=True)
    save_data(df, file)
    print("✅ Expense added successfully!\n")
    return df

def view_expenses(df):
    if df.empty:
        print("No expenses found.\n")
        return
    print("\n📜 All Expenses:\n", df.to_string(index=False), "\n")

def summary_by_category(df):
    if df.empty:
        print("No data to summarize.\n")
        return
    summary = df.groupby("Category")["Amount"].sum()
    print("\n💰 Total spent by category:\n", summary, "\n")
    summary.plot(kind="pie", autopct="%1.1f%%", title="Spending by Category")
    plt.ylabel("")
    plt.show()

def monthly_summary(df):
    if df.empty:
        print("No data to summarize.\n")
        return
    df["Month"] = pd.to_datetime(df["Date"]).dt.to_period("M")
    summary = df.groupby("Month")["Amount"].sum()
    print("\n📆 Monthly Summary:\n", summary, "\n")
    summary.plot(kind="bar", title="Monthly Spending", xlabel="Month", ylabel="Total Amount")
    plt.show()

def weekly_summary(df):
    if df.empty:
        print("No data to summarize.\n")
        return
    df["Date"] = pd.to_datetime(df["Date"])
    last_week = datetime.now() - timedelta(days=7)
    week_data = df[df["Date"] >= last_week]
    if week_data.empty:
        print("No expenses in the last 7 days.\n")
        return
    print("\n🗓️ Weekly Summary:\n", week_data)
    print("Total spent:", week_data["Amount"].sum())

# -------- Menu Logic -------- #
def main_menu(username):
    df, file = load_user_data(username)
    while True:
        print("\n====== EXPENSE TRACKER ======")
        print("1. Add Expense")
        print("2. View All Expenses")
        print("3. Summary by Category")
        print("4. Monthly Summary")
        print("5. Weekly Summary")
        print("6. Logout")
        print("=============================")

        choice = input("Choose an option: ")
        if choice == "1":
            df = add_expense(df, file)
        elif choice == "2":
            view_expenses(df)
        elif choice == "3":
            summary_by_category(df)
        elif choice == "4":
            monthly_summary(df)
        elif choice == "5":
            weekly_summary(df)
        elif choice == "6":
            print(f"👋 Logged out, {username}.")
            break
        else:
            print("Invalid choice.\n")

# -------- Entry Point -------- #
def start():
    while True:
        print("\n===== WELCOME TO EXPENSE TRACKER =====")
        print("1. Login")
        print("2. Sign Up")
        print("3. Exit")
        print("=====================================")
        choice = input("Choose an option: ")

        if choice == "1":
            username = login()
            if username:
                main_menu(username)
        elif choice == "2":
            signup()
        elif choice == "3":
            print("Goodbye 👋")
            break
        else:
            print("Invalid input. Try again.")

if __name__ == "__main__":
    start()