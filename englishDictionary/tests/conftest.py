import pytest
import os
import json
import itertools
import warnings

from cambrigeDictionary import wordParser
import metaword
import configs

def pytest_assertrepr_compare(op, left, right):
    if isinstance(left, metaword.Metaword) and isinstance(right, metaword.Metaword) and op == '==':
        return metawordEqualityRepr(left, right)

def pytest_addoption(parser):
    parser.addoption('--update-metawords', action='store_true', dest='needUpdateMetawords', help='download words from dictionary and update they files')
    parser.addoption('--metaword-ids', action='store', nargs='+', dest='metawordIds', default=configs.metawordIds, help='test only specified metawords')

def updateMetawordFiles(metawordIds):
    import updateMetawordFiles
    updateMetawordFiles.updateMetawordFiles(metawordIds)

def pytest_configure(config):
    metawordIds = set(config.getoption('metawordIds'))
    if config.getoption('needUpdateMetawords'):
        updateMetawordFiles(metawordIds)

def raiseIfDoesntExist(path):
    if not os.path.exists(path):
        raise RuntimeError('Path "', path, '" doesnt exists!')

def generateTestDataFilePaths(metawordIds, htmlDir, jsonDir):
    '''Return tuple (wordName, htmlFilePath, jsonFilePath) for every html file in test dir.
    If there is not corresponding json file - 3rd component will be None'''
    tuples = []
    for metawordId in metawordIds:
        htmlFileName = metawordId + '.html'
        jsonFileName = metawordId + '.json'

        htmlPath = configs.htmlDir + htmlFileName
        jsonPath = configs.jsonDir + jsonFileName
        #if not os.path.exists(htmlPath) or not os.path.exists(jsonPath):
            #warnings.warn('Cannot generate test for metawordId: '+metawordId, RuntimeWarning)
            #continue
        tuples.append((metawordId, htmlPath, jsonPath))
    return tuples

def testFilePaths(htmlFilePath, jsonFilePath):
    noFiles = []
    if not os.path.exists(htmlFilePath):
        noFiles.append('html')
    if not os.path.exists(jsonFilePath):
        noFiles.append('json')

    if not noFiles:
        return

    reason = 'No ' + ' and '.join(noFiles) + ' file'
    return pytest.param(None, marks=pytest.mark.xfail(reason=reason))


def loadMetawordData(htmlFilePath, jsonFilePath):
    xfail = testFilePaths(htmlFilePath, jsonFilePath)
    if xfail:
        return xfail

    with open(htmlFilePath) as htmlFile, open(jsonFilePath) as jsonFile:
        htmlMetaword = wordParser.parse(htmlFile)

        jsonList = json.load(jsonFile)
        jsonMetaword = metaword.Metaword.fromSON(jsonList)
        return htmlMetaword, jsonMetaword

def pytest_generate_tests(metafunc):
    if 'metawordData' in metafunc.fixturenames:
        metawordIds = set(metafunc.config.getoption('metawordIds'))
        testData = generateTestDataFilePaths(metawordIds, configs.htmlDir, configs.jsonDir)

        metawords = []
        for metawordId, htmlPath, jsonPath in testData:
            metawords.append(loadMetawordData(htmlPath, jsonPath))

        metafunc.parametrize('metawordData', metawords, ids=[metawordId for metawordId, htmlPath, jsonPath in testData])

def compareAttributesRepr(left, right):
    symAttrDiff = set(left.__dict__) ^ set(right.__dict__)
    if not symAttrDiff:
        return []
    lines = ['There is attribute present in one object, but not in other: {0}'.format(symAttrDiff)]
    return lines

def attributeEqualityRepr(left, right, attributes):
    lines = []
    lines.extend(compareAttributesRepr(left,right))
    for attribute in attributes:
        leftValue = getattr(left, attribute)
        rightValue = getattr(right, attribute)
        if leftValue != rightValue:
            lines.append('Inequal attribute "{0}": {1} != {2}'.format(attribute, leftValue, rightValue))
    return lines

definitionAttributeCompare = [
        'text', 'hint',
        'variant', 'gc',
        'examples'
]
def definitionEqualityRepr(left, right):
    if left == right:
        return []
    lines = []
    lines.extend(attributeEqualityRepr(left, right, definitionAttributeCompare))

    return lines

wordAttributeCompare = [
        'lettering', 'partOfSpeech',
        'language', 'transcriptions'
]
def wordEqualityRepr(left, right):
    if left == right:
        return []
    lines = []
    lines.extend(attributeEqualityRepr(left, right, wordAttributeCompare))

    if len(left.definitions) != len(right.definitions):
        lines.append('Words have different number of definitions ({0} != {1})'.format(len(left.definitions), len(right.definitions)))
        return lines

    for definitionIndex, leftDefinition, rightDefinition in zip(itertools.count(1), left.definitions, right.definitions):
        if leftDefinition == rightDefinition:
            continue
        newLines = definitionEqualityRepr(leftDefinition, rightDefinition)
        lines.append('')
        lines.append('Definitions at index {0} are not equal ({1} != {2})'.format(definitionIndex, leftDefinition, rightDefinition))
        lines.extend(newLines)

    return lines

def metawordEqualityRepr(left, right):
    lines = ["Metawords are not equal! See:", '']

    if len(left) != len(right):
        lines.append('Number words in metawords differ: {0} != {1}'.format(len(left), len(right)))
        return lines

    for wordIndex, leftWord, rightWord in zip(itertools.count(1), left, right):
        if leftWord == rightWord:
            continue
        newLines = wordEqualityRepr(leftWord, rightWord)
        lines.append('Words at index {0} ({1} and {2}) are not equal:'.format(wordIndex, leftWord, rightWord))
        lines.extend(newLines)
        lines.extend([''] * 3)


    return lines
