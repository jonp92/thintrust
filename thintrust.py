import os
import json
from utils.logger import Logger
import psutil
import subprocess
from utils.system_profiler import SystemProfiler

class ThinTrust(Logger):
    def __init__(self):
        if os.geteuid() != 0:
            print('ThinTrust must be run as root. Please run with sudo or as root.')
            exit(1)
        self.config = json.load(open('config.json')) if os.path.exists('config.json') else None
        if not self.config:
            print('Config file not found. Please create a config.json file.')
            exit(1)
        for key, value in self.config.items():
            setattr(self, key, value)
        super().__init__('ThinTrust', self.log_file, self.log_level)
        self.logger.info('ThinTrust initialized.')
        self.system_profiler = SystemProfiler(self.logger).system_profile