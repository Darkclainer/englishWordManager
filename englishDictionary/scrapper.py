import requests
import urllib

from . import wordParser
from . import suggestionParser
from . import metaword

class NoSuchWord(Exception): pass

class PageException(Exception): pass
class CannotRetreivePage(PageException): pass
class CannotParsePage(PageException): pass

_wordDictionaryUrl = 'https://dictionary.cambridge.org/dictionary/english/'
_suggestionDictionaryUrl = 'https://dictionary.cambridge.org/spellcheck/english/'
_searchDirectionaryUrl = 'https://dictionary.cambridge.org/search/english/direct/'

class Requester:
    def __init__(self, headers=None, timeout=1):
        self.session = requests.Session()
        if headers:
            self.session.headers.update(headers)
        self.timeout = timeout

    def close(self):
        self.session.close()

    def _get(self, url, **kargs):
        try:
            response = self.session.get(url, timeout=self.timeout, **kargs)
            response.raise_for_status()
            return response
        
        except Exception as e:
            raise CannotRetreivePage() from e

    def _getMetaword(self, url):
        response = self._get(url)
        if response.status_code != requests.status_codes.codes.ok:
            raise CannotRetreivePage()
        return _parsePage(response, wordParser.parse)

    def _getSuggestions(self, url):
        response = self._get(url)
        if response.status_code != requests.status_codes.codes.ok:
            raise CannotRetreivePage()
        return _parsePage(response, suggestionParser.parse)
    
    def searchMetaword(self, query):
        url = _searchDirectionaryUrl
        params = {'q': query}

        response = self._get(url, params=params, allow_redirects=False)
        if response.status_code != requests.status_codes.codes.found:
            raise CannotRetreivePage()
        redirect = response.headers['Location']
        
        if redirect.startswith(_wordDictionaryUrl):
            return Requester.WebMetaword(self, redirect)
        elif redirect.startswith(_suggestionDictionaryUrl):
            suggestions = self._getSuggestions(redirect)
            raise metaword.Suggestions(suggestions)
        else:
            raise NoSuchWord()

    class WebMetaword:
        def __init__(self, requester, url):
            self.requester = requester
            self.url = url
            
            path = urllib.parse.urlparse(url).path
            self.metawordId = path.rsplit('/',1)[1]

        def retreive(self):
            return self.requester._getMetaword(self.url)


def requestWord(word, **karg):
    url = _searchDirectionaryUrl
    params = {'q': word}

    response = _getPage(url, params=params, allow_redirects=True, **karg)
    if response.status_code != requests.status_codes.codes.ok:
        raise CannotRetreivePage()
    
    # where we are?
    if response.url.startswith(_wordDictionaryUrl):
        return _parsePage(response, wordParser.parse)
    elif response.url.startswith(_suggestionDictionaryUrl):
        suggestions = _parsePage(response, suggestionParser.parse)
        raise metaword.Suggestions(suggestions)
    else:
        raise NoSuchWord()

def _getPage(url, allow_redirects=False, **karg):
    try:
        response = requests.get(url, allow_redirects=allow_redirects, **karg)
        response.raise_for_status()
        return response
    except Exception as e:
        raise CannotRetreivePage from e

def _parsePage(page, parser):
    try:
        return parser(page.content)
    except Exception as e:
        raise CannotParsePage from e

