import pymysql
from config import DB_CONFIG

try:
    # 连接数据库
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # 查询总新闻数
    cursor.execute('SELECT COUNT(*) FROM sina_finance_news')
    total_news = cursor.fetchone()[0]
    print(f'总新闻数: {total_news}')
    
    # 查询内容为空的新闻数
    cursor.execute('SELECT COUNT(*) FROM sina_finance_news WHERE content IS NULL OR content = \'\'')
    empty_content_news = cursor.fetchone()[0]
    print(f'内容为空的新闻数: {empty_content_news}')
    
    # 查询前5条内容为空的新闻
    print('\n前5条内容为空的新闻:')
    cursor.execute('SELECT id, url, title FROM sina_finance_news WHERE content IS NULL OR content = \'\' LIMIT 5')
    for row in cursor.fetchall():
        news_id, url, title = row
        print(f'ID: {news_id}, Title: {title[:50]}..., URL: {url}')
    
    # 关闭连接
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"错误: {e}")
