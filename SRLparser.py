import copy
from collections import deque

beginNonTerminal = None

def readGrammatic():
  global beginNonTerminal
  grammatic = {}
  with open('grammatic.txt', 'r') as inputFile:
    # for _ in range(2):
    while inputFile:
      tmp = inputFile.readline().split('\n')[0].split(' ')
      if tmp == ['']:
        break
      if not beginNonTerminal:
        beginNonTerminal = tmp[0]

      grammatic[tmp[0]] = []
      currentValue = []
      for item in tmp[2:]:
        if item == '|':
          grammatic[tmp[0]].append(currentValue[:])
          currentValue = []
        else:
          currentValue.append(item)
      try:
        grammatic[tmp[0]].append(currentValue[:])
      except:
        grammatic[tmp[0]]

    return grammatic

def printGrammatic(grammatic):
  for item in grammatic:
    print(item, ':', end=' ')
    for rule in grammatic[item]:
      print(" ".join(rule), end=' | ')
    print()


def buildFirstItem(grammatic, key):
  result = {key: []}
  for item in grammatic[key]:
    dotRule = ['.']
    for element in item:
      dotRule.append(element)
    result[key].append(dotRule)

  return result

def closure(grammatic, item):
  while True:
    itemSize = 0
    for val in item.values():
      itemSize += len(val)

    tmp = []
    for element in item:
      for value in item[element]:
        for i in range(len(value) - 1):
          if value[i] == '.':
            if value[i + 1] in grammatic:
              tmp.append(buildFirstItem(grammatic, value[i + 1]))

    for dictionary in tmp:
      for key in dictionary:
        if key in item:
          for value in dictionary[key]:
            if value not in item[key]:
              item[key].append(value)
        else:
          item[key] = dictionary[key]
    # big potential problem with this criteria
    currentSize = 0
    for val in item.values():
      currentSize += len(val)
    
    if itemSize == currentSize:
      return item

def goto(item, symbol):
  result = {}
  for key in item:
    for value in item[key]:
      for i in range(len(value) - 1):
        if value[i] == '.' and value[i + 1] == symbol:
          tmp = value[:]
          tmp[i], tmp[i + 1] = tmp[i + 1], tmp[i]
          if key in result:
            result[key].append(tmp)
          else:
            result[key] = [tmp]
  return result

def isItemPresent(currentItem, items):
  found = True
  searchList = []
  currentList = []
  for itemDict in items.values():
    for key in itemDict:
      for value in itemDict[key]:
        searchList.append([key] + value)

  for currentKeys in currentItem:
    for values in currentItem[currentKeys]:
      currentList.append([currentKeys] + values)

  for current in currentList:
    if current not in searchList:
      found = False

  return found        

def constructItems(grammatic):
  firstItem = buildFirstItem(grammatic, beginNonTerminal)
  firstItem = closure(grammatic, firstItem)
  items = {0: firstItem}
  k = 1
  # newItem = closure(grammatic, goto(items[0], '('))
  # print(closure(grammatic, goto(items[0], '(')))
  # print(isItemPresent(newItem, items))
  # print(firstItem)
  while True:
    itemsListSize = len(items)
    tmp = []
    for num, dictionary in items.items():
      for key in dictionary:
        for value in dictionary[key]:
          for i in range(len(value) - 1):
            if value[i] == '.':
              newItem = closure(grammatic, goto(items[num], value[i + 1]))
              if not isItemPresent(newItem, items):
                print('GOTO(', num, value[i + 1], ') ', newItem)
                if newItem not in tmp:
                  tmp.append(copy.deepcopy(newItem))

    for i in tmp:
      items[k] = i
      k += 1
    
    if itemsListSize == len(items):
      return items

  # return firstItem


grammatic = readGrammatic()
# print(grammatic)
printGrammatic(grammatic)
print()
print(constructItems(grammatic))