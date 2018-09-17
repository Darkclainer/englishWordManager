import itertools

def _tokenize(text):
    wordvoid = (''.join(ch for ch in w if ch.isalpha()) for w in text.split(' '))
    return (w.lower() for w in wordvoid if w)

class WordFreq(dict):
    def __init__(self, text):

        for word in _tokenize(text):
            self[word] = self.get(word, 0) + 1

    def distance(self, other):
        return sum(abs(self.get(w, 0) - other.get(w, 0)) for w in (set(self) | set(other)))

        
