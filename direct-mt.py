#import nltk

#TODO Implement Chinese->English direct translation system

def load_dictionary(filename):
  d = {}
  with open(filename) as f:
    for line in f:
       tokens = line.split()
       d[tokens[0]] = tokens[1:]

  return d


def main():
  print load_dictionary('data/test-dict.txt')

if __name__ == "__main__":
    main()