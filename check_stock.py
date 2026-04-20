import pymysql
import sys
from config import DB_CONFIG

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

try:
    conn = pymysql.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database=DB_CONFIG['database'],
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    
    cursor.execute("SELECT stock_code, stock_name, current_price, change_percent FROM stock_info LIMIT 10")
    rows = cursor.fetchall()
    
    print("股票代码 | 股票名称 | 当前价格 | 涨跌幅")
    print("-" * 50)
    for row in rows:
        print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
