import json, csv, cPickle as pickle, pprint, sys
def xtract_cooccur_for_case(c):
    #    cases = pickle.load(open('cases.pickle', 'r'))
    #c = cases[10000]
    cid = c['summary']['id']
    cyear = c['summary']['publicationYear']

    k = c['keywords']
    def xtractTerms(l, key):
        ret = filter(lambda x: x['type'] == key, l)
        return [x['text'].lower() for x in ret]
    
    def cleanTerms(terms):
        repMap = {'antibiotic':'antibiotic',
                  'warfarin':'warfarin',
                  'steroid':'steroid',
                  'methylprednizolone':'methylprednisolone',
                  'methylprednisolone':'methylprednisolone',
                  'cyclophosphamide':'cyclophosphamide',
                  'ciprofloxacin':'ciprofloxacin',
                  'anaesthetic':'anesthetic',
                  'anaesthetics':'anesthetic',
                  'analgesic':'analgesic',
                  'amlodipin':'amlodipin',
                  'allopurinol':'allopurinol',
                  'testosterone':'testosterone',
                  'diuretic':'diuretic',
                  'dalteparin':'dalteparin',
                  'cyclosporin':'cyclosporin',
                  'cytarabine':'cytarabine',
                  'cyclizine':'cyclizine',
                  'contraceptive':'contraceptive',
                  'ceftriaxon':'ceftriaxon',
                  'piperacillin':'piperacillin',
                  'penicillin':'penicillin',
                  'gonadotrophin':'gonadotropin'}

        stopwords = ['therapy', 'antagonist', 'receptor', 'treatment', 'agent', 'prophylaxis']
        l = []
        for term in terms:
            for sw in stopwords: term = term.replace(sw, '')
            for key in repMap.keys():
                if term.find(key) >= 0:
                    term = repMap[key]
            term = term.encode("ascii", "ignore").strip()
            l.append(term)
        return(list(set(l)))
                    
    conditionTerms = cleanTerms(xtractTerms(c['keywords'], 'Condition'))
    medicationTerms = cleanTerms(xtractTerms(c['keywords'], 'Medication'))
    interventionTerms = cleanTerms(xtractTerms(c['keywords'], 'Intervention'))
    pathogenTerms = cleanTerms(xtractTerms(c['keywords'], 'Pathogen'))

    ## dump co-occurrence lists
    cond_med = []
    for cond in conditionTerms:
        for med in medicationTerms:
            cond_med.append( [cid, cyear, cond, med] )

    path_med = []
    for path in pathogenTerms:
        for med in medicationTerms:
            path_med.append( [cid, cyear, path, med] )
    
    return {'cond_med':cond_med,
            'path_med':path_med}
            
cases = pickle.load(open('cases.pickle', 'r'))
o1 = csv.writer(open('cooccurr-cond-med.csv', 'w'))
o2 = csv.writer(open('cooccurr-path-med.csv', 'w'))
n = 0
for case in cases:
    foo = xtract_cooccur_for_case(case)
    o1.writerows(foo['cond_med'])
    o2.writerows(foo['path_med'])
    n += 1
    if n % 100 == 0:
        sys.stdout.write('\rProcessed %d cases' % (n))
        sys.stdout.flush()
print
