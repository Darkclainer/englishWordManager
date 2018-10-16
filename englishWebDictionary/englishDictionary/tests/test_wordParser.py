import os
import pytest 
import json

from cambrigeDictionary import wordParser
import metaword
import configs

def test_metaword(metawordData):
    htmlMetaword, jsonMetaword = metawordData
    assert htmlMetaword == jsonMetaword

