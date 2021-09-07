#!/usr/bin/env python

from pprint import pprint
import json

from data_helper import load_csv, load_json, save_json, load, as_json

def test_load_json():
    colors = load_json('colors.json')
    pprint(json.dumps(colors))
    assert len(colors) > 0


def test_load_csv():
    giftcards = load_csv('giftcards.csv', 'giftCardId')
    pprint(json.dumps(giftcards))
    save_json(giftcards, 'giftcards.json')
    

def test_load():
    colors = load('colors.json')
    pprint(colors)
    colors = load('colors.json', 'color')
    pprint(colors)
    
def test_as_json():
    item = load('vouchers.json')
    json = as_json(item)
    pprint(json)