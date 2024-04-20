import os
import sys
import json
import shutil
import subprocess
import requests
from thintrust import ThinTrust
#from utils.sevenzip import SevenZip

class InitialSetup(ThinTrust):
    def __init__(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        setup_file = f'{script_dir}/setup.json'
        super().__init__()
        self.logger.name = 'InitialSetup'
        self.logger.info('Starting initial setup...')
        #self.sevenzip = SevenZip()
        self.setup_config = json.load(open(setup_file)) if os.path.exists(setup_file) else None
        if not self.setup_config:
            print('Setup file not found. Please create a setup.json file.')
            exit(1)
        sanity = self.sanity_check()
        if sanity is not True:
            self.logger.error(f"Sanity check failed: {sanity['error']}")
            exit(1)
        self.setup_overlayroot()
        self.rebrand_os()
    
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
            result = subprocess.check_output('apt install -y overlayroot', shell=True)
            if 'overlayroot is already the newest version' in result.decode('utf-8'):
                self.logger.info('Overlayroot already installed, skipping...')
                return
            subprocess.check_output('overlayroot-chroot', shell=True)
            self.logger.info('Overlayroot installation completed.')
        except Exception as e:
            self.logger.error(f'Error setting up overlayroot: {e}')
            
    def rebrand_os(self):
        self.logger.info('Rebranding OS...')
        def install_rebrand_packages(self):
            try:
                packages = self.setup_config['rebrand_os_packages']
                self.logger.debug(f'Installing rebrand packages: {packages}')
                subprocess.check_output(f'apt install -y {" ".join(packages)}', shell=True)
                return True
            except Exception as e:
                self.logger.error(f'Error installing rebrand packages: {e}')
                return False
        def change_issue(self):
            try:
                with open('/etc/issue', 'w') as f:
                    f.write(f"ThinTrust GNU/Linux {self.distro_version} \n \l")
                with open('/etc/issue.net', 'w') as f:
                    f.write(f"ThinTrust GNU/Linux {self.distro_version}")
                return True
            except Exception as e:
                self.logger.error(f'Error changing issue files: {e}')
                return False
            
        def change_os_release(self):
            try:
                with open('/etc/os-release', 'w') as f:
                    f.write('''PRETTY_NAME="ThinTrust GNU/Linux 1 (Annapolis)"
                            NAME="ThinTrust GNU/Linux"
                            VERSION_ID="1"
                            VERSION="1 (Annapolis)"
                            VERSION_CODENAME=annapolis
                            ID=thintrust
                            HOME_URL="https://thintrust.com/"
                            SUPPORT_URL="https://thintrust.com/support"
                            BUG_REPORT_URL="https://bugs.thintrust.com/"''')
                return True
            except Exception as e:
                self.logger.error(f'Error changing os-release file: {e}')
                return False
            
        def change_lsb_release(self):
            try:
                with open('/etc/lsb-release', 'w') as f:
                    f.write('''DISTRIB_ID=ThinTrust
                            DISTRIB_RELEASE=1
                            DISTRIB_CODENAME=annapolis
                            DISTRIB_DESCRIPTION="ThinTrust GNU/Linux 1 (Annapolis)"''')
                return True
            except Exception as e:
                self.logger.error(f'Error changing lsb-release file: {e}')
                return False
            
        def change_motd(self):
            try:
                with open('/etc/motd', 'w') as f:
                    f.write('') # clear the motd file as we will use update-motd.d to generate it dynamically
                with open('/etc/update-motd.d/15-thintrust', 'w') as f:
                    f.write(f'''#!/bin/sh
                            figlet ThinTrust    # figlet is a program that creates ASCII art text
                            echo "Welcome to ThinTrust GNU/Linux 1 (Annapolis)"
                            echo "For support visit https://thintrust.com/support"
                            echo "Hostname: $(hostname), IP: $(hostname -I | awk '{{print $1}}')"''') # {{}} is used to escape the curly braces in f-strings
                return True
            except Exception as e:
                self.logger.error(f'Error changing motd file: {e}')
                return False

        def change_splash(self):
            try:
                if os.path.exists('/usr/share/plymouth/themes/thintrust'):
                    shutil.rmtree('/usr/share/plymouth/themes/thintrust')
                os.makedirs('/usr/share/plymouth/themes/thintrust')
                if not os.path.exists('plymouththeme.7z'):
                    with open('plymouththeme.7z', 'wb') as f:
                        self.logger.debug(f'Fetching theme from https://thintrust.com/release/{self.distro_release}/plymouththeme.7z')
                        f.write(requests.get(f'https://thintrust.com/release/{self.distro_release}/plymouththeme.7z').content)
                    self.logger.debug('Theme downloaded, decompressing...')
                subprocess.check_output('7z x plymouththeme.7z -o/usr/share/plymouth/themes', shell=True)
                self.logger.debug('Decompressed theme')
                subprocess.check_output('plymouth-set-default-theme -R thintrust', shell=True)
                return True
            except Exception as e:
                self.logger.error(f'Error changing splash screen: {e}')
                return False
            
        def update_grub(self):
            try:
                with open('/boot/grub/thintrust.png', 'wb') as f:
                    f.write(requests.get(f'https://thintrust.com/release/{self.distro_version}/grub.png').content)
                with open('/etc/default/grub', 'r') as f:
                    lines = f.readlines()
                with open('/etc/default/grub', 'w') as f:
                    for i, line in enumerate(lines):
                        if 'GRUB_CMDLINE_LINUX_DEFAULT' in line:
                            line = line.rstrip().rstrip('"')  # Strip newline and trailing quote
                            if 'overlayroot=tmpfs' not in line:
                                line += ' overlayroot=tmpfs'
                            if 'quiet' not in line:
                                line += ' quiet'
                            if 'splash' not in line:
                                line += ' splash'
                            if 'loglevel=3' not in line:
                                line += ' loglevel=3'
                            line += '"'  # Add a single closing quote at the end
                        lines[i] = line + '\n'
                        if 'GRUB_DISTRIBUTOR' in line:
                            lines[i] = 'GRUB_DISTRIBUTOR="ThinTrust"\n' # change GRUB_DISTRIBUTOR to ThinTrust
                        if 'GRUB_TIMEOUT' in line:
                            lines[i] = 'GRUB_TIMEOUT=2\n'
                        if 'GRUB_BACKGROUND' in line:
                            lines[i] = 'GRUB_BACKGROUND="/boot/grub/thintrust.png"\n'
                    if not any('GRUB_DISTRIBUTOR' in line for line in lines):
                            lines.append('GRUB_DISTRIBUTOR="ThinTrust"\n')
                    if not any('GRUB_CMDLINE_LINUX_DEFAULT' in line for line in lines):
                        lines.append('GRUB_CMDLINE_LINUX_DEFAULT="quiet splash loglevel=3 overlayroot=tmpfs"\n')
                    if not any('GRUB_TIMEOUT' in line for line in lines):
                        lines.append('GRUB_TIMEOUT=2\n')
                    if not any('GRUB_BACKGROUND' in line for line in lines):
                        lines.append('GRUB_BACKGROUND="/boot/grub/thintrust.png"\n')
                    f.writelines(lines)
                subprocess.check_output('update-grub', shell=True)
                return True
            except Exception as e:
                self.logger.error(f'Error updating GRUB: {e}')
                return False
            
        def set_default_background(self):
            if not os.path.exists('/usr/share/wallpapers'):
                os.makedirs('/usr/share/wallpapers')
            with open('/usr/share/wallpapers/wallpaper.png', 'wb') as f:
                f.write(requests.get(f'https://thintrust.com/release/{self.distro_version}/wallpaper.png').content)
            try:
                subprocess.check_output('.venv/bin/pip3 install PyGObject', shell=True)
                import gi
                gi.require_version('Gio', '2.0')
                from gi.repository import Gio
            except Exception as e:
                self.logger.error(f'Error importing PyGObject: {e}')
                return False
            gsettings_bg = Gio.Settings.new('org.cinnamon.desktop.background')
            gsettings_bg.set_string('picture-uri', 'file:///usr/share/wallpaper/wallpaper.png')
            gsettings_interface = Gio.Settings.new('org.cinnamon.desktop.interface')
            gsettings_interface.set_string('gtk-theme', 'Adwaita-dark')
            gsettings_interface.set_string('icon-theme', 'Papirus-Dark')
            gsettings_interface.set_string('cursor-theme', 'mate-black')
            gsettings_theme = Gio.Settings.new('org.cinnamon.theme')
            gsettings_theme.set_string('name', 'cinnamon')
            
        def set_lightdm_theme(self):
            try:
                with open('/usr/share/lightdm/lightdm-gtk-greater.conf', 'r') as f:
                    lines = f.readlines()
                with open('/usr/share/lightdm/lightdm-gtk-greater.conf', 'w') as f:
                    for i, line in enumerate(lines):
                        if 'background=' in line:
                            lines[i] = f'background=/usr/share/wallpaper/wallpaper.png\n'
                        if 'theme-name=' in line:
                            lines[i] = f'theme-name=Adwaita-dark\n'
                        if 'icon-theme-name=' in line:
                            lines[i] = f'icon-theme-name=Papirus-Dark\n'
                        if 'cursor-theme-name=' in line:
                            lines[i] = f'cursor-theme-name=mate-black\n'
                    if not any('background=' in line for line in lines):
                        lines.append('background=/usr/share/wallpaper/wallpaper.png\n')
                    if not any('theme-name=' in line for line in lines):
                        lines.append('theme-name=Adwaita-dark\n')
                    if not any('icon-theme-name=' in line for line in lines):
                        lines.append('icon-theme-name=Papirus-Dark\n')
                    if not any('cursor-theme-name=' in line for line in lines):
                        lines.append('cursor-theme-name=mate-black\n')
                    f.writelines(lines)
                return True
            except Exception as e:
                self.logger.error(f'Error setting lightdm theme: {e}')
                return False
            
        if not install_rebrand_packages(self):
            self.logger.error('Error installing rebrand packages.')
            return {'step': 'install_rebrand_packages', 'status': 'failed'}
        if not change_issue(self):
            self.logger.error('Error changing issue files.')
            return {'step': 'change_issue', 'status': 'failed'}
        if not change_os_release(self):
            self.logger.error('Error changing os-release file.')
            return {'step': 'change_os_release', 'status': 'failed'}
        if not change_lsb_release(self):
            self.logger.error('Error changing lsb-release file.')
            return {'step': 'change_lsb_release', 'status': 'failed'}
        if not change_motd(self):
            self.logger.error('Error changing motd file.')
            return {'step': 'change_motd', 'status': 'failed'}
        if not change_splash(self):
            self.logger.error('Error changing splash screen.')
            return {'step': 'change_splash', 'status': 'failed'}
        if not update_grub(self):
            self.logger.error('Error updating GRUB.')
            return {'step': 'update_grub', 'status': 'failed'}
        if not set_default_background(self):
            self.logger.error('Error setting default background.')
            return {'step': 'set_default_background', 'status': 'failed'}
        if not set_lightdm_theme(self):
            self.logger.error('Error setting lightdm theme.')
            return {'step': 'set_lightdm_theme', 'status': 'failed'}
        self.logger.info('Rebranding completed.')
        return {'step': 'rebrand_os', 'status': 'success'}

if __name__ == '__main__':
    InitialSetup()
