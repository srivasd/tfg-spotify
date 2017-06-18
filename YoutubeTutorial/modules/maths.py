
def add(*arg):
    total = arg[0]
    for value in arg[1:]:
        total += value
    return total


def sub(*arg):
    total = arg[0]
    for value in arg[1:]:
        total -= value
    return total


def multi(*arg):
    total = arg[0]
    for value in arg[1:]:
        total *= value
    return total


def div(n1, n2):
    return n1 / n2


