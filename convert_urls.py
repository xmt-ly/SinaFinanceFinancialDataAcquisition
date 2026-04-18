import pymysql
import urllib.parse
from config import DB_CONFIG
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class URLConverter:
    def __init__(self):
        self.db_conn = None
        self.db_cursor = None
    
    def connect_db(self):
        """连接数据库"""
        try:
            self.db_conn = pymysql.connect(
                host=DB_CONFIG['host'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                database=DB_CONFIG['database'],
                charset='utf8mb4'
            )
            self.db_cursor = self.db_conn.cursor()
            logger.info("数据库连接成功")
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            raise
    
    def get_cj_urls(self):
        """获取所有cj.sina.cn格式的URL"""
        sql = "SELECT id, url FROM sina_finance_news WHERE url LIKE 'https://cj.sina.cn/article/norm_detail%'"
        try:
            self.db_cursor.execute(sql)
            return self.db_cursor.fetchall()
        except Exception as e:
            logger.error(f"获取URL失败: {e}")
            return []
    
    def convert_url(self, cj_url):
        """将cj.sina.cn格式的URL转换为finance.sina.com.cn格式"""
        try:
            # 提取url参数
            if '?url=' in cj_url:
                url_param = cj_url.split('?url=')[1]
                # URL解码
                real_url = urllib.parse.unquote(url_param)
                # 添加来源标记
                if '?' not in real_url:
                    real_url += '?cref=cj'
                else:
                    real_url += '&cref=cj'
                return real_url
            return cj_url
        except Exception as e:
            logger.error(f"转换URL失败 {cj_url}: {e}")
            return cj_url
    
    def update_url(self, news_id, new_url):
        """更新数据库中的URL"""
        sql = "UPDATE sina_finance_news SET url = %s WHERE id = %s"
        try:
            self.db_cursor.execute(sql, (new_url, news_id))
            self.db_conn.commit()
            logger.info(f"更新URL成功，ID: {news_id}")
        except Exception as e:
            logger.error(f"更新URL失败: {e}")
            self.db_conn.rollback()
    
    def run(self):
        """运行转换"""
        try:
            # 连接数据库
            self.connect_db()
            
            # 获取cj.sina.cn格式的URL
            cj_urls = self.get_cj_urls()
            logger.info(f"获取到 {len(cj_urls)} 条需要转换的URL")
            
            # 转换并更新URL
            for news_id, cj_url in cj_urls:
                new_url = self.convert_url(cj_url)
                if new_url != cj_url:
                    self.update_url(news_id, new_url)
                else:
                    logger.warning(f"URL转换失败，保持原URL: {cj_url}")
            
        except Exception as e:
            logger.error(f"转换失败: {e}")
        finally:
            # 关闭数据库连接
            if self.db_cursor:
                self.db_cursor.close()
            if self.db_conn:
                self.db_conn.close()
            logger.info("转换完成")

if __name__ == "__main__":
    converter = URLConverter()
    converter.run()
