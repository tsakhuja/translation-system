from ChineseTranslator import ChineseTranslator
import sys

def main():
  verbose = False
  if len(sys.argv) > 1 and sys.argv[1] == '-v':
    verbose = True

  translator = ChineseTranslator()
  with open('data/test-set.txt') as f:
    for line in f:
      sentence = line.split()
      if verbose:
        print ' '.join(sentence)
      print ' '.join(translator.translate(sentence))


if __name__ == "__main__":
    main()