
# Operators of comparation
# equal ==
# different !=
# greater than >
# greater or equal than >=
# less than <
# less or equal tha <=

variable = 1

if variable > 3:
    # If the condition is true
    print(variable, 'is greater than 3')
elif variable == 1:
    print(variable, 'is equal to 1')
else:
    # If the condition is false
    print(variable, 'is less than 3')

# Logic operators

# and : both conditions are true
# or : one of the conditions must be true
# not : the condition is not true

variable1 = 2
variable2 = 2
variable3 = 3
variable4 = 4

if not(variable1 != variable2 or variable3 < variable4):
    print('The conditions are true')
else:
    print('The conditions are false')

# Operator membership allows to check values in strings, list and tuples
# in : the value is found
# not in : the value is not found

list = ['one', 'two', 'three']
if 'two' in list:
    print('Two is in the list')
else:
    print('Two is not in the list')



