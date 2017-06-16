init = 0
final = 10

while init < final:
    print(init)
    init += 1

while init < final:
    print(init)
    init += 1
else:
    print(init, 'is not less than', final)

# Break the iteration

start = 0
end = 10
while start < end:
    print(start)
    if start == 5:
        break
    start += 1

# Iterate array elements
index = 0
list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
while index < len(list):
    print(list[index])
    index += 1
