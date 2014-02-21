#import nltk

#TODO Implement Chinese->English direct translation system

def load_dictionary(filename):
  d = {}
  with open(filename) as f:
    for line in f:
       tokens = line.rstrip().split(',')
       d[tokens[0]] = tokens[1:]

  return d


def direct_translate(sentence, dictionary):
  """ 
  * sentence is a list of words or characters
  """
  translated_sentence = []
  lower_bound = 0
  length = 1
  best_match = None
  while lower_bound < len(sentence):
    try:
      print sentence[lower_bound:lower_bound + length]
      print (lower_bound,length)
      translated_word = dictionary[''.join(sentence[lower_bound:lower_bound + length])][0]
    except:
      lower_bound += 1
      length = 1
      if best_match:
        translated_sentence.append(best_match)
    else:
      best_match = translated_word
      if lower_bound == len(sentence) - 1:
        translated_sentence.append(best_match)
        break

      length += 1

  return translated_sentence



def main():
  dictionary = load_dictionary('data/test-dict.txt')
  print dictionary
  with open('data/test-corpus.txt') as f:
    for line in f:
      sentence = line.split()
      print sentence
      print ' '.join(direct_translate(sentence, dictionary))


if __name__ == "__main__":
    main()