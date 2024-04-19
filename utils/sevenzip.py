import subprocess
import shlex

class SevenZip:
    def __init__(self):
        self.path = subprocess.check_output(['which', '7z']).decode('utf-8').strip() 
        self.version = self.get_version()
    
    def get_version(self):
        try:
            version = subprocess.check_output([self.path, '--version']).decode('utf-8').split('\n')[0].split(' ')[1]
            return version
        except Exception as e:
            print(f'Error getting 7zip version: {e}')
            return None
        
    def compress(self, source, destination):
        try:
            subprocess.check_output([self.path, 'a', shlex.quote(destination), shlex.quote(source)])
            return True
        except Exception as e:
            print(f'Error compressing {source} to {destination}: {e}')
            return False
    
    def decompress(self, source, destination):
        try:
            subprocess.check_output([self.path, 'x', shlex.quote(source), '-o' + shlex.quote(destination)])
            return True
        except Exception as e:
            print(f'Error decompressing {source} to {destination}: {e}')
            return False
    