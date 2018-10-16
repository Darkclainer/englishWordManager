import requests
import os

import configs
import updateJsonFiles

def getHtmlMetaword(metawordId):
    url = 'https://dictionary.cambridge.org/dictionary/english/' + metawordId
    page = requests.get(url, headers=configs.headers)
    return page.text

def updateHtmlFile(metawordId):
        with open(configs.htmlFileName(metawordId), 'w') as htmlFile:
            htmlContents = getHtmlMetaword(metawordId)
            htmlFile.write(htmlContents)
            print('Metaword updated:', metawordId)

def updateMetawordFiles(metawordIds):
    for metawordId in metawordIds:
        updateHtmlFile(metawordId)
        if not os.path.isfile(configs.jsonFileName(metawordId)):
            updateJsonFiles.updateJsonFile(metawordId)

if __name__ == '__main__':
    updateMetawordFiles()
