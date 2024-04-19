import os
import json
from utils.logger import Logger
import psutil
import subprocess

class ThinTrust(Logger):
    def __init__(self):
        self.config = json.load(open('config.json')) if os.path.exists('config.json') else None
        if not self.config:
            print('Config file not found. Please create a config.json file.')
            exit(1)
        for key, value in self.config.items():
            setattr(self, key, value)
        super().__init__('ThinTrust', self.log_file, self.log_level)
        self.logger.info('ThinTrust initialized.')
        self.system_profile = self.system_profile()
        self.logger.info(f"System profile: {self.system_profile['cpu']}")
        
        
    def system_profile(self):
        self.logger.info('Collecting system profile...')
        profile = {}
        profile['cpu'] = self.get_cpu_info()
        profile['bios'] = self.get_bios_info()
        return profile
        
    def get_bios_info(self):
        try:
            bios_info = subprocess.check_output('sudo dmidecode -t bios', shell=True).decode('utf-8').strip()
            return bios_info
        except Exception as e:
            self.logger.error(f'Error getting BIOS info: {e}')
            return None
    
    def get_cpu_info(self):
        try:
            return subprocess.check_output('lscpu', shell=True).decode('utf-8').strip()
        except Exception as e:
            self.logger.error(f'Error getting CPU info: {e}')
            return None