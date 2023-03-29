import sys
 
# for dict
dict = {}
for i in range(1, 1000001):
    dict[i] = i
print(sys.getsizeof(dict))
 
# for list of tuples
lst = list(range(1, 1000001))
print(sys.getsizeof(lst))