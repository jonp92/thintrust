import subprocess
import shlex

class SevenZip:
    """
    A class for interacting with the 7-Zip compression utility.
    """

    def __init__(self):
        try:
            self.path = subprocess.check_output(['which', '7z']).decode('utf-8').strip()
        except Exception as e:
            print(f'Error getting 7zip path: {e}')
            subprocess.check_output('apt-get install -y p7zip-full', shell=True)
            self.path = subprocess.check_output(['which', '7z']).decode('utf-8').strip()
        self.version = self.get_version()
    
    def get_version(self):
        """
        Get the version of the 7-Zip utility.

        Returns:
            str: The version number of the 7-Zip utility, or None if an error occurred.
        """
        try:
            output = subprocess.check_output([self.path]).decode('utf-8')
            version_line = output.split('\n')[1]  # the version is on the second line
            version = version_line.split(' ')[2]  # the version number is the third word
            return version
        except Exception as e:
            print(f'Error getting 7zip version: {e}')
            return None
        
    def compress(self, source, destination):
        """
        Compress a file or directory using the 7-Zip utility.

        Args:
            source (str): The path to the file or directory to compress.
            destination (str): The path to the destination archive file.

        Returns:
            bool: True if the compression was successful, False otherwise.
        """
        try:
            if subprocess.call([self.path, 'a', shlex.quote(destination), shlex.quote(source)]) != 0:
                print(f'Error compressing {source} to {destination}')
                return False
            return True
        except Exception as e:
            print(f'Error compressing {source} to {destination}: {e}')
            return False
    
    def decompress(self, source, destination):
        """
        Decompress an archive file using the 7-Zip utility.

        Args:
            source (str): The path to the archive file to decompress.
            destination (str): The path to the destination directory.

        Returns:
            bool: True if the decompression was successful, False otherwise.
        """
        try:
            if subprocess.call([self.path, 'x', shlex.quote(source), '-o' + shlex.quote(destination)]) != 0:
                print(f'Error decompressing {source} to {destination}')
                return False
            return True
        except Exception as e:
            print(f'Error decompressing {source} to {destination}: {e}')
            return False
    