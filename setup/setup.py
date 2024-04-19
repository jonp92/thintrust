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
            
if __name__ == '__main__':
    InitialSetup()