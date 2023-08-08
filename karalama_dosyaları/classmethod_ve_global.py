"""
experiment with
"""


class MathOperations:
    a = 0
    b = 0

    def __init__(self, a, b):
        self.a = a
        self.b = b

    @classmethod
    def sum(cls, a_z, b_z):
        global a, b
        if a and b:
            return a + b
        if cls is MathOperations:
            return cls.a + cls.b
        else:
            return a_z + b_z

    @classmethod
    def multiply(cls, a, b):
        if cls is MathOperations:
            return cls.a * cls.b
        else:
            return a * b

    @classmethod
    def divide(cls, a, b):
        if cls is MathOperations:
            return cls.a / cls.b
        else:
            return a / b

    @classmethod
    def subtract(cls, a, b):
        if cls is MathOperations:
            return cls.a - cls.b
        else:
            return a - b

    @classmethod
    def power(cls, a, b):
        if cls is MathOperations:
            return cls.a**cls.b
        else:
            return a**b


a = 10
b = 5


class ex:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __repr__(self) -> str:
        return f"ex({self.a!r},{self.b!r})"

    @classmethod
    def ex_(cls, c):
        if cls is ex:
            print(cls.a, cls.b)
            print(cls)
            return cls.a + cls.b + c
        else:
            return a + b + c


if __name__ == "__main__":
    print(MathOperations.sum(a, b))
    print(ex.ex_(b))
