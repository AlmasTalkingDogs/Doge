class Dog:
    def __init__(self, name='chuchu'):
        self.name = name

    def __set_name__(self, name):
        self.name = name

    def __get_name__(self):
        return self.name

    def __del__(self):
        del (self)
