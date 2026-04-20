import requests
import pymysql
import time
import logging
import sys
import argparse
from config import DB_CONFIG

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

STOCK_API_URL = "https://hq.sinajs.cn/list="
STOCK_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "Referer": "https://finance.sina.com.cn/stock/",
    "Accept": "*/*",
    "Accept-Language": "zh-CN,zh;q=0.9",
}

STOCK_NAME_MAP = {
    '贵州茅台': 'sh600519', '茅台': 'sh600519',
    '平安银行': 'sz000001', '银行': 'sz000001',
    '中国平安': 'sh601318', '平安': 'sh601318',
    '招商银行': 'sh600036',
    '长江电力': 'sh600900', '电力': 'sh600900',
    '万科A': 'sz000002', '万科': 'sz000002',
    '中国中免': 'sh601888', '中免': 'sh601888',
    '恒瑞医药': 'sh600276', '恒瑞': 'sh600276',
    '五粮液': 'sz000858',
    '美的集团': 'sz000333', '美的': 'sz000333',
    '格力电器': 'sz000651', '格力': 'sz000651',
    '宁德时代': 'sz300750', '宁德': 'sz300750',
    '比亚迪': 'sz002594',
    '中兴通讯': 'sz000063', '中兴': 'sz000063',
    '工商银行': 'sh601398', '工行': 'sh601398',
    '中国石化': 'sh600028', '中石化': 'sh600028',
    '中国石油': 'sh601857', '中石油': 'sh601857',
    '农业银行': 'sh601288', '农行': 'sh601288',
    '建设银行': 'sh601939', '建行': 'sh601939',
    '中国银行': 'sh601988', '中行': 'sh601988',
    '交通银行': 'sh601328',
    '邮储银行': 'sh601658',
    '民生银行': 'sh600016',
    '浦发银行': 'sh600000',
    '兴业银行': 'sh601166',
    '光大银行': 'sh601818',
    '中信银行': 'sh601998',
    '华夏银行': 'sh600015',
    '上证指数': 'sh000001',
    '深证成指': 'sz399001',
    '创业板指': 'sz399006',
    '沪深300': 'sh000300',
}

def connect_db():
    try:
        conn = pymysql.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            charset='utf8mb4',
            use_unicode=True
        )
        cursor = conn.cursor()
        
        # 删除旧表并重建
        cursor.execute("DROP TABLE IF EXISTS stock_info")
        
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
            buy_price DECIMAL(10,2),
            sell_price DECIMAL(10,2),
            bid1_price DECIMAL(10,2), bid1_vol DECIMAL(15,2),
            bid2_price DECIMAL(10,2), bid2_vol DECIMAL(15,2),
            bid3_price DECIMAL(10,2), bid3_vol DECIMAL(15,2),
            bid4_price DECIMAL(10,2), bid4_vol DECIMAL(15,2),
            bid5_price DECIMAL(10,2), bid5_vol DECIMAL(15,2),
            ask1_price DECIMAL(10,2), ask1_vol DECIMAL(15,2),
            ask2_price DECIMAL(10,2), ask2_vol DECIMAL(15,2),
            ask3_price DECIMAL(10,2), ask3_vol DECIMAL(15,2),
            ask4_price DECIMAL(10,2), ask4_vol DECIMAL(15,2),
            ask5_price DECIMAL(10,2), ask5_vol DECIMAL(15,2),
            trade_date DATE,
            trade_time TIME,
            crawl_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        cursor.execute(sql)
        conn.commit()
        
        logger.info("数据库连接成功")
        return conn, cursor
    except Exception as e:
        logger.error(f"数据库连接失败: {e}")
        return None, None

def get_stock_code(user_input):
    user_input = user_input.strip()
    
    if user_input.startswith('sh') or user_input.startswith('sz'):
        if len(user_input) == 8:
            return user_input.lower()
    
    if user_input.isdigit() and len(user_input) == 6:
        if user_input.startswith('6'):
            return f'sh{user_input}'
        elif user_input.startswith(('0', '3')):
            return f'sz{user_input}'
    
    if user_input in STOCK_NAME_MAP:
        return STOCK_NAME_MAP[user_input]
    
    for name, code in STOCK_NAME_MAP.items():
        if user_input in name or name in user_input:
            return code
    
    return None

def get_stock_info(stock_code):
    try:
        url = f"{STOCK_API_URL}{stock_code}"
        response = requests.get(url, headers=STOCK_HEADERS, timeout=10)
        
        if response.status_code == 200 and '=' in response.text:
            text = response.text
            data = text.split('=')[1].split(',')
            
            if len(data) > 30:
                # 解析数据，按照数据库字段顺序
                stock_info = {
                    'stock_code': stock_code,
                    'stock_name': data[0].strip('"'),
                    'current_price': float(data[3]) if data[3] and data[3] != '0.00' else None,
                    'change_percent': None,  # 需要计算
                    'change_amount': None,   # 需要计算
                    'open_price': float(data[1]) if data[1] and data[1] != '0.00' else None,
                    'high_price': float(data[4]) if data[4] and data[4] != '0.00' else None,
                    'low_price': float(data[5]) if data[5] and data[5] != '0.00' else None,
                    'prev_close': float(data[2]) if data[2] and data[2] != '0.00' else None,
                    'volume': float(data[8]) if data[8] and data[8] != '0' else None,
                    'amount': float(data[9]) if data[9] and data[9] != '0' else None,
                    'buy_price': float(data[6]) if data[6] and data[6] != '0.00' else None,
                    'sell_price': float(data[7]) if data[7] and data[7] != '0.00' else None,
                    # 五档买盘
                    'bid1_price': float(data[11]) if len(data) > 11 and data[11] and data[11] != '0.00' else None,
                    'bid1_vol': float(data[10]) if len(data) > 10 and data[10] and data[10] != '0' else None,
                    'bid2_price': float(data[13]) if len(data) > 13 and data[13] and data[13] != '0.00' else None,
                    'bid2_vol': float(data[12]) if len(data) > 12 and data[12] and data[12] != '0' else None,
                    'bid3_price': float(data[15]) if len(data) > 15 and data[15] and data[15] != '0.00' else None,
                    'bid3_vol': float(data[14]) if len(data) > 14 and data[14] and data[14] != '0' else None,
                    'bid4_price': float(data[17]) if len(data) > 17 and data[17] and data[17] != '0.00' else None,
                    'bid4_vol': float(data[16]) if len(data) > 16 and data[16] and data[16] != '0' else None,
                    'bid5_price': float(data[19]) if len(data) > 19 and data[19] and data[19] != '0.00' else None,
                    'bid5_vol': float(data[18]) if len(data) > 18 and data[18] and data[18] != '0' else None,
                    # 五档卖盘
                    'ask1_price': float(data[21]) if len(data) > 21 and data[21] and data[21] != '0.00' else None,
                    'ask1_vol': float(data[20]) if len(data) > 20 and data[20] and data[20] != '0' else None,
                    'ask2_price': float(data[23]) if len(data) > 23 and data[23] and data[23] != '0.00' else None,
                    'ask2_vol': float(data[22]) if len(data) > 22 and data[22] and data[22] != '0' else None,
                    'ask3_price': float(data[25]) if len(data) > 25 and data[25] and data[25] != '0.00' else None,
                    'ask3_vol': float(data[24]) if len(data) > 24 and data[24] and data[24] != '0' else None,
                    'ask4_price': float(data[27]) if len(data) > 27 and data[27] and data[27] != '0.00' else None,
                    'ask4_vol': float(data[26]) if len(data) > 26 and data[26] and data[26] != '0' else None,
                    'ask5_price': float(data[29]) if len(data) > 29 and data[29] and data[29] != '0.00' else None,
                    'ask5_vol': float(data[28]) if len(data) > 28 and data[28] and data[28] != '0' else None,
                    'trade_date': data[30] if len(data) > 30 and data[30] else None,
                    'trade_time': data[31] if len(data) > 31 and data[31] else None,
                }
                
                # 计算涨跌额和涨跌幅
                if stock_info['current_price'] and stock_info['prev_close']:
                    stock_info['change_amount'] = round(stock_info['current_price'] - stock_info['prev_close'], 2)
                    stock_info['change_percent'] = round((stock_info['change_amount'] / stock_info['prev_close']) * 100, 2)
                
                return stock_info
        
        return None
    except Exception as e:
        logger.error(f"获取股票信息失败: {e}")
        return None

def save_to_db(conn, cursor, stock_info):
    try:
        fields = [
            'stock_code', 'stock_name', 'current_price', 'change_percent', 
            'change_amount', 'open_price', 'high_price', 'low_price', 
            'prev_close', 'volume', 'amount', 'buy_price', 'sell_price',
            'bid1_price', 'bid1_vol', 'bid2_price', 'bid2_vol', 'bid3_price', 'bid3_vol',
            'bid4_price', 'bid4_vol', 'bid5_price', 'bid5_vol',
            'ask1_price', 'ask1_vol', 'ask2_price', 'ask2_vol', 'ask3_price', 'ask3_vol',
            'ask4_price', 'ask4_vol', 'ask5_price', 'ask5_vol',
            'trade_date', 'trade_time'
        ]
        
        placeholders = ', '.join(['%s'] * len(fields))
        update_parts = ', '.join([f"{f} = VALUES({f})" for f in fields])
        
        sql = f"""
        INSERT INTO stock_info ({', '.join(fields)})
        VALUES ({placeholders})
        ON DUPLICATE KEY UPDATE {update_parts}
        """
        
        values = [stock_info.get(f) for f in fields]
        
        cursor.execute(sql, values)
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"保存失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def print_stock_info(stock_info):
    print("\n" + "="*60)
    print(f"  {stock_info['stock_name']} ({stock_info['stock_code'].upper()})")
    print("="*60)
    print(f"  【基本行情】")
    print(f"  当前价格: {stock_info['current_price']}")
    print(f"  涨跌额:   {stock_info.get('change_amount', 'N/A')}")
    print(f"  涨跌幅:   {stock_info.get('change_percent', 'N/A')}%")
    print(f"  开盘价:   {stock_info['open_price']}")
    print(f"  昨收价:   {stock_info['prev_close']}")
    print(f"  最高价:   {stock_info['high_price']}")
    print(f"  最低价:   {stock_info['low_price']}")
    print(f"\n  【成交数据】")
    print(f"  成交量:   {stock_info['volume']}")
    print(f"  成交额:   {stock_info['amount']}")
    print(f"\n  【五档买盘】")
    print(f"  买一价: {stock_info.get('bid1_price')}  买一量: {stock_info.get('bid1_vol')}")
    print(f"  买二价: {stock_info.get('bid2_price')}  买二量: {stock_info.get('bid2_vol')}")
    print(f"  买三价: {stock_info.get('bid3_price')}  买三量: {stock_info.get('bid3_vol')}")
    print(f"  买四价: {stock_info.get('bid4_price')}  买四量: {stock_info.get('bid4_vol')}")
    print(f"  买五价: {stock_info.get('bid5_price')}  买五量: {stock_info.get('bid5_vol')}")
    print(f"\n  【五档卖盘】")
    print(f"  卖一价: {stock_info.get('ask1_price')}  卖一量: {stock_info.get('ask1_vol')}")
    print(f"  卖二价: {stock_info.get('ask2_price')}  卖二量: {stock_info.get('ask2_vol')}")
    print(f"  卖三价: {stock_info.get('ask3_price')}  卖三量: {stock_info.get('ask3_vol')}")
    print(f"  卖四价: {stock_info.get('ask4_price')}  卖四量: {stock_info.get('ask4_vol')}")
    print(f"  卖五价: {stock_info.get('ask5_price')}  卖五量: {stock_info.get('ask5_vol')}")
    print(f"\n  【交易时间】")
    print(f"  日期: {stock_info.get('trade_date')} 时间: {stock_info.get('trade_time')}")
    print("="*60 + "\n")

def main():
    parser = argparse.ArgumentParser(description='新浪财经股票查询系统')
    parser.add_argument('stock', nargs='?', help='股票代码或名称')
    parser.add_argument('--save', '-s', action='store_true', help='直接保存到数据库')
    parser.add_argument('--list', '-l', action='store_true', help='显示已保存的股票列表')
    args = parser.parse_args()
    
    conn, cursor = connect_db()
    if not conn:
        return
    
    print("\n" + "="*60)
    print("  新浪财经股票查询系统 (增强版)")
    print("="*60)
    
    if args.list:
        try:
            cursor.execute("SELECT stock_code, stock_name, current_price, change_percent, trade_date FROM stock_info ORDER BY id DESC LIMIT 10")
            rows = cursor.fetchall()
            print("\n已保存的股票列表:")
            print("-" * 60)
            for row in rows:
                print(f"  {row[0]} | {row[1]} | {row[2]} | {row[3]}% | {row[4]}")
            print("-" * 60 + "\n")
        except Exception as e:
            print(f"查询失败: {e}\n")
        return
    
    if not args.stock:
        print("  输入股票代码或名称进行查询")
        print("  支持的格式:")
        print("    - 6位数字代码 (如: 600519)")
        print("    - 完整代码 (如: sh600519)")
        print("    - 股票名称 (如: 贵州茅台)")
        print("  使用 --save 或 -s 自动保存到数据库")
        print("  使用 --list 或 -l 查看已保存列表")
        print("="*60 + "\n")
        return
    
    stock_code = get_stock_code(args.stock)
    
    if not stock_code:
        print(f"未找到股票: {args.stock}，请尝试其他输入方式\n")
        return
    
    print(f"正在查询: {stock_code} ...")
    stock_info = get_stock_info(stock_code)
    
    if stock_info:
        print_stock_info(stock_info)
        
        if args.save:
            if save_to_db(conn, cursor, stock_info):
                print("保存成功!\n")
            else:
                print("保存失败\n")
        else:
            save = input("是否保存到数据库? (y/n): ").strip().lower()
            if save == 'y' or save == 'yes' or save == '':
                if save_to_db(conn, cursor, stock_info):
                    print("保存成功!\n")
                else:
                    print("保存失败\n")
    else:
        print(f"无法获取股票信息: {stock_code}\n")
    
    if cursor:
        cursor.close()
    if conn:
        conn.close()

if __name__ == "__main__":
    main()
