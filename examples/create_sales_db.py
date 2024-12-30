import sqlite3
from datetime import datetime
import random
from dateutil.relativedelta import relativedelta

def create_sales_database():
    # Create SQLite database
    conn = sqlite3.connect('examples/sales.sqlite3')
    cursor = conn.cursor()

    # Drop existing tables
    cursor.execute('DROP TABLE IF EXISTS monthly_sales')
    cursor.execute('DROP TABLE IF EXISTS products')

    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS monthly_sales (
        month DATE PRIMARY KEY,
        sales DECIMAL(10, 2)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        name TEXT,
        category TEXT,
        units_sold INTEGER,
        revenue DECIMAL(10, 2),
        date DATE
    )
    ''')

    # Clear existing data
    cursor.execute('DELETE FROM monthly_sales')
    cursor.execute('DELETE FROM products')

    # Generate monthly sales data
    start_date = datetime(2024, 1, 1)
    base_sales = 45000
    growth_rate = 1.1

    for i in range(12):
        month = start_date + relativedelta(months=i)
        sales = base_sales * (growth_rate ** i) + random.uniform(-5000, 5000)
        cursor.execute('INSERT OR REPLACE INTO monthly_sales (month, sales) VALUES (?, ?)',
                      (month.strftime('%Y-%m-%d'), round(sales, 2)))

    # Generate product data
    products = [
        ("Premium Coffee Maker", "Appliances", 1200, 360000, "2024-06-15"),
        ("Wireless Earbuds", "Electronics", 2500, 325000, "2024-03-20"),
        ("Smart Watch", "Electronics", 800, 280000, "2024-08-10"),
        ("Robot Vacuum", "Appliances", 600, 270000, "2024-05-01"),
        ("Gaming Console", "Electronics", 450, 225000, "2024-07-30")
    ]

    for product in products:
        cursor.execute('INSERT INTO products (name, category, units_sold, revenue, date) VALUES (?, ?, ?, ?, ?)', product)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_sales_database()
