class SingletonMeta(type):
    """
    The Singleton class can be implemented in different ways in Python. Some
    possible methods include: base class, decorator, metaclass. We will use the
    metaclass because it is best suited for this purpose.
    """

    _instance = None

    def __call__(self): 
        if self._instance is None:
            self._instance = super().__call__()
        return self._instance
