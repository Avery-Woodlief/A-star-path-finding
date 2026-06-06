from functools import wraps

class Int32Base(int):
    max_value = (2 ** 31) - 1
    min_value = -(2 ** 31)

    

    def __new__(cls, value):
        if (isinstance(value, (list, tuple))):
            body = []
            for v in value:
                body.append(super().__new__(cls, v))
            return tuple(body)
        cls.check_overflow(value)
        return super().__new__(cls, value)

    @classmethod
    def type_check(cls, value):
        if (isinstance(value, (list, tuple))):
            print(type(cls))
            for v in value:
                return cls.type_check(v)
        if (isinstance(value, str)):
            return int(value)
        if (not isinstance(value, (int, Int32Base))):
            #print(type(value))
            raise TypeError("argument must be int or Int32")
        return value

    @classmethod
    def check_overflow(cls, value):
        value = cls.type_check(value)

        if value > cls.max_value or value < cls.min_value:
            #print("overflowed")
            raise OverflowError("value outside Int32 range")
        return value

    @classmethod
    def div_param_check(cls, div):
        @wraps(div)
        def wrapper(self, other):
            cls.check_overflow(self)
            other = cls.check_overflow(other)
            if (other == 0):
                raise ZeroDivisionError

            result = div(self, other)

            return Int32(result)
        return wrapper


    @classmethod
    def basic_overflow_and_type_check(cls, func):
        @wraps(func)
        def wrapper(self, other):
            cls.check_overflow(self) # type check done with overflow check
            other = cls.check_overflow(other)
            

            result = func(self, other)
            cls.check_overflow(result)
            return Int32(result)
        return wrapper

    @classmethod
    def pow_check(cls, func):
        @wraps(func)
        def wrapper(self, other):
            cls.check_overflow(self) # type check done with overflow check
            other = cls.check_overflow(other)
            x = int(self)
            y = int(other)
            if (y < 0):
                y = abs(y)
                cls.div_param_check(func)
                return func(self, other)

            i = 1
            while (i <= y):
                if (x ** i > cls.max_value):
                    raise OverflowError
                i += 1
            return Int32(func(self, other))
        return wrapper


class Int32: pass
    

class Int32(Int32Base):

    @Int32Base.basic_overflow_and_type_check
    def __add__(self, other: int | Int32) -> Int32:
        return super().__add__(other)

    @Int32Base.basic_overflow_and_type_check
    def __sub__(self, other: int | Int32) -> Int32:
        return super().__sub__(other)

    def __eq__(self, other: int | Int32) -> Int32:
        return super().__eq__(other)

    @Int32Base.div_param_check
    def __div__(self, other : int | Int32) -> Int32:
        return super().__floordiv__(other)

    @Int32Base.basic_overflow_and_type_check
    def __ge__(self, other : int | Int32) -> bool:
        return super().__ge__(other)

    @Int32Base.basic_overflow_and_type_check
    def __le__(self, other : int | Int32) -> bool:
        return super().__le__(other)

    @Int32Base.pow_check
    def __pow__(self, other : int | Int32) -> Int32:
        return super().__pow__(other)

    def __str__(self):
        return super().__str__(self)

    def __hash__(self):
        return super().__hash__()



