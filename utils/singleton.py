class Singleton:
    """
    Create a singleton class.
    
    This class is used to create a singleton class, which is a class that can only have one instance. The singleton
    class is created by inheriting from this class and calling the __new__ method to create the instance. The instance
    is stored as a class attribute, so that it can be accessed by other classes and methods. This class is useful when
    you want to create a class that can only have one instance, such as a database connection or a configuration object.
    
    Example:
        class MySingleton(Singleton):
            def __init__(self, value):
                self.value = value
        instance1 = MySingleton(1)
        instance2 = MySingleton(2)
        print(instance1.value)  # Output: 2
        print(instance2.value)  # Output: 2
        
    Attributes:
        _instance (Any): The instance of the singleton class.
        
    Raises:
        TypeError: If the singleton class is instantiated more than once.
        
    Returns:
        Any: The instance of the singleton class.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = super(Singleton, cls).__new__(cls)
        return cls._instance