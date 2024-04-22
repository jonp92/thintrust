import subprocess
import socket

class SystemProfiler:
    def __init__(self, logger=None):
        self.logger = logger
        self.system_profile = self.system_profile()
        
    def system_profile(self):
        self.logger.debug('Collecting system profile...')
        profile = {}
        profile['hostname'] = socket.gethostname()
        profile['cpu'] = self.get_cpu_info()
        profile['bios'] = self.get_bios_info()
        profile['memory'] = self.get_system_memory()
        profile['disks'] = self.get_disks()
        return profile
        
    def get_bios_info(self):
        try:
            bios_info = subprocess.check_output('dmidecode -t bios', shell=True).decode('utf-8').split('BIOS Information')[1].strip()
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
        
    def get_system_memory(self, human_readable=False):
        import psutil
        try:
            memory = psutil.virtual_memory()
            if not human_readable:
                return {'total': memory.total, 'available': memory.available, 'used': memory.used, 'free': memory.free}
            else:
                human_readable = ['total', 'available', 'used', 'free']
                if memory.total < 1024 ** 2:
                    # if less than 1MB, show in KB
                    human_readable_values = [str(round(getattr(memory, attr) / 1024, 2)) + " KB" for attr in human_readable]
                elif memory.total < 1024 ** 3:
                    # if less than 1GB, show in MB
                    human_readable_values = [str(round(getattr(memory, attr) / (1024 ** 2), 2)) + " MB" for attr in human_readable]
                elif memory.total < 1024 ** 4:
                    # if less than 1TB, show in GB
                    human_readable_values = [str(round(getattr(memory, attr) / (1024 ** 3), 2)) + " GB" for attr in human_readable]
                else:
                    # if more than 1TB, show in TB
                    human_readable_values = [str(round(getattr(memory, attr) / (1024 ** 4), 2)) + " TB" for attr in human_readable]
                return dict(zip(human_readable, human_readable_values))
        except Exception as e:
            self.logger.error(f'Error getting system memory: {e}')
            return None
        
    def get_disks(self):
        import psutil
        try:
            disks = []
            for disk in psutil.disk_partitions():
                disk_info = {}
                disk_info['device'] = disk.device
                disk_info['mountpoint'] = disk.mountpoint
                disk_info['fstype'] = disk.fstype
                disk_info['opts'] = disk.opts
                disk_info['usage'] = psutil.disk_usage(disk.mountpoint)
                disk_info['size'] = disk_info['usage'].total
                disks.append(disk_info)
            return disks
        except Exception as e:
            self.logger.error(f'Error getting disk info: {e}')
            return None