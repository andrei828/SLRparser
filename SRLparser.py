import copy
from collections import deque

beginNonTerminal = None
terminals = set(['$'])
nonTerminals = set()
dfa = {}

def readGrammatic():
  global terminals
  global beginNonTerminal

  grammatic = {}
  with open('grammatic4.txt', 'r') as inputFile:
    while inputFile:
      tmp = inputFile.readline().split('\n')[0].split(' ')
      if tmp == ['']:
        break
      if not beginNonTerminal:
        beginNonTerminal = tmp[0]

      grammatic[tmp[0]] = []
      currentValue = []
      nonTerminals.add(tmp[0])
      for item in tmp[2:]:
        if item == '|':
          grammatic[tmp[0]].append(currentValue[:])
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
    nonTerminals.remove(beginNonTerminal)
    if '@' in terminals:
      terminals.remove('@')
    return grammatic

def printGrammatic(grammatic):
  for item in grammatic:
    print(item, '->', end=' ')
    for rule in grammatic[item]:
      print(" ".join(rule), end=' | ')
    print()

def printGotoTable(table):
  print('Goto table:')
  print('\t', '\t'.join(nonTerminals))
  for i in range(len(table)):
    print(i, end='\t')
    for val in table[i].values():
      print(val, end='\t')
    print()

def printActionTable(table):
  print('Action table:')
  print('\t', '\t'.join(terminals))
  for i in range(len(table)):
    print(i, end='\t')
    for val in table[i].values():
      print(val, end='\t')
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
          tmp = getFirst(grammatic, value[0], visited)
          totalEps = 0
          for i in value[1:]:
            if '@' in tmp:
              totalEps += 1
              tmp |= getFirst(grammatic, i, copy.deepcopy(visited))
            else:
              break
          if totalEps < len(value) and '@' in tmp:
            tmp.remove('@')
          result |= tmp
          # result |= getFirst(grammatic, value[0], visited)
    return result

def first(grammatic):
  return {item: getFirst(grammatic, item, set()) for item in grammatic}

'''modify for epsilon if necesarry'''
def follow(grammatic, first):
  flw = {item: set() for item in grammatic}
  flw[beginNonTerminal].add('$')
  for _ in range(2):
    for key, values in grammatic.items():
      for value in values:
        for i in range(len(value) - 1):
          if value[i] in grammatic:
            if value[i + 1] in first:
              tmp = copy.deepcopy(first[value[i + 1]])
              if '@' in tmp:
                tmp.remove('@')
              flw[value[i]] |= tmp
            else:
              flw[value[i]].add(value[i + 1])
        # if len(value) >= 2 and value[-1] != '@':
        #   if value[-2] in grammatic:
        #     if value[-1] in first:
        #       tmp = copy.deepcopy(first[value[-1]])
        #       if '@' in tmp:
        #         tmp.remove('@')
        #       flw[value[-2]] |= tmp
        #     else:
        #       flw[value[-2]].add(value[-1])
          # if value[i] in grammatic:
          #   if value[i + 1] in first:
          #     flw[value[i]] |= first[value[i + 1]]
          #   else:
          #     flw[value[i]].add(value[i + 1])

    for key, values in grammatic.items():
      for value in values:
        if value[-1] in flw:
          tmp = copy.deepcopy(flw[key])
          if '@' in flw[key]:
            tmp.remove('@')
          flw[value[-1]] |= tmp

    for key, values in grammatic.items():
      for value in values:
        if len(value) > 2 and value[-1] in first and '@' in first[value[-1]] and value[-2] in grammatic:
          flw[value[-2]] |= flw[key]

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

  return found        

def constructItems(grammatic):
  firstItem = buildFirstItem(grammatic, beginNonTerminal)
  firstItem = closure(grammatic, firstItem)
  items = {0: firstItem}
  k = 1
  while True:
    itemsListSize = len(items)
    tmp = []
    beforeK = k
    for num, dictionary in items.items():
      for key in dictionary:
        for value in dictionary[key]:
          for i in range(len(value) - 1):
            if value[i] == '.' and value[i + 1] != '@':
              
              newItem = closure(grammatic, goto(items[num], value[i + 1]))
              # print(num, value[i + 1], isItemPresent(newItem, items))
              isConnected = isItemPresent(newItem, items)
              if not isConnected and newItem not in tmp:
                  # print('GOTO(', num, value[i + 1], ') ', newItem)
                  dfa[(num, value[i + 1])] = k
                  tmp.append(copy.deepcopy(newItem))
              else:
                dfa[(num, value[i + 1])] = isConnected

    k = beforeK
    for i in tmp:
      items[k] = i
      k += 1
    
    if itemsListSize == len(items):
      return items

def buildParsingTable(first, follow, items, dfa, terminals, nonTerminals, rules):
  gotoTable = [{i: 0 for i in nonTerminals} for _ in range(len(items))]
  actionTable = [{i: 0 for i in terminals} for _ in range(len(items))]

  '''
  Action Table
  '''
  # shift operations
  for tupl, value in dfa.items():
    if tupl[1] in terminals:
      if actionTable[tupl[0]][tupl[1]] != 0:
        print('not a valid grammar')
        return (None, None)
      actionTable[tupl[0]][tupl[1]] = 's' + str(value)

  # reduce operations
  for dictKey, dictValues in items.items():
    for key, matrix in dictValues.items():
      for value in matrix:
        if value[-1] == '.' or (len(value) == 2 and value == ['.', '@']):
          toSearch = None
          if len(value) == 2 and value == ['.', '@']:
            toSearch = {key: ['@']}
          else:
            valCopy = value[:]
            valCopy.pop()
            toSearch = {key: valCopy}
          
          for ruleKey, ruleValue in rules.items():
            if ruleValue == toSearch:
              for followItem in follow[key]:
                if followItem != '@':
                  if actionTable[dictKey][followItem] != 0:
                    print('not a valid grammar')
                    return (None, None)
                  actionTable[dictKey][followItem] = 'r' + str(ruleKey)
  
  # accept operations
  
  for dictKey, dictValues in items.items():
    for key, matrix in dictValues.items():
      for value in matrix:
        if key == beginNonTerminal and value[-1] == '.':
          actionTable[dictKey]['$'] = 'acc'
  # actionTable[1]['$'] = 'acc' easier this way   

  '''
  Goto Table
  '''
  for tupl, value in dfa.items():
    if tupl[1] in nonTerminals:
      gotoTable[tupl[0]][tupl[1]] = value

  return actionTable, gotoTable


def parseInput(rules, actionTable, gotoTable, inputValue, log=False):
  state = ([0], inputValue.split(' '))
  while True:
    currentState, currentValue = state[0][-1], state[1][0]
    cell = actionTable[currentState][currentValue]
    if log:
      print('Stack:', ' '.join([str(i) for i in state[0]]), '\nInput:', ''.join(state[1]), end='\n\n')
    if cell == 0:
      return 'Input ' + inputValue + ' NOT accepted'
    elif cell == 'acc':
      return 'Input ' + inputValue + ' raccepted'
    # shift operation
    elif cell[0] == 's':
      number = int(cell[1:])
      state[0].append(state[1].pop(0))
      state[0].append(number)
    # reduce operation
    elif cell[0] == 'r':
      number = int(cell[1:])
      numberOfItems = list(rules[number].values())[0]
      if len(numberOfItems) == 1 and numberOfItems == ['@']:
        smr = state[0][-1]
        state[0].append(list(rules[number].keys())[0])
        state[0].append(gotoTable[smr][state[0][-1]])
      else:
        for _ in range(len(numberOfItems)):
          state[0].pop()
          state[0].pop()
        smr = state[0][-1]
        state[0].append(list(rules[number].keys())[0])
        state[0].append(gotoTable[smr][state[0][-1]])
      

grammatic = readGrammatic()
printGrammatic(grammatic)

rules = setRules(grammatic)
items = constructItems(grammatic)

firstSet = first(grammatic)
followSet = follow(grammatic, firstSet)

print('First')
print(firstSet)
print('Follow')
print(followSet)
actionTable, gotoTable = buildParsingTable(firstSet, followSet, items, dfa, terminals, nonTerminals, rules)
if actionTable != None and gotoTable != None:
  printActionTable(actionTable)
  printGotoTable(gotoTable)
  print(parseInput(rules, actionTable, gotoTable, 'n + ( n ) $'))
  # print(parseInput(rules, actionTable, gotoTable, 'c d c c d $'))
  # print(parseInput(rules, actionTable, gotoTable, 'id * id + id $'))
  # print(parseInput(rules, actionTable, gotoTable, '( id ) id $'))
  # print(parseInput(rules, actionTable, gotoTable, '( id + id $'))
  # print(parseInput(rules, actionTable, gotoTable, 'id ) + id $'))
  # print(parseInput(rules, actionTable, gotoTable, '( id * id + id ) $'))
