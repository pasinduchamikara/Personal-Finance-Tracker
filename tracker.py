import csv
import os
from datetime import datetime

DATA_FILE = "transactions.csv"

def initialize_files():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Type", "Category", "Amount", "Description"])


def add_transaction():
    date = datetime.now().strftime("%Y-%m-%d")
    type_ = input("Income or Expense? (i/e): ").lower()
    type_ ="Income" if type_ == "i" else "Expense"
    category = input ("Category (e.g. Salary, Food, Rent):")

    amount = float(input("Amount (positive number):"))
    if type_ =="Expense":
        amount = -amount
    desc= input ("Description: ")

    with open (DATA_FILE, "a" , newline="") as f:
        writer = csv.writer(f)
        writer.writerow([date, type_, category, amount, desc])
    print ("Transaction added !")


def view_summary():
    if not os.path.exists(DATA_FILE):
        print("No transactions yet.")
        return
    
    total_income =0
    total_expense = 0
    categories = {}

    with open (DATA_FILE, "r") as f:
        reader = csv.reader(f)
        next (reader) 
        for row in reader:
            if  len (row) < 4: continue 
            amt = float (row[3])
            cat = row[2]
            if amt>0:
                total_income += amt
            else:
                total_expense += abs(amt)
                categories[cat] = categories.get(cat, 0) + amt

    print(f"\nSummary:")
    print (f"Total Income: +{ total_income : ,.2f} LKR")
    print (f"Total Expenses: -{ total_expense:,.2f} LKR")
    print (f"Net Savings: { total_income - total_expense:,.2f} LKR")
    print("By Category:")
    for cat,amt in sorted  (categories.items(), key = lambda x: x[1]):
        print (f" {cat} : {amt:,.2f} LKR")


def main():
    initialize_files()
    while True:
        print ("\nPersonal Finance Tracker")
        print ("1. Add transaction")
        print("2. View summary")
        print ("3. Exit")
        choice = input("Choose:")
        if choice == "1":
            add_transaction()
        elif choice == "2":
            view_summary()
        elif choice == "3":
            break
        else:
            print ("Invalid choice.")

if __name__ == "__main__":
    main()




