import logging
import os
import sys
from logging.handlers import RotatingFileHandler

class Logger:
    def __init__(self, name, log_file, log_level, max_bytes=10485760, backup_count=20):
        self.name = name
        self.log_file = log_file
        self.log_level = log_level
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(self.log_level)
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        if not os.path.exists("log"):
            os.makedirs("log")
        self.file_handler = RotatingFileHandler(f"log/{self.log_file}", maxBytes=max_bytes, backupCount=backup_count)
        self.file_handler.setLevel(self.log_level)
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)
        self.console_handler = logging.StreamHandler(sys.stdout)
        self.console_handler.setLevel(self.log_level)
        self.console_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.console_handler)
        
if __name__ == "__main__":
    logger = Logger("test", "test.log", "DEBUG")
    logger.logger.debug("This is a debug message")
    logger.logger.info("This is an info message")
    logger.logger.warning("This is a warning message")
    logger.logger.error("This is an error message")
    logger.logger.critical("This is a critical message")
    logger.logger.log(logging.DEBUG, "This is a debug message")
    logger.logger.log(logging.INFO, "This is an info message")
    logger.logger.log(logging.WARNING, "This is a warning message")
    logger.logger.log(logging.ERROR, "This is an error message")
    logger.logger.log(logging.CRITICAL, "This is a critical message")
    logger.logger.log(0, "This is a custom level message")
    logger.logger.log(100, "This is a custom level message")
    logger.logger.log(200, "This is a custom level message")
    logger.logger.log(300, "This is a custom level message")
    logger.logger.log(400, "This is a custom level message")
    logger.logger.log(500, "This is a custom level message")
    logger.logger.log(600, "This is a custom level message")
    logger.logger.log(700, "This is a custom level message")
    logger.logger.log(800, "This is a custom level message")
    logger.logger.log(900, "This is a custom level message")
    logger.logger.log(1000, "This is a custom level message")
    logger.logger.log(1100, "This is a custom level message")
    logger.logger.log(1200, "This is a custom level message")
    logger.logger.log(1300, "This is a custom level message")
    logger.logger.log(1400, "This is a custom level message")
    logger.logger.log(1500, "This is a custom level message")
    logger.logger.log(1600, "This is a custom level message")
    logger.logger.log(1700, "This is a custom level message")
    logger.logger.log(1800, "This is a custom level message")
    logger.logger.log(1900, "This is a custom level message")
    logger.logger.log(2000, "This is a custom level message")