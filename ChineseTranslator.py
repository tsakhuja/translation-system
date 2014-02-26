import nltk
import os
import subprocess
from nltk.corpus import sinica_treebank
from collections import defaultdict
from nltk.tag.stanford import POSTagger
import pickle

#TODO Implement Chinese->English direct translation system
class ChineseTranslator:
  """Translates english to chinese"""

  def __init__(self, verbose):
    self.verbose = verbose
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
          pos = 'VA'
        elif pos == 'preposition':
          pos = 'P'
        elif pos == 'adverb':
          pos = 'AD'
        elif pos == 'conjunction':
          pos = 'CC'
        elif pos == 'pronoun':
          pos = 'N'
        elif pos == 'auxiliary verb':
          pos = 'V'
        elif pos == 'particle':
          pos = 'DE'
        d[tokens[0]][pos].append((tokens[2],int(tokens[3]),int(tokens[4])))

    return d


  def parse_sentence(self, sentence):
    sentence = ' '.join(sentence)
    try:
      f = open('stanfordtemp.txt.' + str(hash(sentence)) + ".40" + ".stp", "r")
    except:
      os.popen("echo '" + sentence + "' > stanfordtemp.txt")
      subprocess.call("./stanford-parser-full/lexparser-lang.sh Chinese 40 stanford-parser-full/edu/stanford/nlp/models/lexparser/chinesePCFG.ser.gz " + str(hash(sentence)) + " stanfordtemp.txt", shell=True)
      f = open('stanfordtemp.txt.' + str(hash(sentence))+ ".40" + ".stp", "r")

    tree = nltk.tree.ParentedTree.parse(f.read().translate(None, '\n'))
    f.close()
    # tree.draw()

    return tree
    
  def reorder_sentence(self, source_sentence, translated_sentence):
    tree = self.parse_sentence(source_sentence)
    

    # Look for cases 1-3 of this paper: http://nlp.stanford.edu/pubs/wmt09-chang.pdf
    dnps = list(tree.subtrees(filter=lambda x: x.node=='DNP'))
    for dnp in dnps:
      if dnp[0].node == 'NP' and dnp[0][0].node == 'PN' and dnp[1].node == 'DEG':
        # Case 3 A's B
        #TODO: oneself's should be his/her/their
        a_index = tree.leaves().index(dnp[0].leaves()[-1])
        translated_sentence[a_index] += "'s"
        translated_sentence[a_index + 1] = '<delete>'
      elif dnp[0].node == 'ADJP' and dnp[1].node == 'DEG':
        # Case 1: A B
        a_index = tree.leaves().index(dnp[0].leaves()[-1])
        translated_sentence[a_index + 1] = '<delete>'
      elif dnp[0].node == 'QP' and dnp[1].node == 'DEG':
        # Case 2: A preposition B
        pass
    # Look for case 4
    cps = list(tree.subtrees(filter=lambda x: x.node=='CP'))
    for cp in cps:
      last_vp = list(cp.subtrees(filter=lambda x: x.node == 'VP'))[-1]
      if cp[0].node == 'IP' and cp[-1].node == 'DEC' and len(list(last_vp.subtrees(filter=lambda x: x.node=='VA' or x.node=='VP'))) > 1:
        # Case 4: relative clause: seems we should switch the order of A and B and
        # TODO insert some words to make construction sound more like proper english.
        # b_indices = [tree.leaves().index(x) for x in cp.right_sibling().leaves()]
        # de_index = b_indices[0] - 1
        # a_index = tree.leaves().index(cp[0].leaves()[0])
        # translated_sentence[de_index] = '<delete>'
        # for b_index in b_indices:
        #   translated_sentence.insert(a_index, translated_sentence[b_index])
        #   del(translated_sentence[b_index + 1])
        #   a_index += 1
        pass

    # Look for PP:VP reordering: a PP in a parent VP should be repositioned
    # after its sibling VP.
    vps = list(tree.subtrees(filter=lambda x: x.node=='VP'))
    for vp in vps:
      if vp.left_sibling() and vp.left_sibling().node == 'PP':
        vp_indices = [tree.leaves().index(x) for x in vp.leaves()]
        pp_start_index = tree.leaves().index(vp.left_sibling().leaves()[0])
        print "pp reordering"
        for vp_index in vp_indices:
          translated_sentence.insert(pp_start_index, translated_sentence[vp_index])
          del(translated_sentence[vp_index + 1])
          pp_start_index += 1
        # reposition PP before sibling PP
    return filter(lambda x: x != '<delete>', translated_sentence)


    # for node in tree:
    #   if node

  def translate(self, sentence):
    """This is the function the client should call to translate a sentence"""
    # return self.direct_translate(sentence, self.dictionary)
    translated = self.translate_with_pos(sentence, self.stanford_tagger, self.dictionary)
    return self.reorder_sentence(sentence, translated)

  def translate_with_pos(self, sentence, tagger, dictionary):
    """ 
    * Translates sentence in a POS-aware fashion.
    * sentence is a list of words or characters
    """
    sentence = tagger.tag(sentence)
    if self.verbose:
      print_sentence = [' '.join(x) for x in sentence]
      
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
        # Special case for decorator tags
        pos = 'DE'
      elif pos == 'VA':
        pos = 'VA'
      elif pos == 'AD':
        # special case for adverb
        pos = 'AD'
      elif pos == 'PN':
        # special case for pronoun
        pos = 'N'
      elif pos == 'CC' or pos == 'CS':
        # special case for conjunction
        pos = 'CC'
      else: 
        pos = pos[0]
      if dictionary[token].has_key(pos):
        translated_word = dictionary[token][pos][0][0]
      else:
        # Fall back on any translation of word, even if not correct POS
        try:
          #translated_word = dictionary[token].values()[0][0]
          candidate_list = []
          for part_of_speech, translations in dictionary[token].iteritems():
            candidate_list.append(translations[0])
          candidate_list = sorted(candidate_list, key=lambda rank: rank[2])
          translated_word = candidate_list[0][0]
        except:
          translated_word = token
      translated_sentence.append(translated_word)

    return translated_sentence

  def direct_translate(self, sentence, dictionary):
    translated_sentence = []
    for token in sentence:
      try:
        translated_word = dictionary[token].values()[0][0][0]
      except:
        translated_word = token
      translated_sentence.append(translated_word)

    return translated_sentence

  def direct_freq_translate(self, sentence, dictionary):
    """ 
    * Translates sentence in a completely direct fashion.
    * sentence is a list of words or characters
    """
    translated_sentence = []
    for token in sentence:
      try:
        #translated_word = dictionary[token].values()[0][0]
        candidate_list = []
        for part_of_speech, trans in dictionary[token].iteritems():
          candidate_list.append(trans[0])
        candidate_list = sorted(candidate_list, key=lambda rank: rank[2])
        translated_word = candidate_list[0][0]
      except:
        translated_word = token
      translated_sentence.append(translated_word)

    return translated_sentence



