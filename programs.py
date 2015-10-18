class SingletonProgram(object):
    INSTANCE = None

    @classmethod
    def get(cls):
        if cls.INSTANCE is None:
            cls.INSTANCE = cls()
        return cls.INSTANCE
