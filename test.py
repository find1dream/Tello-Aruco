m = 3
def test():
    global m
    m = 7
    print(m)


test()
if m == 7:
    print("m is 7")
print(m)
