

def readGrammatic():
  grammatic = {}
  with open('grammatic.txt', 'r') as inputFile:
    # for _ in range(2):
    while inputFile:
      tmp = inputFile.readline().split('\n')[0].split(' ')
      if tmp == ['']:
        break
      
      grammatic[tmp[0]] = []
      currentValue = []
      for item in tmp[2:]:
        if item == '|':
          grammatic[tmp[0]].append(currentValue[:])
          currentValue = []
        else:
          currentValue.append(item)
      grammatic[tmp[0]].append(currentValue[:])

    return grammatic

def printGrammatic(grammatic):
  for item in grammatic:
    print(item, ':', end=' ')
    for rule in grammatic[item]:
      print(" ".join(rule), end=' | ')
    print()

grammatic = readGrammatic()
print(grammatic)
printGrammatic(grammatic)