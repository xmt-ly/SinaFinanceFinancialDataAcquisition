import pymysql
from config import DB_CONFIG
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def process_existing_content():
    """处理数据库中已存在的内容，删除责任编辑及其后面的内容"""
    try:
        # 连接数据库
        conn = pymysql.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            charset='utf8mb4',
            use_unicode=True
        )
        cursor = conn.cursor()
        
        # 查询包含责任编辑的内容
        cursor.execute("SELECT id, content FROM sina_finance_news WHERE content LIKE '%责任编辑%'")
        rows = cursor.fetchall()
        
        logger.info(f"找到 {len(rows)} 条包含责任编辑的内容")
        
        count = 0
        for news_id, content in rows:
            if content and '责任编辑' in content:
                # 删除责任编辑及其后面的内容
                new_content = content.split('责任编辑')[0]
                # 更新数据库
                cursor.execute("UPDATE sina_finance_news SET content = %s WHERE id = %s", (new_content, news_id))
                count += 1
        
        conn.commit()
        logger.info(f"成功处理了 {count} 条内容")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"处理失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    process_existing_content()
