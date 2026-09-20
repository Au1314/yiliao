"""集中配置：数据库连接 + 智谱 GLM 大模型。

优先读取环境变量，其次读取项目根目录下的 .env 文件，最后使用默认值。
把敏感信息（数据库密码、API Key）从代码里抽出来，避免硬编码。
"""
import os

# 项目根目录（本文件所在目录）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _load_dotenv(path: str) -> None:
    """极简 .env 解析器，避免额外引入 python-dotenv 依赖。"""
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            # 环境变量优先级更高，已存在则不覆盖
            os.environ.setdefault(key, value)


_load_dotenv(os.path.join(BASE_DIR, ".env"))

# ---- 数据库配置 ----
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = int(os.environ.get("DB_PORT", "3306"))
DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
DB_NAME = os.environ.get("DB_NAME", "medicalinfo")
DB_CHARSET = "utf8mb4"

# SQLAlchemy 连接串（tree.py 使用）
DB_URI = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    f"?charset={DB_CHARSET}"
)

# ---- 智谱 GLM 大模型配置 ----
ZHIPU_API_KEY = os.environ.get("ZHIPU_API_KEY", "")
ZHIPU_BASE_URL = os.environ.get(
    "ZHIPU_BASE_URL", "https://open.bigmodel.cn/api/paas/v4"
)
ZHIPU_MODEL = os.environ.get("ZHIPU_MODEL", "glm-4.5-air")
