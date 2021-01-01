import itertools

def map_reduce(i,mapper,reducer):
  intermediate = []
  for (key,value) in i.items():
    intermediate.extend(mapper(key,value))
  groups = {}

#itertools.groupby takes 2 parameters 
#first parameter an iterable like list, tuple or dictionary
#second a function that determines the key for each element in the iterable

  for key, group in itertools.groupby(sorted(intermediate),lambda x: x[0]):
    groups[key] = list([y for x, y in group])
  return [reducer(intermediate_key,groups[intermediate_key])
          for intermediate_key in groups]
