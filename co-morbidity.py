import cPickle as pickle
import random, sys, collections, csv
from itertools import *
from collections import Counter

def flatten(x):
    result = []
    for el in x:
        if hasattr(el, "__iter__") and not isinstance(el, basestring):
            result.extend(flatten(el))
        else:
            result.append(el)
    return result

def samplePairs(pair, pop, n=10000):
    nobs = 0
    for i in xrange(n):
        spair = sorted(random.sample(pop,2))
        if pair == spair:
            nobs += 1
    return nobs/float(n)

def cleanTerms(terms):
    repMap = {'comatose':'coma',
              'seizures':'seizure',
              'foetal':'fetal',
              'haematomas':'Haematoma',
              'disorders':'disorder',
              'tumour':'tumor',
              'abnormalities':'abnormality',
              'tachycardias':'tachycardias',
              'lymphomas': 'lymphoma',
              'tuberculosis':'tuberculosis',
              'hiv':'hiv',
              'anaemia':'anemia',
              'carcinoma':'carcinoma',
              'metastases':'metastasis',
              'metastatic':'metastasis',
              '?':'-'}
    stopwords = ['state','syndrome'', low grade', 'fever', 'type ii', 'mellitus', 'type 2', 'type 1', 'systemic', 'homogeneous', 'disease']
    l = []
    terms = [x.lower().strip() for x in terms]
    for term in terms:
        for sw in stopwords: term = term.replace(sw, '')
        for key in repMap.keys():
            if term.find(key) >= 0: term = repMap[key]
        term = term.encode("ascii", "ignore").replace('\n','').strip()
        l.append(term)
    l = filter(lambda x: x != '-', l)
    return(list(set(l)))
        
def parallelWorker(item):
    foo, obs, pop = item
    pair,count = foo
    the_pair = None
    for p, c, f in obs:
        if p[0] == pair[0] and p[1] == pair[1]:
            the_pair = [list(p), c, f]
            break
    if the_pair is None:
        raise Exception("Couldn't find observed data for %s"  % (','.join(pair[0])))
    ## get sampled prob
    pvalue = samplePairs(the_pair[0], pop, int(1e7))
    the_pair.extend([pvalue])
    the_pair = flatten(the_pair)
    print the_pair
    return the_pair

def getMorbidityByCondition(freqs, condition, exact = True):
    if exact:
        return filter(lambda x: condition in x[0], freqs)
    else:
        return filter(lambda x: x[0][0].find(condition) >= 0 or x[0][1].find(condition) >= 0, freqs)
    
if __name__ == '__main__':
    cases = pickle.load(open('cases.pickle'))
    allpairs = []
    for case in cases:
        ## get all conditions for this case
        conds = filter(lambda x: x['type'] == 'Condition', [x for x in case['keywords']])
        conds = cleanTerms([x['text'] for x in conds])
        if len(conds) == 0: continue
        conds.sort()
        pairs = [ (x,y) for x,y in list(combinations(conds, 2))]
        allpairs.extend(pairs)

    print 'Got %d condition pairs' % (len(allpairs))
    upair = set(allpairs)
    print 'Got %d unique pairs' % (len(upair))
    uconds = set(chain.from_iterable(upair))
    print 'Got %d unique conditions' % (len(uconds))
    
    ## for each pair, get the count of occurrence
    freqs = Counter(allpairs)
    freqs = freqs.items()

    ## examine how many pairs we get by varying min_freq
    freq_counts = [ (mfreq, len(filter(lambda x: x[1] >= mfreq, freqs))) for mfreq in [1,2,5,10,20,40,50,75,100,200] ]
    for a,b in freq_counts: print a,b

    ###########################################################
    ## remove pairs that occur only once. This represents our
    ## working set of pairs
    freqs = filter(lambda x: x[1] > 1, freqs)
    nupair = len(freqs)
    npair = reduce(lambda x,y: x+y, [x[1] for x in freqs])
    print 'Got %d unique pairs occuring more than once (total of %d pairs)' % (len(freqs), npair)

    ## calculate propensities and empirical p-values. For that we create the population of
    ## individual conditions - note the population will contain repeats of the pairs (according
    ## to their count) and hence repeats of the individual conditions
    population = [x[0] * x[1] for x in freqs]
    population = list(chain.from_iterable(population))
    obs = [ (pair, count, count/float(npair)) for pair, count in freqs]

    ## pull out all co-morbidities that include tuberculosis as one of the conditions
    ## output the (non tuberculosis) conditions, using the frequency of occurrence of the
    ## co-morbidity to generate repeats
    condition = 'tuberculosis'
    conds = getMorbidityByCondition(freqs, condition, exact=False)
    conds.sort(key = lambda x: x[1], reverse=True)
    print 'Found %d co-morbidities that include %s' % (len(conds), condition)
    conds = map(lambda x: [''.join(x[0]).replace(condition, '')] * x[1], conds)
    ## use the contents of conds to make a word cloud
    conds = list(chain.from_iterable(conds))
    
    ## Use a specific value for min_freq to generate our heatmap image
    freq_min = 150
    ofile = open('comorb-%d.csv' % (freq_min), 'w')
    o = csv.writer(ofile)
    o.writerow(['cond1', 'cond2', 'count', 'frac', 'sampled'])
    ffreqs = filter(lambda x: x[1] >= freq_min, freqs)
    print 'Got %d unique pairs (%d unique conditions) with occurence >= %d' % \
        (len(ffreqs), len(set(chain.from_iterable([x[0] for x in ffreqs]))), freq_min)

    from multiprocessing import Pool
    pool = Pool(processes=6)
    arglist = []
    for i in ffreqs:
        arglist.append( (i, obs, population) )
    results = pool.map(parallelWorker, arglist)
    o.writerows(results)
    ofile.close()
