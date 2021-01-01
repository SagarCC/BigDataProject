import map_reduce
import numpy.random
import random

def paretosample(n,power=2.0):
  # Returns a number less than or equal to n+1

  m = n+1
  while m > n: m = numpy.random.zipf(power)
  return m

def initialize(n,power):
  # Returns a Python dictionary representing a web
  # with n pages, and where each page k is linked to by
  # L_k random other pages.  The L_k are independent and
  # identically distributed random variables with a
  # shifted and truncated Pareto probability mass function
  # p(l) proportional to 1/(l+1)^power.

  # The representation used is a Python dictionary with
  # keys 0 through n-1 representing the different pages.
  # i[j][0] is the estimated PageRank, initially set at 1/n,
  # i[j][1] the number of outlinks, and i[j][2] a list of
  # the outlinks.

  # This dictionary is used to supply (key,value) pairs to
  # both mapper tasks defined below.

  # initialize the dictionary
  i = {} 
  for j in xrange(n): i[j] = [1.0/n,0,[]]
  
  # For each number from 0 to n-1 add lk will call paretosample
  # It will have a maximum value of n+1 but 1 is subtracted ,so 
  # lk<=n, the list 'values' will have a size lk with values <=n
  # We are iterating through all elements in the list 'values'
  # increment counter which is in 2nd index of the list present 
  # as a value of the dictionary and 3rd index of that list will 
  # the element itself
    
  for k in xrange(n):
    lk = paretosample(n+1,power)-1
    values = random.sample(xrange(n),lk)
    for j in values:
      i[j][1] += 1 # increment the outlink count for page j
      i[j][2].append(k) # insert the link from j to k

  #print graph
  print "";
  print "Graph representing the web pages\n";
  for k in xrange(n):
    if i[k][1]==0:
      print "Page "+str(k)+" links to 0 pages";
    elif i[k][1]==1:
      print "Page "+str(k)+" links to 1 page "+str(i[k][2]); 
    else:
      print "Page "+str(k)+" links to "+str(i[k][1])+" pages "+str(i[k][2]);
  print("\n");

  #printing initial page rank values
  print "Inital page rank values of web pages\n";
  for k in xrange(n):
    print "Page rank of page "+str(k)+" = "+str(i[k][0]);
  print "\n";
  return i

def ip_mapper(input_key,input_value):
  # The mapper returns [(1,pagerank)] if the page is dangling,
  # and otherwise returns nothing.
  
  if input_value[1] == 0: return [(1,input_value[0])]
  else: return []

def ip_reducer(input_key,input_value_list):
  # The reducer used to compute the inner product.  Simply
  # sums the pageranks listed in the input value list, which
  # are all the pageranks for dangling pages.

  return sum(input_value_list)

def pr_mapper(input_key,input_value):
  # The mapper used to update the PageRank estimate.  Takes
  # as input a key for a webpage, and as a value the corresponding
  # data, as described in the function initialize.  It returns a
  # list with all outlinked pages as keys, and corresponding values
  # just the PageRank of the origin page, divided by the total
  # number of outlinks from the origin page.  Also appended to
  # that list is a pair with key the origin page, and value 0.
  # This is done to ensure that every single page ends up with at
  # least one corresponding (intermediate_key,intermediate_value)
  # pair output from a mapper.
  
  return [(input_key,0.0)]+[(outlink,input_value[0]/input_value[1])
          for outlink in input_value[2]]

def pr_reducer_inter(intermediate_key,intermediate_value_list,
                     s,ip,n):
  # This is a helper function used to define the reducer used
  # to update the PageRank estimate.  Note that the helper differs
  # from a standard reducer in having some additional inputs:
  # s (the PageRank parameter), ip (the value of the inner product
  # between the dangling pages vector and the estimated PageRank),
  # and n, the number of pages.
  
  return (intermediate_key,
          s*sum(intermediate_value_list)+s*ip/n+(1.0-s)/n)

def pagerank(i,s=0.85,tolerance=0.00001):
  # Returns the PageRank vector for the web described by i,
  # using parameter s.  The function stops execution 
  # when absolute difference of sum of new page rank vales 
  # and sum of old page rank values is less than tolerance.
  
  n = len(i)
  iteration = 1
  change = 2 # initial estimate of error
  while change > tolerance:
    print "Iteration: "+str(iteration)
    # Run the MapReduce job used to compute the inner product
    # between the vector of dangling pages and the estimated
    # PageRank.
    ip_list = map_reduce.map_reduce(i,ip_mapper,ip_reducer)

    # the if-else clause is needed in case there are no dangling
    # pages, in which case MapReduce returns ip_list as the empty
    # list.  Otherwise, set ip equal to the first (and only)
    # member of the list returned by MapReduce.
    if ip_list == []: ip = 0
    else: ip = ip_list[0]

    # Dynamically define the reducer used to update the PageRank
    # vector, using the current values for s, ip, and n.
    pr_reducer = lambda x,y: pr_reducer_inter(x,y,s,ip,n)

    # Run the MapReduce job used to update the PageRank vector.
    new_i = map_reduce.map_reduce(i,pr_mapper,pr_reducer)

    # Compute the new estimate of error.
    change = sum([abs(new_i[j][1]-i[j][0]) for j in xrange(n)])
    #print "Change in l1 norm: "+str(change)

    # Update the estimate PageRank vector.
    for j in xrange(n): i[j][0] = new_i[j][1]

    print "Page rank values of web pages\n";
    for k in xrange(n):
      print "Page rank of page "+str(k)+" = "+str(i[k][0]);
    print "\n";
    
    iteration += 1
  return i

print "Enter N the number of pages"
n = int(input())
i = initialize(n,2.0)
new_i = pagerank(i,0.85,0.0001)
