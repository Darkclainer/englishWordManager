from bs4 import BeautifulSoup, SoupStrainer

class NoSuggestions(Exception): pass

def parse(htmlText, parser='html.parser', maxSuggestions = 20):
    soup = BeautifulSoup(htmlText, parser)
    entryBody = soup.find(class_='entry-body__el')

    suggestionList = entryBody.find('ol', class_='prefix-block', recursive=False)
    if not suggestionList:
        raise NoSuggestions

    listElements = suggestionList.findAll('li')
    return [ extractSpelling(listElement) for listElement in listElements ]

def extractSpelling(listElement):
    return str(listElement.find(class_='prefix-item').string)

    
