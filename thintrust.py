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
        self.logger.info(f"System CPU: {self.system_profile['cpu']}")
        self.logger.info(f"System BIOS:\n{self.system_profile['bios']}")
        self.logger.info(f"System Memory:\n{self.system_profile['memory']}")
        
        
    def system_profile(self):
        self.logger.info('Collecting system profile...')
        profile = {}
        profile['cpu'] = self.get_cpu_info()
        profile['bios'] = self.get_bios_info()
        profile['memory'] = self.get_system_memory()
        return profile
        
    def get_bios_info(self):
        try:
            bios_info = subprocess.check_output('sudo dmidecode -t bios', shell=True).decode('utf-8').split('BIOS Information')[1].strip()
            bios = {}
            bios['vendor'] = bios_info.split('Vendor: ')[1].split('\n')[0].strip()
            bios['version'] = bios_info.split('Version: ')[1].split('\n')[0].strip()
            bios['release_date'] = bios_info.split('Release Date: ')[1].split('\n')[0].strip()
            bios['is_virtual'] = bios_info.find('System is a virtual machine') != -1
            return bios
        except Exception as e:
            self.logger.error(f'Error getting BIOS info: {e}')
            return None
    
    def get_cpu_info(self):
        try:
            verbose_info = subprocess.check_output('lscpu', shell=True).decode('utf-8').strip()
            architecture = verbose_info.split('Architecture:')[1].split('\n')[0].strip()
            vendor = verbose_info.split('Vendor ID:')[1].split('\n')[0].strip()
            model = verbose_info.split('Model name:')[1].split('\n')[0].strip()
            cores = verbose_info.split('CPU(s):')[1].split('\n')[0].strip()
            threads = verbose_info.split('Thread(s) per core:')[1].split('\n')[0].strip()
            return {'architecture': architecture, 'vendor': vendor, 'model': model, 'cores': cores, 'threads': threads}
        except Exception as e:
            self.logger.error(f'Error getting CPU info: {e}')
            return None
        
    def get_system_memory(self):
        try:
            memory = psutil.virtual_memory()
            human_readable = ['total', 'available', 'used', 'free']
            # convert to GB
            human_readable_values = [round(getattr(memory, attr) / (1024 ** 3), 2) for attr in human_readable]
            return dict(zip(human_readable, human_readable_values))
        except Exception as e:
            self.logger.error(f'Error getting system memory: {e}')
            return None