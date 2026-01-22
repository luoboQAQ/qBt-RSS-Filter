import feedparser
import re
from qbittorrentapi import Client

import os
import json
from dotenv import load_dotenv

load_dotenv()

# --- 配置部分 ---
RSS_URL = os.getenv('RSS_URL', 'None')
QBT_HOST = os.getenv('QBT_HOST', 'None')
QBT_PORT = int(os.getenv('QBT_PORT', 8080))
QBT_USER = os.getenv('QBT_USER', 'None')
QBT_PASS = os.getenv('QBT_PASS', 'None')

if RSS_URL == 'None' or QBT_HOST == 'None' or QBT_USER == 'None' or QBT_PASS == 'None':
    print("请先配置 .env 文件")
    exit()

HISTORY_FILE = 'history.json'

# 筛选范围 (单位: MB)
MIN_SIZE_MB = float(os.getenv('MIN_SIZE_MB', 200))
MAX_SIZE_MB = float(os.getenv('MAX_SIZE_MB', 2048))

# 下载设置
DOWNLOAD_CATEGORY = os.getenv('DOWNLOAD_CATEGORY', '刷下载')
DOWNLOAD_PATH = os.getenv('DOWNLOAD_PATH', '/data/Downloads/刷下载') 

def parse_size_to_mb(text):
    """
    从字符串中提取大小并统一转换为 MB。
    例如: "[1.5 GB]" -> 1536.0, "[500 MiB]" -> 500.0
    """
    # 匹配类似 [4.82 GiB] 的格式
    match = re.search(r'\[\s*(\d+(?:\.\d+)?)\s*([GM]i?B)\s*\]', text, re.IGNORECASE)
    if not match:
        return None
    
    value = float(match.group(1))
    unit = match.group(2).upper()
    
    if 'G' in unit:
        return value * 1024
    elif 'M' in unit:
        return value
    return None

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def save_history(history):
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(history), f, ensure_ascii=False, indent=2)

def main():
    # 1. 连接 qBittorrent
    try:
        qbt_client = Client(host=QBT_HOST, port=QBT_PORT, username=QBT_USER, password=QBT_PASS)
        qbt_client.auth_log_in()
        print("成功连接到 qBittorrent")
    except Exception as e:
        print(f"连接失败: {e}")
        return

    # 2. 解析 RSS
    print(f"正在读取 RSS: {RSS_URL}")
    feed = feedparser.parse(RSS_URL)
    
    history = load_history()
    print(f"已加载历史记录: {len(history)} 条")

    added_count = 0

    for entry in feed.entries:
        # 获取唯一标识符 (优先使用 id, 其次 link)
        unique_id = entry.get('id', entry.link)
        
        if unique_id in history:
            # print(f"跳过已存在: {entry.title}") 
            continue
        # 尝试从标题中提取大小信息 (格式如 [4.82 GiB])
        size_mb = parse_size_to_mb(entry.get('title', ''))
        
        # 如果 summary 里没有，尝试找附件标签 (enclosure) 中的 length
        if size_mb is None and 'enclosures' in entry:
            for enc in entry.enclosures:
                if 'length' in enc:
                    size_mb = int(enc.length) / (1024 * 1024)
                    break

        if size_mb:
            if MIN_SIZE_MB <= size_mb <= MAX_SIZE_MB:
                print(f"符合条件: [{size_mb:.2f} MB] {entry.title}")
                
                # 3. 推送到 qBittorrent
                download_url = entry.enclosures[0].href
                try:
                    qbt_client.torrents_add(urls=download_url, category=DOWNLOAD_CATEGORY, save_path=DOWNLOAD_PATH, content_layout='Original')
                    print(f"推送成功: {entry.title}")
                    added_count += 1
                    history.add(unique_id)
                    save_history(history)
                except Exception as e:
                    print(f"推送失败: {entry.title}, 错误: {e}")
        else:
            pass

    print(f"--- 任务完成，共添加了 {added_count} 个种子 ---")

if __name__ == "__main__":
    main()