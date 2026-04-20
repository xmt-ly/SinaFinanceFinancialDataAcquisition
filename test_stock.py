import requests
from bs4 import BeautifulSoup
import re

url = "https://finance.sina.com.cn/stock/sh600519.shtml"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    response.encoding = 'utf-8'
    html_content = response.content.decode('utf-8', errors='ignore')
    soup = BeautifulSoup(html_content, 'html.parser')
    
    print(f"Status: {response.status_code}")
    print(f"URL: {response.url}")
    
    # 查找股票名称
    name_elem = soup.find('h1', id='stockName')
    if not name_elem:
        name_elem = soup.find('h1', class_='stock-name')
    if not name_elem:
        name_elem = soup.find('div', class_='stock-title')
    if not name_elem:
        name_elem = soup.find('span', class_='name')
    print(f"Name element: {name_elem}")
    
    if name_elem:
        print(f"Stock name: {name_elem.get_text(strip=True)}")
    
    # 查找价格
    price_elem = soup.find('span', id='price')
    if not price_elem:
        price_elem = soup.find('span', class_='price')
    if not price_elem:
        price_elem = soup.find('div', class_='price')
    print(f"Price element: {price_elem}")
    
    if price_elem:
        print(f"Price: {price_elem.get_text(strip=True)}")
    
    # 查找所有script中的股票数据
    scripts = soup.find_all('script')
    for script in scripts:
        if script.string and 'hq_str' in script.string:
            print(f"\nFound script with hq_str:")
            print(script.string[:500])
            
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
