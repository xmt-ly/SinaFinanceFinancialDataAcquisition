import requests
from bs4 import BeautifulSoup

url = "https://finance.sina.com.cn/roll/?pageid=384&lid=2519&k=&num=50&page=1"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    # 自动检测编码
    response.encoding = response.apparent_encoding
    
    # 解析页面
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 查找新闻列表容器
    print("Looking for news list...")
    
    # 查找包含新闻的主要容器
    main_content = soup.find('div', class_='partMain')
    if main_content:
        print("Found main content div")
        
        # 查找新闻列表
        news_list = main_content.find('ul')
        if news_list:
            print(f"Found news list ul with {len(news_list.find_all('li'))} items")
            
            # 打印前5个新闻项的完整内容
            print("\nFirst 5 news items:")
            for i, item in enumerate(news_list.find_all('li')[:5]):
                print(f"\n{item.prettify()}")
        else:
            print("No news list ul found")
    else:
        print("No main content div found")
        
    # 查找所有的时间标签
    print("\nLooking for time elements...")
    time_elements = soup.find_all(['span', 'time'], class_=True)
    for i, time_elem in enumerate(time_elements[:10]):
        print(f"{i+1}: {time_elem.get('class')} - {time_elem.get_text(strip=True)}")
        
except Exception as e:
    print(f"Error: {e}")
