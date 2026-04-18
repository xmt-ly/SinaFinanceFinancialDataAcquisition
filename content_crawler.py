import requests
from bs4 import BeautifulSoup
import pymysql
import time
import logging
from config import DB_CONFIG

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ContentCrawler:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6",
            "Cache-Control": "max-age=0",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Priority": "u=0, i",
            "Sec-Ch-Ua": "\"Chromium\";v=\"146\", \"Not-A.Brand\";v=\"24\", \"Google Chrome\";v=\"146\"",
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": "\"Windows\""
        }
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
    
    def get_news_urls(self, limit=100):
        """从数据库中获取新闻URL"""
        sql = "SELECT id, url FROM sina_finance_news WHERE content IS NULL OR content = '' LIMIT %s"
        try:
            self.db_cursor.execute(sql, (limit,))
            return self.db_cursor.fetchall()
        except Exception as e:
            logger.error(f"获取新闻URL失败: {e}")
            return []
    
    def get_news_content(self, url):
        """爬取新闻内容"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10, allow_redirects=True)
            
            # 检查是否返回404错误
            if response.status_code == 404:
                logger.warning(f"URL返回404错误: {url}")
                return "内容不可用（页面不存在）"
            
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 使用用户提供的XPath路径对应的CSS选择器
            # //div[@id="artibody"]//p 对应 .artibody p
            content_div = soup.find('div', id='artibody')
            
            # 如果没有找到artibody，尝试其他可能的内容容器
            if not content_div:
                # 尝试article标签
                content_div = soup.find('article')
                # 尝试其他常见的内容容器类
                if not content_div:
                    content_div = soup.find('div', class_='article-content')
                if not content_div:
                    content_div = soup.find('div', class_='content')
            
            if content_div:
                paragraphs = content_div.find_all('p')
                content = ''.join([p.get_text(strip=True) for p in paragraphs])
                
                # 删除责任编辑及其后面的内容
                editor_keyword = '责任编辑'
                if editor_keyword in content:
                    content = content.split(editor_keyword)[0]
                
                return content
            return "内容不可用（未找到内容容器）"
        except Exception as e:
            logger.error(f"爬取新闻内容失败 {url}: {e}")
            return f"内容不可用（错误: {str(e)}"
    
    def update_content(self, news_id, content):
        """更新数据库中的新闻内容"""
        sql = "UPDATE sina_finance_news SET content = %s WHERE id = %s"
        try:
            self.db_cursor.execute(sql, (content, news_id))
            self.db_conn.commit()
            logger.info(f"更新新闻内容成功，ID: {news_id}")
        except Exception as e:
            logger.error(f"更新新闻内容失败: {e}")
            self.db_conn.rollback()
    
    def run(self, limit=100):
        """运行爬虫"""
        try:
            # 连接数据库
            self.connect_db()
            
            # 获取新闻URL
            news_urls = self.get_news_urls(limit)
            logger.info(f"获取到 {len(news_urls)} 条需要爬取内容的新闻")
            
            # 爬取内容并更新数据库
            for news_id, url in news_urls:
                logger.info(f"爬取新闻内容: {url}")
                content = self.get_news_content(url)
                if content:
                    self.update_content(news_id, content)
                else:
                    logger.warning(f"未获取到新闻内容: {url}")
                # 避免请求过快
                time.sleep(1)
                
        except Exception as e:
            logger.error(f"爬虫运行失败: {e}")
        finally:
            # 关闭数据库连接
            if self.db_cursor:
                self.db_cursor.close()
            if self.db_conn:
                self.db_conn.close()
            logger.info("爬虫运行结束")

if __name__ == "__main__":
    crawler = ContentCrawler()
    crawler.run(limit=50)  # 默认爬取50条新闻的内容
