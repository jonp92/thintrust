import os
import sys
import json
import subprocess
from thintrust import ThinTrust

class InitialSetup(ThinTrust):
    def __init__(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        setup_file = f'{script_dir}/setup.json'
        super().__init__()
        self.logger.name = 'InitialSetup'
        self.logger.info('Starting initial setup...')
        self.setup_configuration = json.load(open(setup_file)) if os.path.exists(setup_file) else None
        if not self.setup_configuration:
            print('Setup file not found. Please create a setup.json file.')
            exit(1)
        sanity = self.sanity_check()
        if sanity is not True:
            self.logger.error(f"Sanity check failed: {sanity['error']}")
            exit(1)
    
    def sanity_check(self):
        supported_cpus = ['x86_64']
        if self.system_profiler['cpu']['architecture'] not in supported_cpus:
            self.logger.error(f'Unsupported CPU architecture: {self.system_profiler["cpu"]["architecture"]}')
            return {'error': 'Unsupported CPU architecture'}
        else:
            self.logger.info(f'CPU architecture Supported: {self.system_profiler["cpu"]["architecture"]}')
        if self.system_profiler['disks'] is None:
            self.logger.error('No disks found.')
            return {'error': 'No disks found'}
        disk_sizes = [round(disk['size'] / (1024 ** 3)) for disk in self.system_profiler['disks']]
        self.logger.info(f'Disk sizes: {disk_sizes}')
        if not any(size >= 25 for size in disk_sizes):
            self.logger.error('No 32GB disk found.')
            return {'error': 'No 32GB disk found'}
        return True
        
if __name__ == '__main__':
    InitialSetup()