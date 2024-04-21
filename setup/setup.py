import os
import json
import shutil
import subprocess

from thintrust import ThinTrust
from utils.sevenzip import SevenZip

class InitialSetup(ThinTrust):
    """
    Class representing the initial setup of the ThinTrust system.

    Attributes:
        setup_config (dict): Configuration data for the setup.
        sevenzip (SevenZip): Instance of the SevenZip class for handling 7zip operations.

    Methods:
        __init__(): Initializes the InitialSetup object.
        sanity_check(): Performs a sanity check on the system.
        setup_overlayroot(): Sets up overlayroot on the system.
        rebrand_os(): Rebrands the operating system.
    """

    def __init__(self):
        """
        Initializes the InitialSetup object.

        This method sets up the necessary attributes and performs the initial setup steps.

        Args:
            None

        Returns:
            None
        """
        script_dir = os.path.dirname(os.path.abspath(__file__))
        setup_file = f'{script_dir}/setup.json'
        super().__init__()
        self.logger.name = 'InitialSetup'
        self.logger.info('Starting initial setup...')
        self.sevenzip = SevenZip()
        if os.path.exists(setup_file):
            with open(setup_file, 'r') as f:
                self.setup_config = json.load(f)
        else:
            self.logger.error('Setup file not found.')
            exit(1)
        sanity = self.sanity_check()
        if sanity is not True:
            self.logger.error(f"Sanity check failed: {sanity['error']}")
            exit(1)
        self.setup_overlayroot()
        self.rebrand_os()
    
    def sanity_check(self):
        """
        Performs a sanity check on the system.

        This method checks if the CPU architecture and disk space meet the requirements.

        Args:
            None

        Returns:
            bool or dict: True if the sanity check passes, otherwise a dictionary with an error message.
        """
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
        """
        Sets up overlayroot on the system.

        This method installs overlayroot if it is not already installed.

        Args:
            None

        Returns:
            None
        """
        self.logger.info('Setting up overlayroot...')
        try:
            result = subprocess.check_output('apt-get install -y overlayroot', shell=True)
            if 'overlayroot is already the newest version' in result.decode('utf-8'):
                self.logger.info('Overlayroot already installed, skipping...')
                return
            subprocess.check_output('overlayroot-chroot', shell=True)
            self.logger.info('Overlayroot installation completed.')
        except Exception as e:
            self.logger.error(f'Error setting up overlayroot: {e}')
            
    def rebrand_os(self):
        """
        Rebrands the operating system.

        This method performs various rebranding tasks such as changing issue files, OS release file,
        motd file, splash screen, and updating grub.

        Args:
            None

        Returns:
            None
        """
        self.logger.info('Rebranding OS...')
        def install_rebrand_packages(self):
            """
            Installs the rebrand packages.

            This method installs the rebrand packages specified in the setup configuration.

            Args:
                None

            Returns:
                bool: True if the packages are installed successfully, False otherwise.
            """
            try:
                packages = self.setup_config['rebrand_os_packages']
                self.logger.debug(f'Installing rebrand packages: {packages}')
                subprocess.check_output(f'apt-get install -y {" ".join(packages)}', shell=True)
                return True
            except Exception as e:
                self.logger.error(f'Error installing rebrand packages: {e}')
                return False
        def change_issue(self):
            """
            Changes the issue files.

            This method updates the /etc/issue and /etc/issue.net files with the ThinTrust branding.

            Args:
                None

            Returns:
                bool: True if the files are updated successfully, False otherwise.
            """
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
            """
            Changes the os-release file.

            This method updates the /etc/os-release file with the ThinTrust branding.

            Args:
                None

            Returns:
                bool: True if the file is updated successfully, False otherwise.
            """
            try:
                with open('/etc/os-release', 'w') as f:
                    f.write('PRETTY_NAME="ThinTrust GNU/Linux 1 (Annapolis)"\n'
                            'NAME="ThinTrust GNU/Linux"\n'
                            'VERSION_ID="1"\n'
                            'VERSION="1 (Annapolis)"\n'
                            'VERSION_CODENAME=annapolis\n'
                            'ID=thintrust\n'
                            'HOME_URL="https://thintrust.com/"\n'
                            'SUPPORT_URL="https://thintrust.com/support"\n'
                            'BUG_REPORT_URL="https://bugs.thintrust.com/"')
                return True
            except Exception as e:
                self.logger.error(f'Error changing os-release file: {e}')
                return False
            
        def change_lsb_release(self):
            """
            Changes the lsb-release file.

            This method updates the /etc/lsb-release file with the ThinTrust branding.

            Args:
                None

            Returns:
                bool: True if the file is updated successfully, False otherwise.
            """
            try:
                with open('/etc/lsb-release', 'w') as f:
                    f.write('DISTRIB_ID=ThinTrust\n'
                            'DISTRIB_RELEASE=1\n'
                            'DISTRIB_CODENAME=annapolis\n'
                            'DISTRIB_DESCRIPTION="ThinTrust GNU/Linux 1 (Annapolis)"')
                return True
            except Exception as e:
                self.logger.error(f'Error changing lsb-release file: {e}')
                return False
            
        def change_motd(self):
            """
            Changes the motd file.

            This method updates the /etc/motd file and generates a dynamic motd using update-motd.d.

            Args:
                None

            Returns:
                bool: True if the file is updated successfully, False otherwise.
            """
            try:
                with open('/etc/motd', 'w') as f:
                    f.write('') # clear the motd file as we will use update-motd.d to generate it dynamically
                with open('/etc/update-motd.d/15-thintrust', 'w') as f:
                    f.write('#!/bin/sh\n'
                            'figlet ThinTrust\n'    # figlet is a program that creates ASCII art text
                            'echo "Welcome to ThinTrust GNU/Linux 1 (Annapolis)"\n'
                            'echo "For support visit https://thintrust.com/support"\n'
                            'echo "Hostname: $(hostname), IP: $(hostname -I | awk \'{print $1}\')"') # {{}} is used to escape the curly braces in f-strings
                os.chmod('/etc/update-motd.d/15-thintrust', 0o755)
                subprocess.check_output('run-parts /etc/update-motd.d/ > /var/run/motd.dynamic', shell=True)
                return True
            except Exception as e:
                self.logger.error(f'Error changing motd file: {e}')
                return False

        def change_splash(self):
            """
            Changes the splash screen.

            This method downloads and sets the ThinTrust theme as the default splash screen.

            Args:
                None

            Returns:
                bool: True if the splash screen is changed successfully, False otherwise.
            """
            import requests
            try:
                if os.path.exists('/usr/share/plymouth/themes/thintrust'):
                    shutil.rmtree('/usr/share/plymouth/themes/thintrust')
                os.makedirs('/usr/share/plymouth/themes/thintrust')
                if not os.path.exists('plymouththeme.7z'):
                    with open('plymouththeme.7z', 'wb') as f:
                        self.logger.debug(f'Fetching theme from https://thintrust.com/release/{self.distro_release}/resources/plymouththeme.7z')
                        f.write(requests.get(f'https://thintrust.com/release/{self.distro_release}/resources/plymouththeme.7z').content)
                    self.logger.debug('Theme downloaded, decompressing...')
                self.sevenzip.decompress('plymouththeme.7z', '/usr/share/plymouth/themes/')
                self.logger.info('Decompressed theme, please wait as it is set as the default theme)')
                self.logger.debug('Decompressed theme, setting as default theme (Note: This may take a few seconds as it regenerates the initramfs)')
                subprocess.check_output('plymouth-set-default-theme -R thintrust', shell=True)
                return True
            except Exception as e:
                self.logger.error(f'Error changing splash screen: {e}')
                return False
            
        def update_grub(self):
            """
            Updates the grub configuration.

            This method updates the grub configuration to include a custom menu entry for ThinTrust.

            Args:
                None

            Returns:
                bool: True if the grub configuration is updated successfully, False otherwise.
            """
            import requests
            blkid = subprocess.check_output('blkid -s UUID -o value /dev/sda2', shell=True).decode('utf-8').strip()
            try:
                with open('/boot/grub/thintrust.png', 'wb') as f:
                    f.write(requests.get(f'https://thintrust.com/release/{self.distro_release}/resources/wallpapers/wallpapernologo.png').content)
                with open('/etc/grub.d/40_custom', 'w') as f:
                    f.write("#!/bin/sh\n"
                        "exec tail -n +3 $0\n"
                        "# This file provides an easy way to add custom menu entries.  Simply type the\n"
                        "# menu entries you want to add after this comment.  Be careful not to change\n"
                        "# the 'exec tail' line above.\n"
                        f"menuentry 'ThinTrust GNU/Linux Read-Write Mode' --class debian --class gnu-linux --class gnu --class os $menuentry_id_option 'gnulinux-simple-{blkid}' {{\n"
                        "    load_video\n"
                        "    insmod gzio\n"
                        "    if [ x$grub_platform = xxen ]; then insmod xzio; insmod lzopio; fi\n"
                        "    insmod part_gpt\n"
                        "    insmod ext2\n"
                        f"    search --no-floppy --fs-uuid --set=root {blkid}\n"
                        f"    echo    'Loading Linux {os.uname().release} ...'\n"
                        f"    linux   /boot/vmlinuz-{os.uname().release} root=UUID={blkid} rw quiet splash loglevel=3\n"
                        f"    echo    'Loading initial ramdisk ...'\n"
                        f"    initrd  /boot/initrd.img-{os.uname().release}\n"
                        "}\n")
                os.chmod('/etc/grub.d/40_custom', 0o755)
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
                        if 'GRUB_DISTRIBUTOR' in line:
                            line = 'GRUB_DISTRIBUTOR="ThinTrust"'
                        if 'GRUB_TIMEOUT' in line:
                            line = 'GRUB_TIMEOUT=2'
                        if 'GRUB_BACKGROUND' in line:
                            line = 'GRUB_BACKGROUND="/boot/grub/thintrust.png"'
                        lines[i] = line if line.endswith('\n') else line + '\n'
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
        
        def ensure_user(self):
            try:
                if subprocess.check_output('id user', shell=True):
                    return True
                else:
                    subprocess.check_output('useradd -m -s /bin/bash user', shell=True)
                    subprocess.check_output('echo "user:user" | chpasswd', shell=True)
                    return True
            except Exception as e:
                self.logger.error(f'Error creating user: {e}')
                return False
            
        def set_default_background(self):
            import requests
            if not os.path.exists('/usr/share/wallpapers'):
                os.makedirs('/usr/share/wallpapers')
            with open('/usr/share/wallpapers/wallpaper.svg', 'wb') as f:
                f.write(requests.get(f'https://thintrust.com/release/{self.distro_release}/resources/wallpapers/wallpaper.svg').content)
            try:
                os.chmod('/usr/share/wallpapers/wallpaper.svg', 0o644)
                subprocess.check_output('cp setup/default_theme.sh /usr/local/etc/', shell=True)
                os.chmod('/usr/local/etc/default_theme.sh', 0o755)
                if not os.path.exists('/home/user/.config/autostart'):
                    os.makedirs('/home/user/.config/autostart')
                with open('/home/user/.config/autostart/set_theme.desktop', 'w') as f:
                    f.write('[Desktop Entry]\n'
                            'Type=Application\n'
                            'Name=Set Theme\n'
                            'Comment=Set the default theme\n'
                            'Comment[en_US]=Set the default theme\n'
                            'Exec=/usr/local/etc/default_theme.sh\n'
                            'X-GNOME-Autostart-enabled=true\n'
                            'StartupNotify=false\n'
                            'Terminal=false\n'
                            'Hidden=false\n')
                return True
            except Exception as e:
                self.logger.error(f'Error setting default background: {e}')
                return False
            
        def set_lightdm_theme(self):
            import requests
            try:
                with open('/usr/share/wallpapers/wallpaper.png', 'wb') as f:
                    f.write(requests.get(f'https://thintrust.com/release/{self.distro_release}/resources/wallpapers/wallpaper.png').content)
                os.chmod('/usr/share/wallpapers/wallpaper.png', 0o644)
                if not os.path.exists('/etc/lightdm/lightdm-gtk-greeter.conf.d'):
                    os.makedirs('/etc/lightdm/lightdm-gtk-greeter.conf.d')
                elif os.path.exists('/etc/lightdm/lightdm-gtk-greeter.conf.d/01_debian.conf'):
                    os.remove('/etc/lightdm/lightdm-gtk-greeter.conf.d/01_debian.conf')
                with open('/etc/lightdm/lightdm-gtk-greeter.conf.d/01_thintrust.conf', 'w') as f:
                    f.write('[greeter]\n'
                            'background=/usr/share/wallpapers/wallpaper.png\n'
                            'theme-name=Adwaita-dark\n'
                            'icon-theme-name=Papirus-Dark\n'
                            'xft-antialias=true\n'
                            'xft-hintstyle=hintfull\n'
                            'xft-rgba=rgb\n'
                            'reader=orca')
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
        if not ensure_user(self):
            self.logger.error('Error creating user.')
            return {'step': 'ensure_user', 'status': 'failed'}
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
