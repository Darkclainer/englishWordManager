class Metaword(list):
    def append(self, newWord, union=False):
        if union:
            for word in self:
                if word.isSame(newWord):
                    word.augmentDefinitions(newWord)
                    return
        list.append(self, newWord)
    
    def toSON(self):
        return [word.toSON() for word in self]

    @staticmethod
    def fromSON(document):
        return Metaword( Word.fromSON(child) for child in document ) 

class Suggestions(Exception):
    def __init__(self, suggestions):
        self.suggestions = suggestions

class Word:
    def __init__(self, lettering, partOfSpeech,*, language):
        self.lettering = lettering.lower()
        self.partOfSpeech = partOfSpeech
        self.language = language
        self.transcriptions = {}
        self.definitions = []

    def addDefinition(self, definition):
        self.definitions.append(definition)

    def isSame(self, other):
        '''Return true if word is the same as other word, but without considering definitions'''
        return ( self.lettering == other.lettering and
                 self.partOfSpeech == other.partOfSpeech and
                 self.language == other.language and
                 self.transcriptions == other.transcriptions ) 
    def augmentDefinitions(self, otherWord):
        '''Append definitions of current word with definitions from other word'''
        for otherDefinition in otherWord.definitions:
            self.definitions.append(otherDefinition)

    def toSON(self):
        document = dict(
                lettering = self.lettering,
                partOfSpeech = self.partOfSpeech,
                language = self.language,
                transcriptions = dict(self.transcriptions),
                definitions = [d.toSON() for d in self.definitions]
        )
        return document

    @staticmethod
    def fromSON(document):
        word = Word(
                lettering=document['lettering'],
                partOfSpeech=document['partOfSpeech'],
                language=document['language']
        )
        word.transcriptions = dict(document['transcriptions'])
        for definitionDict in document['definitions']:
            word.addDefinition(Definition.fromSON(definitionDict))
        return word

    def __repr__(self):
        return self.lettering + ' [' + self.partOfSpeech + ']'

    def __eq__(self, other):
        if type(self) is type(other):
            return self.__dict__ == other.__dict__
        else:
            return False

class Definition:
    def __init__(self, text ='', hint=None, variant=None):
        self.text = text
        self.hint = hint
        self.examples = []
        self.variant = variant
        self.gc = set()

    @property
    def text(self):
        return self.__text

    @text.setter
    def text(self, newText):
        #downcase first letter
        newText = newText.strip()
        newText = newText[:1].lower() + newText[1:] if newText else ''
        if not newText[-1].isalnum():
            newText = newText[:-1]
        self.__text = newText

    def addExample(self, example):
        self.examples.append(example)

    def toSON(self):
        return dict(
                text = self.text,
                hint = self.hint,
                examples = list(self.examples),
                variant = self.variant,
                gc = list(self.gc)
        )

    @staticmethod
    def fromSON(document):
        definition = Definition(
                text=document['text'],
                hint=document['hint'],
                variant=document['variant']
        )
        definition.examples = list(document['examples'])
        definition.gc = set(document['gc'])
        return definition

    def __repr__(self):
        return "<Definition: '{0}' with {1} examples>".format(self.text, len(self.examples))

    def __eq__(self, other):
        if type(self) is type(other):
            return self.__dict__ == other.__dict__
        else:
            return False
