import logging
import os
import datetime


class Logger:

    LOGGER_NAME = "myLogger"

    def __init__(self):
        """
        获取参数并记录到文件中
        """

        present_time = datetime.datetime.now()
        self.log_name = datetime.datetime.strftime(present_time, '%Y-%m-%d %H-%M-%S')
        # 用当前时间为本次日志命名
        self.path = os.path.join(os.path.abspath(os.path.dirname(__file__)), self.log_name)

        self.logger = logging.getLogger(Logger.LOGGER_NAME)
        self.logger.propagate = False  # 不向root传播，防止重复输出
        self.logger.setLevel(level=logging.DEBUG)  # 设置整体最低层级为debug

        self.formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
        # formatter: 统一的日志输出格式
        # file_handler: 文件输出
        # stream_handler: 控制台输出

        self.file_handler = logging.FileHandler(self.path)
        self.file_handler.setLevel(logging.INFO)
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)

        self.stream_handler = logging.StreamHandler()
        self.stream_handler.setLevel(logging.INFO)
        self.stream_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.stream_handler)

    def log_input(self, level, message, pos=None):
        """
        记录日志信息，level为'debug', 'info', 'warning', 'error', 'critical'，分别用数值1-5表示
        # 颜色分别为白、绿、黄、红、红
        :param level: 信息等级
        :param message: 信息内容
        :param pos: 文件及函数所在位置，run as u_log.log_input(level, message, sys._getframe().f_code)
        """

        message = str(message)
        try:
            message = pos.co_filename + '/' + pos.co_name + ' - ' + message
        except AttributeError:
            pass
            # 未获取日志信息生成所在位置，不记录该信息
        if level == 1:
            self.logger.debug(message)
            # Fore.WHITE + message +Style.RESET_ALL
        elif level == 2:
            self.logger.info(message)
            # Fore.GREEN + message +Style.RESET_ALL
        elif level == 3:
            self.logger.warning(message)
            # Fore.YELLOW + message +Style.RESET_ALL
        elif level == 4:
            self.logger.error(message)
            # Fore.RED + message +Style.RESET_ALL
        elif level == 5:
            self.logger.critical(message)
            # Fore.RED + message +Style.RESET_ALL

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)
