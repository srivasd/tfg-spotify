def square(number):
    """Return the square of number."""
    sqr_num = number ** 2
    return sqr_num


input_num = 5
output_num = square(input_num)

print('Square result: ', output_num)


def return_difference(num1, num2):
    """Return the difference between two numbers.
        Subtracts n2 from n1."""
    return num1 - num2

print('Return difference result: ', return_difference(3, 5))
