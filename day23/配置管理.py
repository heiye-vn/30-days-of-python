from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# 1. 动态获取当前文件所在目录的 .env 绝对路径，防止因为执行目录（Cwd）不同而找不到文件
CURRENT_DIR = Path(__file__).resolve().parent
ENV_FILE_PATH = CURRENT_DIR / ".env"


class Settings(BaseSettings):
    # 基础配置，自动读取系统环境变量 APP_NAME
    app_name: str = "My Awesome App"
    # 强类型校验
    port: int = 8080

    # 2. 字段名直接与环境变量对应（由 env_prefix="APP_" 自动映射 APP_OPENAI_API_KEY）
    openai_api_key: str

    # 3. 字段名直接与环境变量对应（由 env_prefix="APP_" 自动映射 APP_DATABASE_URL）
    database_url: str

    # 4. 显式声明需要使用的配置字段，确保类型自动转换 (Coercion)
    debug: bool = False
    request_timeout: int = 30

    # 配置读取行为
    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding="utf-8",
        env_prefix="APP_",  # 环境变量统一前缀
        case_sensitive=False,  # 是否区分大小写
        extra="ignore",  # 忽略多余字段，防止无用系统环境变量污染配置对象
        populate_by_name=True,  # 允许使用字段名称进行实例化传参
    )


@lru_cache
def get_settings() -> Settings:
    # 5. 移除了硬编码的传参，完全从 .env / 系统环境变量中读取加载
    return Settings()


settings = get_settings().model_dump()
print(settings)
print(settings["debug"])
