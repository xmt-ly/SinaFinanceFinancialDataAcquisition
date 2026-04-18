import requests
from bs4 import BeautifulSoup

url = "https://finance.sina.com.cn/roll/?pageid=384&lid=2519&k=&num=50&page=1"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6",
}

try:
    print("1. 发送请求...")
    response = requests.get(url, headers=headers, timeout=10)
    print(f"2. 响应状态码: {response.status_code}")
    print(f"3. 响应编码: {response.encoding}")
    print(f"4. 响应内容长度: {len(response.content)}")
    
    print("5. 解码内容...")
    # 先尝试用gbk解码，如果失败就用utf-8
    try:
        text = response.content.decode('gbk', errors='replace')
    except:
        text = response.content.decode('utf-8', errors='replace')
    
    print("6. 解析HTML...")
    soup = BeautifulSoup(text, 'html.parser')
    
    print("7. 查找seo_data_list...")
    seo_data_list = soup.find('ul', class_='seo_data_list')
    if seo_data_list:
        print(f"8. 找到seo_data_list，获取新闻项...")
        news_items = seo_data_list.find_all('li')
        print(f"9. 找到 {len(news_items)} 条新闻")
        
        for i, item in enumerate(news_items[:3]):
            a_tag = item.select_one('a')
            if a_tag:
                title = a_tag.get_text(strip=True)
                print(f"   新闻 {i+1}: {title[:50]}")
    else:
        print("未找到seo_data_list")
        
except Exception as e:
    import traceback
    print(f"错误: {e}")
    traceback.print_exc()
