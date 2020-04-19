from enum import Enum


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


class AccessList:
    """
        Users and groups access manager
    """
    # Current user is enabled by default and can't be disabled

    OTHERS = '$others'    
    ME = '$me'
    
    def __init__(self, is_allow_others=False):
        self.whitelist = set()
        self.blacklist = set()
        self.is_allow_others = is_allow_others

    def __access_modifier(self, entity: str, lst: set, desirable: bool):
        if entity == self.ME:
            return

        if entity != self.OTHERS and self.is_allow_others is desirable:
            lst.add(entity)
        else:
            self.whitelist = self.blacklist = set()
            self.is_allow_others = not desirable
        
    def allow(self, entity: str):
        self.__access_modifier(entity, self.whitelist, desirable=False)
               
    def ban(self, entity: str):
        self.__access_modifier(entity, self.blacklist, desirable=True)

    def is_allowed(self, entity: str):
        return self.is_allow_others or entity in self.whitelist or entity == self.ME


