from int32 import Int32, Int32Base

Int32_operations = dict(Int32.__dict__)
Int32_operations.pop("__module__")
Int32_operations.pop("__doc__")
Int32_operations.pop("__hash__")

int_operations = dict(int.__dict__)


valid_ops_names = Int32_operations.keys()
#print(valid_ops_names)


from random import randint

trials = 100000

for i in range(trials):
    try:
        x = randint(Int32Base.min_value//(2**30), Int32Base.max_value//(2**27))
        y = randint(Int32Base.min_value//(2**30), Int32Base.max_value//(2**27))
        #print(x, y)
        a = Int32(x)
        b = Int32(y)

        for name in valid_ops_names:
            if (name == "__div__"):
                assert(Int32_operations[name](a, b) == int_operations["__floordiv__"](x, y))
            else:
                assert(Int32_operations[name](a, b) == int_operations[name](x, y))
            
    except (OverflowError, TypeError, ZeroDivisionError) as e:
        print(f"{type(e)} {name}")
        #continue
        

