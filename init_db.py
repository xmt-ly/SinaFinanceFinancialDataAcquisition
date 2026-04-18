import pymysql
from config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE

# 连接到MySQL服务器（不指定数据库）
try:
    conn = pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    
    # 创建数据库
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DATABASE} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    print(f"数据库 {MYSQL_DATABASE} 创建成功")
    
    # 关闭连接
    cursor.close()
    conn.close()
    print("数据库初始化完成")
except Exception as e:
    print(f"数据库初始化失败: {e}")
