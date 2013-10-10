import cPickle as pickle, csv, sys
from operator import *
from itertools import *

condition = sys.argv[1].lower()
cases = pickle.load(open('cases.pickle'))
print 'Loaded %d cases' % (len(cases))

def hasCondition(case, cond):
    ret = filter(lambda x: x['type'] == 'Condition' and x['text'].lower().find(cond) >= 0, case['keywords'])
    return len(ret) > 0

cases = filter(lambda x: hasCondition(x, condition), cases)
print 'Got %d cases with %s as a condition' % (len(cases), condition)

## dump out year, country, count
countries = [ (x['summary']['publicationYear'], [ z['text'] for z in filter(lambda y: y['type'] == 'AuthorCountry', x['keywords'])]) for x in cases]
countries = filter(lambda x: len(x[1]) > 0, countries)

## now aggregate by year, and then get country frequencies
sorted_input = sorted(countries, key=itemgetter(0))
groups = groupby(sorted_input, key=itemgetter(0))
output = []
for year, viter in groups:
    cnames = list(chain.from_iterable([x[1] for x in viter]))
    counts = [(k, len(list(g))) for k, g in groupby(sorted(cnames))]
    counts = [ list(chain.from_iterable(x)) for x in zip( repeat([condition], len(counts)), repeat([year], len(counts)), counts ) ]
    for i in counts: output.append(i)
o = csv.writer(open('condition_country.csv', 'w'))
o.writerow(['condition', 'year', 'cname', 'count'])
o.writerows(output)
    
