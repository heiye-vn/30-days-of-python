import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

# 最简配置：设置最低级别为 INFO，默认为 WARNING
logging.basicConfig(level=logging.INFO)

# logging.debug("这条不会显示，因为级别低于 INFO")
# logging.info("服务启动成功")
# logging.warning("磁盘空间不足 20%")
# logging.error("数据库连接失败")
# logging.critical("系统崩溃")


"""
核心四大组件

Logger：决定 “记什么”，暴露 info()、error() 等接口
Handler：决定 “写到哪”，控制台、文件、网络，邮件等
Formatter：决定 “长什么样”，时间、级别、消息格式
Filter：决定 “要不要记”，比级别更精细的过滤

关系：Logger 把日志记录交给 Handler，Handler 用 Formatter 格式化后输出，Filter 在两端做拦截
"""

# 推荐：用 __name__ 命名，自动对应模块路径
# logger = logging.getLogger(__name__)
# print(logger.name)

# 也支持自定义名称
logger_self = logging.getLogger("payment.service")
# print(logger_self.name)


"""
五大日志级别及使用场景
DEBUG(10): 开发调试信息，生产环境关闭
INFO(20): 正常运行事件，请求到达、任务完成
WARNING(30): 异常但不影响运行，重试、降级、废弃API（默认，不设置 basicConfig 的话低级别日志不会输出）
ERROR(40): 功能失败，某个请求处理出错
CRITICAL(50): 系统级故障，程序无法继续运行
"""

# 自定义一个新的级别和对应的数值
TRACE_LEVEL = 5
logging.addLevelName(TRACE_LEVEL, "TRACE")


# 封装一个快捷使用的方法
def trace(self, message, *args, **kwargs):
    if self.isEnabledFor(TRACE_LEVEL):
        self._log(TRACE_LEVEL, message, args, **kwargs)


# 绑定到 logging
logging.Logger.trace = trace

# 使用
# logger = logging.getLogger("my_logger")
# logger.setLevel(TRACE_LEVEL)
# logger.trace("这是比 DEBUG 还要详细的 TRACE 级别日志！")


""" 常用 Handler """
# 输出到控制台
console_handler = logging.StreamHandler()

# 输出到文件（追加模式）
file_handler = logging.FileHandler("app.log", encoding="utf-8")

# 按大小滚动：每个文件最大 5MB，保留 3 个备份
rotating_handler = RotatingFileHandler(
    "app.log", maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
)

# 按时间滚动：每天午夜切割，保留 30 天
timed_handler = TimedRotatingFileHandler(
    "app.log", when="midnight", backupCount=30, encoding="utf-8"
)


""" Formatter：统一格式 """
# 基础格式（s：字符串，d：整数，f：浮点数，t：时间戳）
base_fmt = logging.Formatter("%(asctime)s - [%(levelname)s] %(message)s")

# 完整格式
fmt_full = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
