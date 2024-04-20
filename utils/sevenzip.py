import subprocess
import shlex

class SevenZip:
    def __init__(self):
        try:
            self.path = subprocess.check_output(['which', '7z']).decode('utf-8').strip()
        except Exception as e:
            print(f'Error getting 7zip path: {e}')
            subprocess.check_output('apt-get install -y p7zip-full', shell=True)
            self.path = subprocess.check_output(['which', '7z']).decode('utf-8').strip()
        self.version = self.get_version()
    
    def get_version(self):
        try:
            output = subprocess.check_output([self.path]).decode('utf-8')
            version_line = output.split('\n')[1]  # the version is on the second line
            version = version_line.split(' ')[2]  # the version number is the third word
            return version
        except Exception as e:
            print(f'Error getting 7zip version: {e}')
            return None
        
    def compress(self, source, destination):
        try:
            if subprocess.call([self.path, 'a', shlex.quote(destination), shlex.quote(source)]) != 0:
                print(f'Error compressing {source} to {destination}')
                return False
            return True
        except Exception as e:
            print(f'Error compressing {source} to {destination}: {e}')
            return False
    
    def decompress(self, source, destination):
        try:
            if subprocess.call([self.path, 'x', shlex.quote(source), '-o' + shlex.quote(destination)]) != 0:
                print(f'Error decompressing {source} to {destination}')
                return False
            return True
        except Exception as e:
            print(f'Error decompressing {source} to {destination}: {e}')
            return False
    