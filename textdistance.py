"""This module define WordFreq. WordFreq helps to measure distance between two texts."""

def _tokenize(text):
    """Return tokens from text.

    Text are splitted by tokens with space as seperator.
    All non alpha character discarded.
    All tokens are casefolded.
    """

    # split text by spaces and add only alpha character
    wordvoid = (''.join(ch for ch in w if ch.isalpha()) for w in text.split(' '))
    # discard empty element and lower others
    return (w.casefold() for w in wordvoid if w)

class WordFreq(dict):
    """This class help relatively fast determine distance between to texts.

    Use WordFreq(text1).distance(WordFreq(text2))."""

    def __init__(self, text):
        dict.__init__(self)

        for word in _tokenize(text):
            self[word] = self.get(word, 0) + 1

    def distance(self, other):
        """Distance between two text is sum of module substractions of corresponding token freqs."""
        return sum(abs(self.get(w, 0) - other.get(w, 0)) for w in set(self) | set(other))
