import sqlite3
from datetime import datetime
import random
from dateutil.relativedelta import relativedelta

def create_sales_database():
    # Create SQLite database
    conn = sqlite3.connect('examples/sales.sqlite3')
    cursor = conn.cursor()

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
        revenue DECIMAL(10, 2)
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
        ("Premium Coffee Maker", "Appliances", 1200, 360000),
        ("Wireless Earbuds", "Electronics", 2500, 325000),
        ("Smart Watch", "Electronics", 800, 280000),
        ("Robot Vacuum", "Appliances", 600, 270000),
        ("Gaming Console", "Electronics", 450, 225000)
    ]

    for product in products:
        cursor.execute('''
        INSERT INTO products (name, category, units_sold, revenue)
        VALUES (?, ?, ?, ?)
        ''', product)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_sales_database()
