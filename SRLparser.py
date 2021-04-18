import copy
from collections import deque

beginNonTerminal = None
terminals = set(['$'])
nonTerminals = set()
dfa = {}

def readGrammatic():
  global terminals
  global nonTerminals
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
          nonTerminals.add(tmp[0])
          terminals |= set(currentValue)
          currentValue = []
        else:
          currentValue.append(item)
          terminals.add(item)
      try:
        grammatic[tmp[0]].append(currentValue[:])
        terminals |= set(currentValue)
      except:
        pass

    for item in nonTerminals:
      if item in terminals:
        terminals.remove(item)

    return grammatic

def printGrammatic(grammatic):
  for item in grammatic:
    print(item, ':', end=' ')
    for rule in grammatic[item]:
      print(" ".join(rule), end=' | ')
    print()

def getFirst(grammatic, symbol, visited=set()):
  if symbol not in grammatic:
    return set([symbol])
  else:
    visited.add(symbol)
    result = set()
    for value in grammatic[symbol]:
      if len(value) > 0:
        if value[0] not in grammatic:
          result.add(value[0])
        elif value[0] not in visited:
          result |= getFirst(grammatic, value[0], visited)
    return result

def first(grammatic):
  return {item: getFirst(grammatic, item, set()) for item in grammatic}

'''modify for epsilon if necesarry'''
def follow(grammatic, first):
  flw = {item: set() for item in grammatic}
  flw[beginNonTerminal].add('$')
  for key, values in grammatic.items():
    for value in values:
      for i in range(len(value) - 1):
        if value[i] in grammatic:
          if value[i + 1] in first:
            flw[value[i]] |= first[value[i + 1]]
          else:
            flw[value[i]].add(value[i + 1])

  for key, values in grammatic.items():
    for value in values:
      if value[-1] in flw:
        flw[value[-1]] |= flw[key]
  return flw  

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
    
    # big potential problem with this condition
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

def setRules(grammatic):
  result = {}
  k = 0
  for key, matrix in grammatic.items():
    for value in matrix:
      result[k] = {key: value}
      k += 1
  return result

def isItemPresent(currentItem, items):
  found = True
  searchList = []
  currentList = []
  # print('-----------------------')
  # print(currentItem)
  # print('000009090909090')
  # print(items)
  helper = {}
  # print(items)
  for masterKey, itemDict in items.items():
    for key in itemDict:
      for value in itemDict[key]:
        searchList.append([key] + value)
        if masterKey not in helper:
          helper[masterKey] = [[key] + value]
        else:
          helper[masterKey].append([key] + value)
  for currentKeys in currentItem:
    for values in currentItem[currentKeys]:
      currentList.append([currentKeys] + values)

  for current in currentList:
    if current not in searchList:
      found = False
  
  if found == True:
    for itemNum, values in helper.items():
      total = 0
      for current in currentList:
        if current in values:
          total += 1
      if total == len(currentList):
        return itemNum
    # print(helper)
  # print(found)
  # print(searchList)
  # print(helper)
  # print('-----------------------')
  return found        

def constructItems(grammatic):
  global dfa
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
    beforeK = k
    for num, dictionary in items.items():
      for key in dictionary:
        for value in dictionary[key]:
          for i in range(len(value) - 1):
            if value[i] == '.':
              
              newItem = closure(grammatic, goto(items[num], value[i + 1]))
              # print(num, value[i + 1], isItemPresent(newItem, items))
              isConnected = isItemPresent(newItem, items)
              if not isConnected and newItem not in tmp:
                  # print('GOTO(', num, value[i + 1], ') ', newItem)
                  dfa[(num, value[i + 1])] = k
                  tmp.append(copy.deepcopy(newItem))
              else:
                dfa[(num, value[i + 1])] = isConnected


  # itemsListSize = len(items)
  # tmp = []
  # beforeK = k
  # for num, dictionary in items.items():
  #   for key in dictionary:
  #     for value in dictionary[key]:
  #       for i in range(len(value) - 1):
  #         if value[i] == '.':
  #           newItem = closure(grammatic, goto(items[num], value[i + 1]))
            
  #           if not isItemPresent(newItem, items):
  #             if newItem not in tmp:
  #               # print('GOTO(', num, value[i + 1], ') ', newItem)
  #               dfa[(num, value[i + 1])] = k
  #               tmp.append(copy.deepcopy(newItem))
    k = beforeK
    for i in tmp:
      items[k] = i
      k += 1
    
    if itemsListSize == len(items):
      return items

def printGotoTable(table):
  print('\t', '\t'.join(nonTerminals))
  for i in range(len(table)):
    print(i, end='\t')
    for val in table[i].values():
      print(val, end='\t')
    print()

def printActionTable(table):
  print('\t', '\t'.join(terminals))
  for i in range(len(table)):
    print(i, end='\t')
    for val in table[i].values():
      print(val, end='\t')
    print()

def buildParsingTable(first, follow, items, dfa, terminals, nonTerminals):
  gotoTable = [{i: 0 for i in nonTerminals} for _ in range(len(items))]
  actionTable = [{i: 0 for i in terminals} for _ in range(len(items))]
  for tupl, value in dfa.items():
    if tupl[1] in terminals:
      actionTable[tupl[0]][tupl[1]] = value
  printActionTable(actionTable)
  printGotoTable(gotoTable)
  return gotoTable

grammatic = readGrammatic()
# print(grammatic)
printGrammatic(grammatic)
# print(setRules(grammatic))

# print(terminals) 
print()
items = constructItems(grammatic)
# print(items)
print('DFA:')
print(dfa)
print()
# for key, value in dfa.items():
#   print(value, items[value])
# print()

firstSet = first(grammatic)
followSet = follow(grammatic, firstSet)

print(buildParsingTable(firstSet, followSet, items, dfa, terminals, nonTerminals))