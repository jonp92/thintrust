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
            self.logger.debug(f'CPU architecture Supported: {self.system_profiler["cpu"]["architecture"]}')
        if self.system_profiler['disks'] is None:
            self.logger.error('No disks found.')
            return {'error': 'No disks found'}
        disk_sizes = [round(disk['size'] / (1024 ** 3)) for disk in self.system_profiler['disks']]
        self.logger.debug(f'Disk sizes: {disk_sizes}')
        if not any(size >= self.min_disk_space for size in disk_sizes):
            self.logger.error('No 32GB disk found.')
            return {'error': 'No 32GB disk found'}
        return True
    
    def setup_overlayroot(self):
        self.logger.info('Setting up overlayroot...')
        try:
            subprocess.check_output('sudo apt-get install -y overlayroot', shell=True)
            subprocess.check_output('sudo overlayroot-chroot', shell=True)
            self.logger.info('Overlayroot installation completed.')
            with open('/etc/default/grub', 'r') as f:
                lines = f.readlines()
            with open('/etc/default/grub', 'w') as f:
                for i, line in enumerate(lines):
                    if 'GRUB_CMDLINE_LINUX_DEFAULT' in line:
                        if 'overlayroot=tmpfs' not in line:
                            line = line.rstrip() + ' overlayroot=tmpfs"'
                        if 'quiet' not in line:
                            line = line.rstrip() + ' quiet"'
                        if 'splash' not in line:
                            line = line.rstrip() + ' splash"'
                        if 'loglevel=3' not in line:
                            line = line.rstrip() + ' loglevel=3"'
                        lines[i] = line + '\n'
                if not any('GRUB_CMDLINE_LINUX_DEFAULT' in line for line in lines):
                    lines.append('GRUB_CMDLINE_LINUX_DEFAULT="quiet splash loglevel=3 overlayroot=tmpfs"\n')
                f.writelines(lines)
            subprocess.check_output('sudo update-grub', shell=True)
            self.logger.info('Overlayroot setup completed. GRUB updated.')
        except Exception as e:
            self.logger.error(f'Error setting up overlayroot: {e}')
        
if __name__ == '__main__':
    InitialSetup()