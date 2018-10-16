import sys
import os
import cambrigeDictionary
import json

import configs

def updateJsonFile(metawordId):
    try:
        jsonFileName = configs.jsonFileName(metawordId)
        if os.path.isfile(jsonFileName):
            raise RuntimeError('There is json file already.')

        with open(configs.htmlFileName(metawordId)) as htmlFile, open(jsonFileName, 'w') as jsonFile: 
            metaword = cambrigeDictionary.wordParser.parse(htmlFile)
            json.dump(metaword.toSON(), jsonFile, indent=4, ensure_ascii=False)
            print('Json file "{0}" updated.'.format(jsonFileName))

    except Exception as e:
        print('With metawordId "{0}" exception raised: {1}'.format(metawordId, e))

if __name__ == '__main__':
    metawordIds = sys.argv[1:]
    for metawordId in metawordIds:
        updateJsonFile(metawordId)

