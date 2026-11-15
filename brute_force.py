import time


n = int(input("Please enter your n value: "))
maxFires = int(input("Please enter the max fire station num: "))
a = input("Please enter your a string: ").split("$")
for i in range (0, len(a)):
    a[i] = a[i].split(",")
m = len(a[0])
w = input("Please enter your w string: ").split(",")
minCost = 0
minIndex = 0
testMaker = []
start = time.perf_counter()
for index in range(0, pow(2, n)):
    testMaker.append(bin(index)[2:])
for index1 in range (1, len(testMaker)):
    c = 0
    for j in range (0, m):
        cost = 1
        for i in range (len(testMaker[index1]) - 1, -1, -1):
            cost *= 1 - int(a[i + n - len(testMaker[index1])][j]) * int(testMaker[index1][i:i+1])
        c -= int(w[j]) * (1 - cost)
    if c < minCost:
        numFire = 0
        for i in range (0, len(testMaker[index1])):
            numFire += int(testMaker[index1][i:i+1])
        if numFire < maxFires + 1:
            minCost = c
            minIndex = index1
while(len(testMaker[minIndex]) < n):
    testMaker[minIndex] = "0" + testMaker[minIndex]
print(testMaker[minIndex][::-1])
print(minCost)
