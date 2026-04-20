import requests
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

stock_codes = ['sh600519']

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://finance.sina.com.cn/stock/",
    "Accept": "*/*",
}

for code in stock_codes:
    url = f"https://hq.sinajs.cn/list={code}"
    response = requests.get(url, headers=headers)
    text = response.text
    
    if '=' in text:
        data = text.split('=')[1].split(',')
        print(f"\n=== {code} API Data ===")
        print(f"Total fields: {len(data)}")
        
        # 显示所有字段
        field_names = [
            'name', 'open', 'prev_close', 'current', 'high', 'low',
            'buy_price', 'sell_price', 'volume', 'amount',
            'bid1_vol', 'bid1_price', 'bid2_vol', 'bid2_price',
            'bid3_vol', 'bid3_price', 'bid4_vol', 'bid4_price',
            'bid5_vol', 'bid5_price',
            'ask1_vol', 'ask1_price', 'ask2_vol', 'ask2_price',
            'ask3_vol', 'ask3_price', 'ask4_vol', 'ask4_price',
            'ask5_vol', 'ask5_price',
            'date', 'time', 'unknown'
        ]
        
        for i, name in enumerate(field_names):
            if i < len(data):
                print(f"  {i}: {name} = {data[i]}")
