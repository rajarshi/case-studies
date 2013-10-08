import urllib, sys, os, json, time
import cPickle as pickle

API_TOKEN = open('API_TOKEN', 'r').read()
HOST = 'http://www.casesdatabase.com'
SEARCH = '/api/search/?query=* AND (PublicationYear:%d)'
CASE = '/api/case/%s'

def getIds():
    for year in range(2000, 2014):
        url = HOST + SEARCH % (year) + "&authorization="+API_TOKEN
        print url
        data = urllib.urlopen(url).read()

        data = data.decode('utf8', 'replace')
        data = json.loads(data)
        print '%d entries for %d' % (len(data['results']), year)
        pj = json.dumps(data, indent=4, sort_keys=True)

        o = open('data-%d.json' % (year), 'w')
        o.write(pj)
        o.close()

        time.sleep(5)

def getCases():
    idlist = []
    for year in range(2000, 2014):
        data = json.load(open('data-%d.json' % (year)))
        for elem in data['results']:
            idlist.append(elem['id'])
    print 'Got %d case ids' % (len(idlist))

    cases = []
    n = 0
    for cid in idlist:
        url = HOST + CASE % (cid) + "?authorization="+API_TOKEN
        data = urllib.urlopen(url).read()
        data = data.decode('utf8', 'replace')
        try:
            data = json.loads(data)
            cases.append(data)            
        except ValueError, e:
            pass

        n += 1
        if n % 50 == 0:
            pickle.dump(cases, open('cases.pickle', 'wb'))
            sys.stdout.write("\rDumped %d cases\n" % (n))
            sys.stdout.flush()
            time.sleep(10)
        sys.stdout.write("\rGot %d cases     " % (n))
        sys.stdout.flush()
    print

if __name__ == '__main__':
    getIds()
    getCases()
