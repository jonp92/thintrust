#!/usr/bin/python3
import os
import json
from utils.logger import Logger
import subprocess

from argparse import ArgumentParser

class ThinTrust(Logger):
    """
    The ThinTrust class represents the main functionality of the ThinTrust application.

    It is responsible for initializing the application, installing the initial packages, running the ThinTrust agent and server,
    and running the initial setup for ThinTrust. In essence, it manages all functionality of the ThinTrust application suite.

    Attributes:
        config (dict): The configuration loaded from the config.json file.
        system_profiler (SystemProfiler): An instance of the SystemProfiler class.
        pretty_version (str): A human-readable version of the OS version.

    Methods:
        __init__(): Initializes the ThinTrust application.
        install_initial_packages(): Installs the initial packages required by ThinTrust.
        is_package_installed(package_name): Checks if a package is installed.
        run_agent(): Runs the ThinTrust agent.
        run_server(): Runs the ThinTrust server.
        run_initial_setup(): Runs the initial setup for ThinTrust.

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
        self.pretty_version = f'v{self.distro_version} {self.distro_release.capitalize()}'
        super().__init__('ThinTrust', self.log_file, self.log_level)
        # if not self.install_initial_packages():
        #     self.logger.error(f'Error installing initial packages:{self.initial_packages}\n Try installing them manually and running ThinTrust again.')
        #     exit(1)
        
        
    def is_package_installed(self,package_name):
        try:
            output = subprocess.check_output(f"dpkg-query -s {package_name}", shell=True, stderr=subprocess.STDOUT)
            return True
        except subprocess.CalledProcessError:
            return False

        
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
        
    def run_agent(self):
        from agent.agent import ThinAgent
        agent = ThinAgent()
        agent.loop.run_until_complete(agent.connect())
        
    def run_server(self):
        from tec.tec_server import TECServer
        server = TECServer()
        server.run()
        
    def run_initial_setup(self):
        self.install_initial_packages()
        from setup.setup_v2 import InitialSetup
        self.initial_setup = InitialSetup(self)
        self.initial_setup.run()
        
if __name__ == '__main__':
    parser = ArgumentParser()
    thintrust = ThinTrust()
    parser.add_argument('-v', '--version', action='store_true', help='Display the version of ThinTrust.')
    parser.add_argument('-i', '--install', action='store_true', help='Run the initial install for ThinTrust.')
    parser.add_argument('-p', '--sysprofile', action='store_true', help='Display the system profile.')
    parser.add_argument('-a', '--agent', action='store_true', help='Run the ThinTrust agent. (If not running as a service)')
    parser.add_argument('-s', '--server', action='store_true', help='Run the ThinTrust server.')
    parser.description = 'ThinTrust setup and management tool.'
    parser.epilog = 'ThinTrust is a tool for setting up and managing ThinTrust OS endpoints.\n'
    args = parser.parse_args()
    if args.version:
        print(f'ThinTrust {thintrust.pretty_version}')
    elif args.install:
        thintrust.run_initial_setup()
    elif args.sysprofile:
        from utils.system_profiler import SystemProfiler
        try:
            import psutil
        except ImportError:
            if not thintrust.is_package_installed('python3-psutil'):
                try:
                    if subprocess.call('apt-get install -y python3-psutil', shell=True) != 0:
                        thintrust.logger.error('Error installing python3-psutil. Try installing it manually and running ThinTrust again.')
                        exit(1)
                except Exception as e:
                    thintrust.logger.error(f'Error installing python3-psutil: {e}')
                    exit(1)
        sp = SystemProfiler(logger=thintrust.logger)
        print(json.dumps(sp.system_profile, indent=4))
    elif args.agent:
        thintrust.run_agent()
    elif args.server:
        thintrust.run_server()
    else:
        parser.print_help()

        