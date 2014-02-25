import nltk
from collections import defaultdict

#TODO Implement Chinese->English direct translation system

def load_dictionary(filename):
  d = defaultdict(list)
  with open(filename) as f:
    for line in f:
       tokens = line.rstrip().split(',')
       d[tokens[0]].append(tokens[2])

  return d


def direct_translate(sentence, dictionary):
  """ 
  * sentence is a list of words or characters
  """
  translated_sentence = []
  for token in sentence:
    try:
      translated_word = dictionary[token][0]
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
      print ' '.join(direct_translate(sentence, dictionary))


if __name__ == "__main__":
    main()
