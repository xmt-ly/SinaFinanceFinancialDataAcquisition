<<<<<<< HEAD
# 新浪财经新闻爬虫

这是一个爬取新浪财经新闻并存储到MySQL数据库的Python爬虫。

## 功能特性
- 自动爬取新浪财经新闻列表
- 提取新闻标题、URL、发布时间和内容
- 自动存储到MySQL数据库
- 支持错误处理和日志记录
- 避免重复存储（基于URL唯一性）

## 环境要求
- Python 3.6+
- MySQL 5.7+
- 所需Python包：
  - requests
  - beautifulsoup4
  - pymysql

## 安装步骤

1. **克隆项目**
   ```bash
   git clone <项目地址>
   cd 新浪财经数据爬取
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置数据库**
   - 确保MySQL服务已启动
   - 创建数据库：
     ```sql
     CREATE DATABASE sina_finance;
     ```
   - 修改 `config.py` 文件中的数据库配置：
     ```python
     DB_CONFIG = {
         'host': 'localhost',  # 数据库主机地址
         'user': 'root',       # 数据库用户名
         'password': '123456', # 数据库密码
         'database': 'sina_finance'  # 数据库名称
     }
     ```

4. **运行爬虫**
   ```bash
   python main.py
   ```

## 数据库表结构

爬虫会自动创建以下表结构：

```sql
CREATE TABLE IF NOT EXISTS sina_finance_news (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    url VARCHAR(255) NOT NULL UNIQUE,
    content TEXT,
    publish_time DATETIME,
    crawl_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

## 运行参数

在 `main.py` 文件中，你可以修改以下参数：

- `pages`：要爬取的页数，默认为3页
- `time.sleep()`：控制请求间隔，避免被反爬

## 注意事项

1. 请遵守网站的 robots.txt 规则
2. 不要过度频繁爬取，以免给网站服务器造成压力
3. 本爬虫仅用于学习和研究目的
4. 确保你的MySQL服务已正常运行

## 故障排除

- **数据库连接失败**：检查MySQL服务是否启动，用户名和密码是否正确
- **爬取失败**：检查网络连接，或调整请求间隔
- **数据存储失败**：检查数据库权限和表结构

## 示例输出

运行爬虫后，你会看到类似以下的日志输出：

```
2024-01-01 12:00:00,000 - INFO - 数据库连接成功
2024-01-01 12:00:00,000 - INFO - 新闻表创建成功
2024-01-01 12:00:00,000 - INFO - 爬取第 1 页
2024-01-01 12:00:01,000 - INFO - 获取到 20 条新闻
2024-01-01 12:00:02,000 - INFO - 保存新闻成功: 央行降准0.5个百分点 释放长期资金约1.2万亿元
2024-01-01 12:00:03,000 - INFO - 保存新闻成功: 2024年A股市场展望：结构性机会凸显
...
2024-01-01 12:00:30,000 - INFO - 爬虫运行结束
```
=======
# SinaFinanceFinancialDataAcquisition
这是一个用于爬取新浪财经新闻并存储到MySQL数据库的Python爬虫。该项目旨在帮助用户自动获取和存储新浪财经网站上的最新新闻数据。
>>>>>>> e804b5cad9fe3e8ac523e2b2a3c2413260fb46bb
