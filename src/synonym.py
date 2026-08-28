import requests
from os.path import isfile
from data_paths import synonyms_file
import json


def _extract_terms(resp):
    definitions = resp.get('definitionData', {}).get('definitions', [])
    return [synonym['term'] for defn in definitions for synonym in defn.get('synonyms', [])]


def in_local(word):
    word = word.replace(' ', '-').lower()
    file = synonyms_file(f'{word}.json')
    if isfile(file) is True:
        with open(file, 'r') as f:
            return json.load(f), True
    return {}, False


def save_to_local(word, dict_):
    file = synonyms_file(f'{word}.json')
    with open(file, 'w+') as f:
        json.dump(dict_, f)


def save_empty_to_local(word):
    save_to_local(word, {'definitionData': {'definitions': []}})


def synonym(word):
    resp = ""
    if (resp := in_local(word))[1] == True:
        resp = resp[0]
    else:
        try:
            resp = requests.get(
                f'https://tuna.thesaurus.com/pageData/'
                f'{word.replace(" ", "-").lower()}',
                timeout=5).json().get('data', {})
        except requests.RequestException:
            save_empty_to_local(word)
            return []

        if resp is None:
            save_empty_to_local(word)
            return []

        save_to_local(word, resp)

    return _extract_terms(resp)
