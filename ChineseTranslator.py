import nltk
from nltk.corpus import sinica_treebank
from collections import defaultdict
from nltk.tag.stanford import POSTagger
import pickle

#TODO Implement Chinese->English direct translation system
class ChineseTranslator:
  """Translates english to chinese"""

  def __init__(self):
    self.dictionary = self.load_dictionary('data/zhen-dict.csv')
    self.pos_tagger = self.trained_pos_tagger();
    self.stanford_tagger = POSTagger('chinese-distsim.tagger', 'stanford-postagger.jar') 

  def trained_pos_tagger(self):
    return pickle.load(open("sinica_treebank_brill_aubt.pickle"))


  def tag_pos(self, sentence):
    return self.pos_tagger.tag(sentence)

  def load_dictionary(self, filename):
    d = defaultdict(lambda: defaultdict(list))
    with open(filename) as f:
      for line in f:
        tokens = line.rstrip().split(',')
        pos = tokens[1]
        if pos == 'noun':
          pos = 'N'
        elif pos == 'verb':
          pos = 'V'
        elif pos == 'adjective':
          pos = 'A'
        elif pos == 'preposition':
          pos = 'P'
        elif pos == 'adverb':
          pos = 'D'
        elif pos == 'conjunction':
          pos = 'T'
        elif pos == 'pronoun':
          pos = 'N'
        elif pos == 'auxiliary verb':
          pos = 'V'
        d[tokens[0]][pos].append(tokens[2])

    return d

  def translate(self, sentence):
    """This is the function the client should call to translate a sentence"""
    # return self.direct_translate(sentence, self.dictionary)
    return self.translate_with_pos(sentence, self.pos_tagger, self.dictionary)

  def translate_with_pos(self, sentence, tagger, dictionary):
    """ 
    * Translates sentence in a POS-aware fashion.
    * sentence is a list of words or characters
    """
    sentence = tagger.tag(sentence)
    if tagger == self.stanford_tagger:
      # correct weird word#POS format
      correct_sentence = []
      for blank, wordpos in sentence:
        wordsplit = wordpos.split('#')
        correct_sentence.append((wordsplit[0], wordsplit[1]))
      sentence = correct_sentence
    # print sentence
    translated_sentence = []
    for token, pos in sentence:
      # Get first char of tag since we only care about simplified tags
      if pos[0:2] == 'DE':
        # Ignore decorators for now
        pos = -1
      else: 
        pos = pos[0]
      if dictionary[token].has_key(pos):
        translated_word = dictionary[token][pos][0]
      else:
        # Fall back on any translation of word, even if not correct POS
        try:
          translated_word = dictionary[token].values()[0][0]
        except:
          translated_word = token
      translated_sentence.append(translated_word)

    return translated_sentence

  def direct_translate(self, sentence, dictionary):
    """ 
    * Translates sentence in a completely direct fashion.
    * sentence is a list of words or characters
    """
    translated_sentence = []
    for token in sentence:
      try:
        translated_word = dictionary[token].values()[0][0]
      except:
        translated_word = token
      translated_sentence.append(translated_word)

    return translated_sentence



