import hashlib

class HashTools:
    """
    A class to hash files and compare hashes.
    
    This class provides method to hash files, save a hash to a file, load a hash from a file, compare two hashes, and compare two files.
    By default, the class uses the sha256 algorithm to hash files, but other algorithms can be used by specifying the algorithm when creating an instance of the class.
    The algorithms available are those provided by the hashlib module and guranteed to be available on all platforms. You can use this module in any Python application
    to hash files and compare hashes.

    Attributes:
        hash (hashlib): A hashlib object used to hash files. A new hash object is created for each method to avoid issues with reusing the same hash object.
        available_algorithms (list): A list of strings representing the available hashing algorithms. This is based on the algorithms provided 
        by the hashlib module and guranteed to be available on all platforms.
    
    Args:
        algorithm (str): A string representing the hashing algorithm to use. The default value is 'sha256'.
        
    Methods:
        hash_file(filename: str) -> str: Hashes a file and returns the hash value.
        save_hash(hash_value: str, filename: str): Saves a hash value to a file.
        load_hash(filename: str) -> str: Loads a hash value from a file.
        compare_hashes(hash1: str, hash2: str) -> bool: Compares two hash values and returns True if they are the same.
        compare_files(file1: str, file2: str) -> bool: Compares two files and returns True if they have the same hash value.
    """
    def __init__(self, algorithm: str = 'sha256') -> None:
        self.algorithm = algorithm
        self.available_algorithms = hashlib.algorithms_guaranteed
        if algorithm not in self.available_algorithms:
            raise ValueError(f'Invalid algorithm. Available algorithms are: {self.available_algorithms}')
    
    def hash_file(self, filename: str) -> str:
        """
        Hash a file using the sha256 algorithm.
        
        Used to hash a file using the sha256 algorithm. The file is read in chunks of 4096 bytes to avoid memory issues with large files and to improve performance.
        The hash object is updated with each chunk of data read from the file. The final hash value is returned as a string in hexadecimal format.
        
        Args:
            filename (str): A string representing the path to the file to hash.
            
        Returns:
            str: The hexadecimal hash of the file.
        """
        # Create a hash object using the specified algorithm. A new hash object is created for each file to avoid issues with reusing the same hash object.
        self.hash = getattr(hashlib, self.algorithm)()
        # Open the file in binary mode
        with open(filename, 'rb') as file:
            while True:
                # Read data from file in chunks of 4096 bytes
                chunk = file.read(4096) 
                if not chunk: 
                    break # If there is no more data, break the loop
                self.hash.update(chunk) # Update the hash with the chunk of data

        # Return the hexadecimal hash
        return self.hash.hexdigest() # Return the hexadecimal hash
    
    def save_hash(self, filename: str, hash: str) -> str:
        """
        Save a hash to a file.
        
        Used to save a hash to a file. The hash is saved as a string in hexadecimal format.
        
        Args:
            filename (str): A string representing the path to the file to save the hash to.
            hash (str): A string representing the hash to save.
            
        Returns:
            str: the path to the file where the hash was saved.
        """
        self.hash = getattr(hashlib, self.algorithm)() # Create a hash object using the specified algorithm
        with open(filename + '.sha256', 'w') as file:
            file.write(hash) # Write the hash to the file
        return filename + '.sha256' # Return the path to the file where the hash was saved
    
    def load_hash(self, filename: str) -> str:
        """
        Load a hash from a file.
        
        Used to load a hash from a file. The hash is expected to be saved as a string in hexadecimal format.
        
        Args:
            filename (str): A string representing the path to the file to load the hash from.
            
        Returns:
            str: The hash loaded from the file.
        """
        self.hash = getattr(hashlib, self.algorithm)() # Create a hash object using the specified algorithm
        with open(filename, 'r') as file:
            return file.read().strip() # Remove any leading or trailing whitespace

    def compare_hashes(self, hash1: str, hash2: str) -> bool:
        """
        Compare two hashes.
        
        Used to compare two hashes and determine if they are equal.
        
        Args:
            hash1 (str): A string representing the first hash.
            hash2 (str): A string representing the second hash.
            
        Returns:
            bool: A boolean value indicating whether the hashes are equal.
        """
        return hash1 == hash2 # Compare the hashes and return the result
    
    def compare_files(self, file1: str, file2: str) -> bool:
        """
        Compare two files using hashes.
        
        Used to compare two files by hashing them and comparing the resulting hashes.
        
        Args:
            file1 (str): A string representing the path to the first file.
            file2 (str): A string representing the path to the second file.
            
        Returns:
            bool: A boolean value indicating whether the files are equal based on their hashes.
        """
        self.hash = getattr(hashlib, self.algorithm)() # Create a hash object using the specified algorithm
        return self.hash_file(file1) == self.hash_file(file2) # Hash the files and compare the hashes