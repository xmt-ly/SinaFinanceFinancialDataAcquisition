import requests
from bs4 import BeautifulSoup
import pymysql
import time
import logging
import re
import sys
from config import DB_CONFIG

# 设置控制台输出编码为UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SinaFinanceSpider:
    def __init__(self):
        self.base_url = "https://finance.sina.com.cn"
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
                charset='utf8mb4',
                use_unicode=True
            )
            self.db_cursor = self.db_conn.cursor()
            logger.info("数据库连接成功")
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            raise
    
    def create_table(self):
        """创建新闻表"""
        sql = """
        CREATE TABLE IF NOT EXISTS sina_finance_news (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            url VARCHAR(255) NOT NULL UNIQUE,
            content TEXT,
            publish_time DATETIME,
            crawl_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        try:
            self.db_cursor.execute(sql)
            self.db_conn.commit()
            logger.info("新闻表创建成功")
        except Exception as e:
            logger.error(f"创建表失败: {e}")
            self.db_conn.rollback()
            raise
    
    def get_news_list(self, page=1):
        """获取新闻列表"""
        url = f"{self.base_url}/roll/?pageid=384&lid=2519&k=&num=50&page={page}"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.encoding = 'utf-8'
            html_content = response.content.decode('utf-8', errors='ignore')
            soup = BeautifulSoup(html_content, 'html.parser')
            
            news_list = []
            # 查找新闻列表（从seo_data_list中提取）
            seo_data_list = soup.find('ul', class_='seo_data_list')
            if seo_data_list:
                news_items = seo_data_list.find_all('li')
                for item in news_items:
                    a_tag = item.select_one('a')
                    if a_tag:
                        title = a_tag.get_text(strip=True)
                        news_url = a_tag.get('href')
                        
                        # 从URL中提取发布时间
                        # URL格式类似：https://finance.sina.com.cn/meeting/2026-04-12/doc-inhufqsh5639201.shtml
                        time_match = re.search(r'/(\d{4}-\d{2}-\d{2})/', news_url)
                        if time_match:
                            date_str = time_match.group(1)
                            # 假设时间为当天的某个默认时间
                            publish_time = f"{date_str} 00:00"
                        else:
                            # 如果URL中没有时间，使用当前日期
                            publish_time = time.strftime("%Y-%m-%d %H:%M")
                        
                        # 过滤掉无效的新闻
                        if title and news_url:
                            news_list.append({
                                'title': title,
                                'url': news_url,
                                'publish_time': publish_time
                            })
            
            logger.info(f"获取到 {len(news_list)} 条新闻")
            return news_list
        except Exception as e:
            import traceback
            logger.error(f"获取新闻列表失败: {e}")
            logger.error(f"详细错误: {traceback.format_exc()}")
            return []
    
    def get_news_content(self, url):
        """获取新闻内容"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找新闻内容
            content_div = soup.select_one('.article-content') or soup.select_one('#artibody')
            if content_div:
                content = ''.join([p.get_text(strip=True) for p in content_div.select('p')])
                return content
            return ''
        except Exception as e:
            logger.error(f"获取新闻内容失败 {url}: {e}")
            return ''
    
    def save_news(self, news):
        """保存新闻到数据库"""
        sql = """
        INSERT IGNORE INTO sina_finance_news (title, url, content, publish_time)
        VALUES (%s, %s, %s, %s)
        """
        try:
            self.db_cursor.execute(sql, (
                news['title'],
                news['url'],
                news['content'],
                news['publish_time']
            ))
            self.db_conn.commit()
            if self.db_cursor.rowcount > 0:
                logger.info(f"保存新闻成功: {news['title']}")
            else:
                logger.info(f"新闻已存在: {news['title']}")
        except Exception as e:
            logger.error(f"保存新闻失败: {e}")
            self.db_conn.rollback()
    
    def run(self, pages=5):
        """运行爬虫"""
        try:
            # 连接数据库
            self.connect_db()
            # 创建表
            self.create_table()
            
            for page in range(1, pages + 1):
                logger.info(f"爬取第 {page} 页")
                # 获取新闻列表
                news_list = self.get_news_list(page)
                
                for news in news_list:
                    # 获取新闻内容
                    news['content'] = self.get_news_content(news['url'])
                    # 保存新闻
                    self.save_news(news)
                    # 避免请求过快
                    time.sleep(1)
                
                # 每页之间休息
                time.sleep(2)
                
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
    spider = SinaFinanceSpider()
    spider.run(pages=3)  # 默认爬取3页
