import numpy as np

a = [10, 11, -4, -6, 0, 18]

def remove_negative(list):
    temp = []
    for i in list:
        if i < 0:
            temp.append(0)
        else:
            temp.append(i)

    return temp

print(list(map(lambda x:max(x,0), a)))
