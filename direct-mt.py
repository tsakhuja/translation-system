import nltk
from nltk.corpus import sinica_treebank
from collections import defaultdict
import pickle

#TODO Implement Chinese->English direct translation system

def trained_pos_tagger():
  try:
    with open('markov_sinica.pickle', 'r') as fd:
      trained_pos_tagger.tagger = pickle.load(fd)
  except:
    if not trained_pos_tagger.tagger:
      sents = sinica_treebank.tagged_sents(simplify_tags=True)
      training = []
      test = []
      for i in range(len(sents)):
        if i % 10:
          training.append(sents[i])
        else:
          test.append(sents[i])
      trained_pos_tagger.tagger = nltk.HiddenMarkovModelTagger.train(training)
      print '%.1f %%' % (trained_pos_tagger.tagger.evaluate(test) * 100)
      # Dump trained tagger
      # with open('markov_sinica.pickle', 'w') as fd:
      #   pickle.dump(trained_pos_tagger.tagger, fd)

  return trained_pos_tagger.tagger

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
