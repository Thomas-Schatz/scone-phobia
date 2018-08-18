# -*- coding: utf-8 -*-
"""
Created on Wed Jun 27 12:18:50 2018

@author: Thomas Schatz

Useful info about corpora of speech recordings.

Currently there are four functions:
    - two which take the corpus name as input and respectively return the:
        - language
        - register
    - two which take a language as input and return the:
        - list of consonants (in ASCII code or ipa, depending on
            'ipa' optional arg)
        - list of vowels  (in ASCII code or ipa, depending on
            'ipa' optional arg).

This assumes that the ASCII code for all corpora sharing a same langague
is consistent. 

To add new corpora just extend these functions appropriately.

We might want to get the info directly from spock-formatted files at some point.
"""

def language(corpus):
    if corpus == 'None':
        lang = 'None'
    elif corpus in ['GPJ', 'CSJ']:
        lang = 'Japanese'
    elif corpus in ['WSJ', 'BUC']:
        lang = 'American English'
    else:
        print("Unknown corpus {}".format(corpus))
        lang = 'Unknown'
    return lang


def register(corpus):
    if corpus == 'None':
        reg = 'None'
    elif corpus in ['GPJ', 'WSJ']:
        reg = 'Read'
    elif corpus in ['CSJ', 'BUC']:
        reg = 'Spontaneous'
    else:
        print("Unknown corpus {}".format(corpus))
        reg = 'Unknown'
    return reg


ipa_jap = {'F': 'ɸ',
           'N': 'ɴ',
           'Q+c': 't͡s:',
           'Q+c+y': 't͡ɕ:',
           'Q+k': 'k:',
           'Q+p': 'p:',
           'Q+s': 's:',
           'Q+s+y': 'ɕ:',
           'Q+t': 't:',
           'b': 'b',
           'c': 't͡s',
           'c+y': 't͡ɕ',
           'd': 'd',
           'g': 'g',
           'h': 'h',
           'k': 'k',
           'm': 'm',
           'n': 'n',
           'p': 'p',
           'r': 'r',
           's': 's',
           's+y': 'ɕ',
           't': 't',
           'w': 'w',
           'y': 'j',
           'z': 'z',
           'z+y': 'ʑ',
           'a': 'ä',
           'a+H': 'ä:',
           'e': 'e',
           'e+H': 'e:',
           'i': 'i',
           'i+H': 'i:',
           'o': 'o',
           'o+H': 'o:',
           'u': 'ɯ',
           'u+H': 'ɯ:'}
           

ipa_eng = {'B': 'b',
           'CH': 'ʧ',
           'D': 'd',
           'DH': 'ð',
           'F': 'f',
           'G': 'g',
           'HH': 'h',
           'JH': 'ʤ',
           'K': 'k',
           'L': 'l',
           'M': 'm',
           'N': 'n',
           'NG': 'ŋ',
           'P': 'p',
           'R': 'ɹ',
           'S': 's',
           'SH': 'ʃ',
           'T': 't',
           'TH': 'θ',
           'V': 'v',
           'W': 'w',
           'Y': 'j',
           'Z': 'z',
           'ZH': 'ʒ',
           'AA': 'ɑː',
           'AE': 'æ',
           'AH': 'ʌ',
           'AO': 'ɔː',
           'AW': 'aʊ',
           'AY': 'aɪ',
           'EH': 'ɛ',
           'ER': 'ɝ',
           'EY': 'eɪ',
           'IH': 'ɪ',
           'IY': 'iː',
           'OW': 'oʊ',
           'OY': 'ɔɪ',
           'UH': 'ʊ',
           'UW': 'uː'}

ipas = {'American English': ipa_eng, 'Japanese': ipa_jap}


def consonants(lang, ipa=False):
    if lang == 'American English':
        C = ['B', 'CH', 'D', 'DH', 'F', 'G', 'HH', 'JH', 'K', 'L', 'M', 'N',
            'NG', 'P', 'R', 'S', 'SH', 'T', 'TH', 'V', 'W', 'Y', 'Z', 'ZH']
    elif lang == 'Japanese':
        C = ['z+y', 's+y', 'Q+k', 'N', 'w', 'g', 'd', 'k', 't', 'r', 'p', 'b',
             'y', 'Q+p', 'm', 'n', 'c+y', 'Q+t', 'z', 'Q+s+y', 'Q+c+y', 's',
             'Q+s', 'h', 'c', 'Q+c', 'F']
    else:
        raise "Unsupported language {}".format(lang)
    if ipa:
        C = [ipas[lang][e] for e in C]
    return C


def vowels(lang, ipa=False):
    if lang == 'American English':
        V = ['UW', 'OY', 'IY', 'AY', 'ER', 'AO', 'OW', 'AA', 'IH', 'AH', 'AW',
             'AE', 'EY', 'EH', 'UH']
    elif lang == 'Japanese':
        V = ['i+H', 'o+H', 'e', 'u+H', 'a', 'a+H', 'i', 'o', 'u', 'e+H']
    else:
        raise "Unsupported corpus {}".format(lang)
    if ipa:
        V = [ipas[lang][e] for e in V]
    return V