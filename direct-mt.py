import nltk
from nltk.corpus import sinica_treebank
from collections import defaultdict
import pickle

#TODO Implement Chinese->English direct translation system

def trained_pos_tagger():
  return trained_pos_tagger.tagger = pickle.load(open("sinica_treebank_brill_aubt.pickle"))

trained_pos_tagger.tagger = None

def tag_pos(sentence):
  pos_tagger = trained_pos_tagger()
  return pos_tagger.tag(sentence)

def load_dictionary(filename):
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



def direct_translate(sentence, dictionary):
  """ 
  * sentence is a list of words or characters
  """
  translated_sentence = []
  for token, pos in sentence:
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



def main():
  dictionary = load_dictionary('data/zhen-dict.csv')
  with open('data/dev-set.txt') as f:
    for line in f:
      sentence = line.split()
      print ' '.join(sentence)
      print ' '.join(direct_translate(tag_pos(sentence), dictionary))


if __name__ == "__main__":
    main()
