class Environment():
    def __init__(self, name, parent = None):
        self.parent = parent
        self.name = name
        self.values = {}

    @staticmethod
    def globalEnv():
        return Environment("global")

    def lookup(self, identifier):
        if identifier in self.values:
            return self.values[identifier]
        elif self.parent != None:
            return self.parent.find(identifier)
        else:
            return None
    
    def set(self, identifier, value):
        self.values[identifier] = value
    
    def derive(self, name):
        return Environment(name, self)