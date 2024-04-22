#!/usr/bin/python3
import os
import json
from utils.logger import Logger
import subprocess
from utils.system_profiler import SystemProfiler
from argparse import ArgumentParser

class ThinTrust(Logger):
    """
    The ThinTrust class represents the main functionality of the ThinTrust application.

    It initializes the ThinTrust application, checks for root privileges, loads the configuration file,
    installs initial packages, and sets up the system profiler.

    Attributes:
        config (dict): The configuration loaded from the config.json file.
        system_profiler (SystemProfiler): An instance of the SystemProfiler class.

    Methods:
        __init__(): Initializes the ThinTrust application.
        install_initial_packages(): Installs the initial packages required by ThinTrust.

    """

    def __init__(self):
        """
        Initializes the ThinTrust application.

        Raises:
            SystemExit: If ThinTrust is not run as root or if the config file is not found.

        """
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
        self.logger.info(f'ThinTrust Version: {self.distro_version} Release: {self.distro_release.capitalize()}\n')
        # if not self.install_initial_packages():
        #     self.logger.error(f'Error installing initial packages:{self.initial_packages}\n Try installing them manually and running ThinTrust again.')
        #     exit(1)
        self.system_profiler = SystemProfiler(self.logger).system_profile
        from setup.setup_v2 import InitialSetup
        self.initial_setup = InitialSetup
        
    def install_initial_packages(self):
        """
        Installs the initial packages required by ThinTrust.

        Returns:
            bool: True if the installation is successful, False otherwise.

        """
        self.logger.info('Installing initial packages...')
        try:
            subprocess.check_output(f'apt-get update -y', shell=True)
            subprocess.check_output(f'apt-get install -y {" ".join(self.initial_packages)}', shell=True)
            return True
        except Exception as e:
            self.logger.error(f'Error installing initial packages: {e}')
            return False
        
if __name__ == '__main__':
    parser = ArgumentParser()
    thintrust = ThinTrust()
    parser.add_argument('-v', '--version', action='store_true', help='Display the version of ThinTrust.')
    parser.add_argument('-s', '--setup', action='store_true', help='Run the initial setup for ThinTrust.')
    args = parser.parse_args()
    if args.version:
        print(f'ThinTrust Release: {thintrust.distro_release} Version: {thintrust.distro_version}')
    elif args.setup:
        thintrust.install_initial_packages()
        thintrust.initial_setup(thintrust)

        