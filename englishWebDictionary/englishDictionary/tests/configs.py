headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0'
}
htmlDir = 'htmlWords/'
jsonDir = 'jsonWords/'
metawordIdFileName = 'metawordIds'

with open(metawordIdFileName) as f:
    metawordIds = f.read().splitlines()

def htmlFileName(metawordId):
    return htmlDir + metawordId + '.html'
def jsonFileName(metawordId):
    return jsonDir + metawordId + '.json'
