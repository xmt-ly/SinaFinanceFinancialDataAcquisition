import requests
from bs4 import BeautifulSoup
import pymysql
import time
import logging
import re
import sys
from config import DB_CONFIG

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StockSpider:
    def __init__(self):
        self.base_url = "https://finance.sina.com.cn"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6",
        }
        self.db_conn = None
        self.db_cursor = None
    
    def connect_db(self):
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
        sql = """
        CREATE TABLE IF NOT EXISTS stock_info (
            id INT AUTO_INCREMENT PRIMARY KEY,
            stock_code VARCHAR(20) NOT NULL UNIQUE,
            stock_name VARCHAR(100),
            current_price DECIMAL(10,2),
            change_percent DECIMAL(10,2),
            change_amount DECIMAL(10,2),
            open_price DECIMAL(10,2),
            high_price DECIMAL(10,2),
            low_price DECIMAL(10,2),
            prev_close DECIMAL(10,2),
            volume DECIMAL(20,2),
            amount DECIMAL(20,2),
            market_cap DECIMAL(20,2),
            pe_ratio DECIMAL(10,2),
            turnover_rate DECIMAL(10,2),
            crawl_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        try:
            self.db_cursor.execute(sql)
            self.db_conn.commit()
            logger.info("股票信息表创建成功")
        except Exception as e:
            logger.error(f"创建表失败: {e}")
            self.db_conn.rollback()
            raise
    
    def get_stock_list(self):
        url = f"{self.base_url}/stock/gsgg/"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.encoding = 'utf-8'
            html_content = response.content.decode('utf-8', errors='ignore')
            soup = BeautifulSoup(html_content, 'html.parser')
            
            stock_list = []
            
            # 尝试多种方式获取股票列表
            
            # 方式1: 从页面获取股票链接
            stock_links = soup.find_all('a', href=re.compile(r'/stock/(sh|sz)\d{6}\.shtml'))
            for link in stock_links:
                href = link.get('href')
                if href:
                    match = re.search(r'(sh|sz)(\d{6})\.shtml', href)
                    if match:
                        prefix = match.group(1)
                        code = match.group(2)
                        full_code = f"{prefix}{code}"
                        if full_code not in [s['code'] for s in stock_list]:
                            stock_list.append({'code': full_code, 'name': link.get_text(strip=True)})
            
            logger.info(f"获取到 {len(stock_list)} 只股票")
            return stock_list
        except Exception as e:
            logger.error(f"获取股票列表失败: {e}")
            return []
    
    def get_stock_detail(self, stock_code):
        try:
            # 使用新浪股票API获取实时数据
            api_url = f"https://hq.sinajs.cn/list={stock_code}"
            api_headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
                "Referer": "https://finance.sina.com.cn/stock/",
                "Accept": "*/*",
                "Accept-Language": "zh-CN,zh;q=0.9",
            }
            response = requests.get(api_url, headers=api_headers, timeout=10)
            
            stock_info = {'code': stock_code, 'name': ''}
            
            if response.status_code == 200 and '=' in response.text:
                text = response.text
                data = text.split('=')[1].split(',')
                
                if len(data) > 1:
                    # 解析股票数据
                    stock_info['name'] = data[0].strip('"')
                    stock_info['open_price'] = float(data[1]) if data[1] and data[1] != '0.00' else None
                    stock_info['prev_close'] = float(data[2]) if data[2] and data[2] != '0.00' else None
                    stock_info['current_price'] = float(data[3]) if data[3] and data[3] != '0.00' else None
                    stock_info['high_price'] = float(data[4]) if data[4] and data[4] != '0.00' else None
                    stock_info['low_price'] = float(data[5]) if data[5] and data[5] != '0.00' else None
                    stock_info['volume'] = float(data[8]) if data[8] and data[8] != '0' else None
                    stock_info['amount'] = float(data[9]) if data[9] and data[9] != '0' else None
                    
                    # 计算涨跌额和涨跌幅
                    if stock_info['current_price'] and stock_info['prev_close']:
                        stock_info['change_amount'] = round(stock_info['current_price'] - stock_info['prev_close'], 2)
                        stock_info['change_percent'] = round((stock_info['change_amount'] / stock_info['prev_close']) * 100, 2)
            
            logger.info(f"股票: {stock_info['name']}, 价格: {stock_info.get('current_price')}, 涨跌: {stock_info.get('change_percent')}%")
            
            return stock_info
        except Exception as e:
            logger.error(f"获取股票详情失败 {stock_code}: {e}")
            return None
    
    def save_stock(self, stock_info):
        if not stock_info:
            return
        
        sql = """
        INSERT INTO stock_info (
            stock_code, stock_name, current_price, change_percent, 
            change_amount, open_price, high_price, low_price, 
            prev_close, volume, amount, market_cap, pe_ratio, turnover_rate
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            stock_name = VALUES(stock_name),
            current_price = VALUES(current_price),
            change_percent = VALUES(change_percent),
            change_amount = VALUES(change_amount),
            open_price = VALUES(open_price),
            high_price = VALUES(high_price),
            low_price = VALUES(low_price),
            prev_close = VALUES(prev_close),
            volume = VALUES(volume),
            amount = VALUES(amount)
        """
        try:
            self.db_cursor.execute(sql, (
                stock_info.get('code', ''),
                stock_info.get('name', ''),
                stock_info.get('current_price'),
                stock_info.get('change_percent'),
                stock_info.get('change_amount'),
                stock_info.get('open_price'),
                stock_info.get('high_price'),
                stock_info.get('low_price'),
                stock_info.get('prev_close'),
                stock_info.get('volume'),
                stock_info.get('amount'),
                stock_info.get('market_cap'),
                stock_info.get('pe_ratio'),
                stock_info.get('turnover_rate')
            ))
            self.db_conn.commit()
            logger.info(f"保存股票成功: {stock_info.get('code')} - {stock_info.get('name')}")
        except Exception as e:
            logger.error(f"保存股票失败: {e}")
            self.db_conn.rollback()
    
    def run(self, stock_codes=None):
        try:
            self.connect_db()
            self.create_table()
            
            if stock_codes is None:
                # 获取股票列表
                stock_list = self.get_stock_list()
                stock_codes = [s['code'] for s in stock_list]
            
            # 爬取每只股票的详情
            for i, code in enumerate(stock_codes):
                logger.info(f"爬取股票 {i+1}/{len(stock_codes)}: {code}")
                stock_info = self.get_stock_detail(code)
                if stock_info:
                    self.save_stock(stock_info)
                time.sleep(1)
            
            logger.info("爬虫运行结束")
        except Exception as e:
            logger.error(f"爬虫运行失败: {e}")
        finally:
            if self.db_cursor:
                self.db_cursor.close()
            if self.db_conn:
                self.db_conn.close()

if __name__ == "__main__":
    spider = StockSpider()
    # 指定常用股票代码列表测试
    stock_codes = [
        'sh600519',  # 贵州茅台
        'sz000001',  # 平安银行
        'sh601318',  # 中国平安
        'sh600036',  # 招商银行
        'sh600900',  # 长江电力
        'sz000002',  # 万科A
        'sh601888',  # 中国中免
        'sh600276',  # 恒瑞医药
    ]
    spider.run(stock_codes=stock_codes)
