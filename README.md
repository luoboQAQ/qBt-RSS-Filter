# qBt-RSS-Filter

一个简单的 Python 脚本，用于过滤 RSS 订阅源中的种子，并根据文件大小自动推送到 qBittorrent 下载。

## 功能特性

*   **大小过滤**：支持设置最小和最大文件大小（MB）。
*   **智能解析**：自动从标题（如 `[4.82 GiB]`）或 RSS 附件信息中提取文件大小。
*   **自动去重**：使用 `history.json` 记录已添加的种子，避免重复下载。
*   **灵活配置**：支持自定义下载分类、保存路径及 qBittorrent 连接信息。

## 快速开始

本项目使用 [uv](https://github.com/astral-sh/uv) 进行依赖管理。

### 1. 配置环境

1.  克隆或下载本项目。
2.  复制 `.env` 配置文件模板（首次运行会自动生成，也可手动创建）：

    ```ini
    RSS_URL='您的RSS订阅地址'
    QBT_HOST='127.0.0.1'
    QBT_PORT=8080
    QBT_USER='admin'
    QBT_PASS='adminadmin'
    
    # 过滤设置
    MIN_SIZE_MB=200
    MAX_SIZE_MB=5120
    
    # 下载设置
    DOWNLOAD_CATEGORY='刷下载'
    DOWNLOAD_PATH='/data/Downloads/刷下载'
    ```

### 2. 运行

使用 `uv`直接运行（会自动安装依赖）：

```bash
uv run main.py
```

或者创建虚拟环境运行：

```bash
uv init
uv sync
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
python main.py
```

## 依赖

*   feedparser
*   qbittorrent-api
*   python-dotenv
