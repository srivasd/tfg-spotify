# Lists

list = ['Manuel', 23, 'Hello world', 3.14]
print(list[0])

list[0] = 'My value is different'
print(list[0])

tuples = ('Manuel', 'Rosa', 'Pepito', 45, 3.14)
# tuples[0] = 'My value is different'

print('All elements of list:', list)
print('All elements of tuples:', tuples)

print(list[1:4])
print(tuples[1:4])
print(tuples[1:])

new_array = tuples * 2
print(new_array)

list_1 = ['one', 'two', 'three']
list_2 = ['four', 'five', 'six']

concat_list = list_1 + list_2
print(concat_list)
