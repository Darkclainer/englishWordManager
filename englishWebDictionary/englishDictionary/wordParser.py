'''Get word data from cambrige word html page

TODO:
    Not work with phrasal verb like 'work off', 'work out'
'''
from bs4 import BeautifulSoup, SoupStrainer, Tag
import re

from .metaword import Word, Definition, Metaword
from . import ipaSupport

class UnknownIpa(Exception): pass
class CannotParsePage(Exception): pass

def parse(htmlText, parser = 'html.parser'):
    onlyEntryContent = SoupStrainer(id='entryContent')
    soup = BeautifulSoup(htmlText, parser, parse_only=onlyEntryContent)

    content = soup.find(id='entryContent')
    wordDataSets = _getWordDataSets(content) # different wordDataSet for each language

    metaword = Metaword()
    for dataSet in wordDataSets:
        _addWordsFromDataSet(dataSet, metaword)

    if len(metaword) == 0:
        raise CannotParsePage('Seems that information has not been retreived')
    return metaword

def _prettifyString(s):
    s = s.replace('\n', '')
    s = re.sub('\s\s+', ' ', s)
    return s.strip()

def _getWordDataSets(content):
    'Extract tags that content various definitions of words in various languages'
    page = content.find(class_='page')
    return page.findAll(class_='dictionary', recursive=False)

dataIdToLanguage = {
        'cald4': 'british',
        'cacd': 'american-english',
        'cbed': 'business-english'
}
def _getLanguageFromDataSet(wordDataSet):
    if wordDataSet.has_attr('data-wrodlist-dataset'):
        return wordDataSet['data-wordlist-dataset']
    elif wordDataSet.has_attr('data-id'):
        dataId = wordDataSet['data-id']
        try:
            return dataIdToLanguage[dataId]
        except Exception:
            raise CannotParsePage('Unkown data-id: ' + dataId)
    else:
        raise CannotParsePage('Unkown language')


def _addWordsFromDataSet(wordDataSet, metaword):
    language = _getLanguageFromDataSet(wordDataSet)

    entryBodies = wordDataSet.findAll(class_='entry-body')
    for entryBody in entryBodies:
        _addWordsFromEntryBody(entryBody, language, metaword)

    return metaword


def _addWordsFromEntryBody(entryBody, language, metaword):
    # find all wordTags - big frame with transcription and other. Distinguished by part of speech may be
    entryBody_els = entryBody.findAll('div', recursive=False) # often as class_="entry-body__el"
    for entryBody_el in entryBody_els:
        # this div has phrasal verbs and doesn't have general words
        relativDiv = entryBody_el.find(class_='relativDiv', recursive=False)
        if relativDiv:
            newWord = _extractWordFromRelativDiv(relativDiv, language)
        else:
            newWord = _extractWord(entryBody_el, language)
        metaword.append(newWord, union=True)


def _extractWord(wordTag, language):
    header = wordTag.find(class_='pos-header', recursive=False)
    word = _makeWordFromHeader(header, language)

    body = wordTag.find(class_='pos-body', recursive=False)
    senseBlocks = body.findAll(class_='sense-block')
    for senseBlock in senseBlocks:
        _addDefinitionsFromSenseBlock(word, senseBlock)

    return word

def _getPartOfSpeachFromHeadWord(headWord):
    #Part Of Speach
    posgram = headWord.find_next_sibling(class_='posgram')
    if not posgram:
        return 'unknown'
    else:
        return posgram.span.string

def _makeWordFromHeader(headerTag, language):
    headWordTag = headerTag.find(class_='headword')
    lettering = str(headWordTag.string)
    partOfSpeach = _getPartOfSpeachFromHeadWord(headWordTag)

    word = Word(lettering, partOfSpeach, language=language)
    _addTranscriptionsFromHeader(headerTag, word)
    return word

def _addTranscriptionsFromHeader(headerTag, word):
    transcriptionTags = headerTag.findAll(class_='pron-info', recursive=False)
    for transcriptionTag in transcriptionTags:
        _addTranscriptionFromTag(transcriptionTag, word)

def ipaTagParser(ipaTag):
    parts = []
    for child in ipaTag.children:
        if isinstance(child, Tag):
            if child.has_attr('class') and 'sp' in child['class']:
                parts.append(ipaSupport.toSuperscript(child.text))
            else:
                raise UnknownIpa(child['class'])
        else:
            parts.append(str(child))
    return ''.join(parts)


def _addTranscriptionFromTag(transcriptionTag, word):
    regionTag = transcriptionTag.find('span', class_='region')
    ipaTag = transcriptionTag.find('span', class_='ipa')
    if not regionTag or not ipaTag:
        return
    region = str(regionTag.string).lower()
    ipa = ipaTagParser(ipaTag)
    word.transcriptions[region] = ipa

def _extractHintFromSenseBlock(senseBlock):
    txtBlock = senseBlock.find(class_='txt-block', recursive=False)
    if not txtBlock:
        return None

    guideWord = txtBlock.find(class_='guideword', recursive=False)
    if not guideWord:
        return None

    guideStr = guideWord.getText()
    hint = ''.join(char.lower() for char in guideStr if char.isalpha() or char.isspace())
    return hint.strip()


def _addDefinitionsFromSenseBlock(word, senseBlock):
    hint = _extractHintFromSenseBlock(senseBlock)

    senseBodies = senseBlock.findAll(class_='sense-body')
    for senseBody in senseBodies:
        _addDefinitionsFromSenseBody(word, senseBody, hint)


def _addDefinitionsFromSenseBody(word, senseBody, hint):
    for child in senseBody.findAll('div', recursive=False):
        if 'def-block' in child['class']:
            definition = _getDefinitionFromDefBlock(child)
        elif 'phrase-block' in child['class']:
            definition = _getDefinitionFromPhraseBlock(child)
        else:
            definition = None

        if definition:
            definition.hint = hint
            word.addDefinition(definition)

def _getDefinitionFromDefBlock(defBlock):
    defHead = defBlock.find(class_='def-head', recursive=False)
    definition = _getDefinitionFromDefHead(defHead)

    defBody = defBlock.find(class_='def-body', recursive=False)
    if defBody:
        _addDefinitionExamples(definition, defBody)

    return definition

def _getDefinitionFromDefHead(defHead):
    defText = _prettifyString(defHead.find(class_='def', recursive=False).getText())
    definition = Definition(defText)
    
    defInfo = defHead.find(class_='def-info', recursive=False)
    if defInfo:
        _addDefinitionGCs(definition, defInfo)
        _addDefinitionVariant(definition, defInfo)

    return definition

def _addDefinitionGCs(definition, defInfo):
    gcs = defInfo.find('span', class_='gcs')
    if not gcs:
        return
    for gc in gcs.findAll(class_='gc'):
        definition.gc.add(str(gc.string))

def _addDefinitionVariant(definition, defInfo):
    vTag = defInfo.find(class_='v')
    if not vTag:
        return
    definition.variant = str(vTag.string)


def _addDefinitionExamples(definition, defBody):
    for exampTag in defBody.findAll(class_='examp', recursive=False):
        definition.addExample(_prettifyString(exampTag.getText()))

def _getDefinitionFromPhraseBody(phraseBody):
    defBlock = phraseBody.find(class_='def-block', recursive=False)
    if not defBlock:
        return Definition()
    else:
        return _getDefinitionFromDefBlock(defBlock)

def _getDefinitionFromPhraseBlock(phraseBlock):
    phraseBody = phraseBlock.find(class_='phrase-body', recursive=False)
    definition = _getDefinitionFromPhraseBody(phraseBody)

    phraseHead = phraseBlock.find(class_='phrase-head', recursive=False)
    phraseTag = phraseHead.find(class_='phrase')
    if phraseTag:
        definition.variant = phraseTag.getText()

    return definition

def _extractPartOfSpechFromPosHeader(posHeader):
    ancInfoHead = posHeader.find(class_='anc-info-head', recursive=False)
    partOfSpeachTag = ancInfoHead.find(class_='pos')
    return partOfSpeachTag.getText().lower()

def _makeWordFromIdiomBlock(idiomBlock, language):
    diTitle = idiomBlock.find(class_='di-title', recursive=False)
    headWord = diTitle.find(class_='headword', recursive=False)
    lettering = headWord.getText().strip()

    return  Word(lettering, 'idiom', language=language)

def _extractWordFromIdiomBlock(idiomBlock, language):
    word = _makeWordFromIdiomBlock(idiomBlock, language)

    idiomBody = idiomBlock.find(class_='idiom-body', recursive=False)
    senseBlocks = idiomBody.findAll(class_='sense-block', recursive=False)
    for senseBlock in senseBlocks:
        _addDefinitionsFromSenseBlock(word, senseBlock)

    return word

def _extractWordFromRelativDiv(relativDiv, language):
    tag = relativDiv.find(class_='pv-block', recursive=False)
    if tag:
        return _extractWordFromPVBlock(tag, language)

    tag = relativDiv.find(class_='idiom-block', recursive=False)
    if tag:
        return _extractWordFromIdiomBlock(tag, language)

    raise RuntimeError('Can not extract word! Unknow block type!')

def _makeWordFromPVBlock(pvBlock, language):
    title = pvBlock.find(class_='di-title', recursive=False)
    lettering = title.getText().strip().lower()

    diInfo = pvBlock.find(class_='di-info', recursive=False)
    posHeader = diInfo.find(class_='pos-header', recursive=False)
    partOfSpeach = _extractPartOfSpechFromPosHeader(posHeader)

    word = Word(lettering, partOfSpeach, language=language)
    _addTranscriptionsFromHeader(posHeader, word)
    
    return word


def _extractWordFromPVBlock(pvBlock, language):
    word = _makeWordFromPVBlock(pvBlock, language)

    pvBody = pvBlock.find(class_='pv-body', recursive=False)
    senseBlocks = pvBody.findAll(class_='sense-block')
    for senseBlock in senseBlocks:
        _addDefinitionsFromSenseBlock(word, senseBlock)

    return word

__all__ = ['parse']
