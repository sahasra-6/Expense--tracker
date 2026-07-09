from tkinter import *
from tkinter import ttk
from matplotlib import pyplot as plt
import mysql.connector
from tkinter import messagebox

# ---------------- MySQL Connection ----------------
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Varanasi@6",
    database="expense_tracker"
)

cur = conn.cursor()
print("Connected Successfully")

# ---------------- Add Expense ----------------
def add_expense():
    date_value = date_entry.get()
    category = category_entry.get()
    amount = amount_entry.get()
    monthly_budget = monthly_budget_entry.get()

    if date_value and category and amount:
        try:
            monthly_budget = float(monthly_budget) if monthly_budget else None

            cur.execute(
                "INSERT INTO expenses (date, category, amount, monthly_budget) VALUES (%s, %s, %s, %s)",
                (date_value, category, float(amount), monthly_budget)
            )
            conn.commit()

            status_label.config(text="Expense added successfully!", fg="green")

            date_entry.delete(0, END)
            category_entry.set('')
            amount_entry.delete(0, END)
            monthly_budget_entry.delete(0, END)

            view_expenses()
            limit()

        except Exception as e:
            status_label.config(text=f"Error: {e}", fg="red")
    else:
        status_label.config(text="Please fill all the fields!", fg="red")


# ---------------- Delete All Expenses ----------------
def delete_expense():
    confirm = messagebox.askyesno("Confirm", "Delete all expenses?")
    if confirm:
        cur.execute("DELETE FROM expenses")
        conn.commit()
        view_expenses()
        status_label.config(text="All expenses deleted.", fg="red")


# ---------------- View Expenses ----------------
def view_expenses():
    total_expense = 0
    expenses_tree.delete(*expenses_tree.get_children())

    try:
        cur.execute("SELECT * FROM expenses")
        rows = cur.fetchall()

        for row in rows:
            id, date_value, category, amount, monthly_budget = row

            expenses_tree.insert("", END, values=(
                date_value,
                category,
                f"{amount:.2f}",
                f"{monthly_budget:.2f}" if monthly_budget else ""
            ))

            total_expense += float(amount)

        total_label.config(text=f"Total Expense: {total_expense:.2f}")

        # Color configuration
        expenses_tree.tag_configure('over_budget', background='lightcoral')
        expenses_tree.tag_configure('within_budget', background='lightgreen')

        for child in expenses_tree.get_children():
            vals = expenses_tree.item(child, "values")
            amount = float(vals[2])
            monthly_budget = vals[3]

            if monthly_budget:
                if amount > float(monthly_budget):
                    expenses_tree.item(child, tags=('over_budget',))
                else:
                    expenses_tree.item(child, tags=('within_budget',))

    except Exception as e:
        status_label.config(text=f"Error: {e}", fg="red")


# ---------------- Visualize Expenses ----------------
def visualize_expenses_by_month():
    expenses_by_month = {}
    expenses_by_category = {}

    try:
        cur.execute("SELECT date, category, amount FROM expenses")
        rows = cur.fetchall()

        for date_value, category, amount in rows:
            month = date_value.strftime("%m")
            expenses_by_month[month] = expenses_by_month.get(month, 0) + float(amount)
            expenses_by_category[category] = expenses_by_category.get(category, 0) + float(amount)

        months = list(expenses_by_month.keys())
        expenses_values = list(expenses_by_month.values())

        plt.figure(figsize=(14, 8))

        plt.subplot(2, 2, 1)
        plt.bar(months, expenses_values)
        plt.xlabel("Month")
        plt.ylabel("Total Expense")
        plt.title("Expenses by Month")

        plt.subplot(2, 2, 2)
        plt.pie(
            list(expenses_by_category.values()),
            labels=list(expenses_by_category.keys()),
            autopct="%1.1f%%"
        )
        plt.title("Expenses by Category")

        plt.tight_layout()
        plt.show()

    except Exception as e:
        status_label.config(text=f"Error: {e}", fg="red")


# ---------------- Budget Limit Warning ----------------
def limit():
    cur.execute("SELECT SUM(amount) FROM expenses WHERE DATE_FORMAT(date, '%Y-%m') = DATE_FORMAT(CURDATE(), '%Y-%m')")
    lexpense = cur.fetchone()[0]
    lexpense = float(lexpense) if lexpense else 0.0

    cur.execute("SELECT MAX(monthly_budget) FROM expenses WHERE DATE_FORMAT(date, '%Y-%m') = DATE_FORMAT(CURDATE(), '%Y-%m')")
    mbudget = cur.fetchone()[0]
    mbudget = float(mbudget) if mbudget else 0.0

    if mbudget:
        used = (lexpense / mbudget) * 100
        messagebox.showinfo("Monthly Budget Status", f"You have used {used:.2f}% of your monthly budget.")


# ---------------- Show This Month’s Total ----------------
def thismonth():
    cur.execute("SELECT SUM(amount) FROM expenses WHERE DATE_FORMAT(date, '%Y-%m') = DATE_FORMAT(CURDATE(), '%Y-%m')")
    mthex = cur.fetchone()[0]
    mthex = float(mthex) if mthex else 0.0
    messagebox.showinfo("This Month's Expenses", f"This month's total expense: ₹{mthex:.2f}")


# ---------------- Main Tkinter UI ----------------
root = Tk()
root.title("Expense Tracker")
root.geometry("800x600")

Label(root, text="Date (YYYY-MM-DD):", fg="blue").grid(row=0, column=0, padx=5, pady=5)
date_entry = Entry(root)
date_entry.grid(row=0, column=1, padx=5, pady=5)

Label(root, text="Category:", fg="blue").grid(row=1, column=0, padx=5, pady=5)
category_entry = ttk.Combobox(root, values=[
    "Car EMI", "Loan EMI", "Grocery", "Electricity Bill", "Transportation",
    "Education and Childcare", "Medical Expenses", "Personal Care",
    "Entertainment", "Rent", "OTT Subscriptions", "Unexpected Expense"
], state="readonly")
category_entry.grid(row=1, column=1, padx=5, pady=5)

Label(root, text="Amount:", fg="blue").grid(row=2, column=0, padx=5, pady=5)
amount_entry = Entry(root)
amount_entry.grid(row=2, column=1, padx=5, pady=5)

Label(root, text="Monthly Budget:", fg="blue").grid(row=3, column=0, padx=5, pady=5)
monthly_budget_entry = Entry(root)
monthly_budget_entry.grid(row=3, column=1, padx=5, pady=5)

Button(root, text="Add Expense", fg="white", bg="black", command=add_expense).grid(row=4, column=0, columnspan=2, pady=10)
Button(root, text="Visualize Expenses", fg="white", bg="black", command=visualize_expenses_by_month).grid(row=5, column=0, columnspan=2, pady=10)
Button(root, text="Reset (Delete All)", fg="white", bg="black", command=delete_expense).grid(row=6, column=0, pady=10)
Button(root, text="This Month", fg="white", bg="black", command=thismonth).grid(row=6, column=1, pady=10)

columns = ("Date", "Category", "Amount", "Monthly Budget")
expenses_tree = ttk.Treeview(root, columns=columns, show="headings")

for col in columns:
    expenses_tree.heading(col, text=col)

expenses_tree.grid(row=7, column=0, columnspan=3, padx=5, pady=5)

total_label = Label(root, text="", font=("Arial", 10, "bold"))
total_label.grid(row=8, column=0, columnspan=2)

status_label = Label(root, text="", fg="green")
status_label.grid(row=9, column=0, columnspan=2)

view_expenses()
root.mainloop()