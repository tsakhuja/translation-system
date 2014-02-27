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
        for token in d:
          for pos, pos_trans in d[token].iteritems():
            d[token][pos] = sorted(d[token][pos], key=lambda tup: tup[1])

    return d

  def postprocess_reorder(self, translated_sentence, source_sentence):
    for ind in xrange(0, len(source_sentence)): #removes quantifier words
      if (ind > 0 and source_sentence[ind][1][0] == 'M' and source_sentence[ind-1][1] =='CD'):
        if (ind+1 < len(source_sentence) and source_sentence[ind+1][1][0:2]!='DE'):
          source_sentence[ind] = "<delete>"
          translated_sentence[ind] = "<delete>"


    translated_sentence = filter(lambda x: x != '<delete>', translated_sentence)
    source_sentence = filter(lambda x: x != "<delete>", source_sentence)



    for ind in xrange(0, len(source_sentence)): #removes DE particles before nouns
      if (ind > 0 and source_sentence[ind][1][0] == 'N' and source_sentence[ind-1][1][0:2]=='DE'):
        source_sentence[ind-1] = "<delete>"
        translated_sentence[ind-1] = "<delete>"

    translated_sentence = filter(lambda x: x != "<delete>", translated_sentence)
    source_sentence = filter(lambda x: x != "<delete>", source_sentence)

    printsentence = ""
    for a, b in source_sentence:
      printsentence += a.decode('utf-8') + "#" + b + " "
    if self.verbose:
      print printsentence  

    return translated_sentence


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
    
  def reorder_sentence(self, source_sentence):
    tree = self.parse_sentence(source_sentence)
    if self.verbose:
      print_sentence = [' '.join(x) for x in tree.pos()] 
      # print print_sentence

    # Look for cases 1-3 of this paper: http://nlp.stanford.edu/pubs/wmt09-chang.pdf
    dnps = list(tree.subtrees(filter=lambda x: x.node=='DNP'))
    for dnp in dnps:
      if dnp[0].node == 'NP' and dnp[0][0].node == 'PN' and dnp[1].node == 'DEG':
        # Case 3 A's B
        a_index = dnp[0].treeposition()
        dnp[0][dnp[0].leaf_treeposition(0)] = "their"
        # tree[a_index].leaves()[-1] = "their"
        de_index = dnp[1].treeposition()
        del tree[de_index]
      elif dnp[0].node == 'ADJP' and dnp[1].node == 'DEG':
        # Case 1: A B - delete DE
        de_index = dnp[1].treeposition()
        del tree[de_index]

    # Look for LC>LCP reordering
    lcps = list(tree.subtrees(filter=lambda x: x.node=='LCP'))
    for lcp in lcps:
      lc = list(lcp.subtrees(filter=lambda x: x.node=='LC'))
      if lcp:
        lc = lc[0]
        if lc.left_sibling():
          # Swap order of LC and left sibling
          parent = lc.parent()
          sib = lc.left_sibling()
          lc_index = lc.treeposition()
          sib_index = sib.treeposition()
          del tree[lc_index]
          del tree[sib_index]
          parent.insert(sib_index[-1], lc)
          parent.insert(lc_index[-1], sib)


    # Look for PP:VP reordering: a PP in a parent VP should be repositioned
    # after its sibling VP.
    vps = list(tree.subtrees(filter=lambda x: x.node=='VP'))
    for vp in vps:
      if vp.left_sibling() and vp.left_sibling().node == 'PP':
        # Remove PP sibling
        parent = vp.parent()
        pp = vp.left_sibling()
        vp_index = vp.treeposition()
        pp_index = pp.treeposition()
        del tree[vp_index]
        del tree[pp_index]
        parent.insert(pp_index[-1], vp)
        parent.insert(vp_index[-1], pp)

    return tree.pos()


  def translate(self, sentence):
    """This is the function the client should call to translate a sentence"""
    # return self.direct_translate(sentence, self.dictionary)
    translated = self.translate_with_pos(sentence, self.stanford_tagger, self.dictionary)

    return translated

  def translate_with_pos(self, sentence, tagger, dictionary):
    """ 
    * Translates sentence in a POS-aware fashion.
    * sentence is a list of words or characters
    """
    sentence = self.reorder_sentence(sentence)
      
    # if tagger == self.stanford_tagger:
    #   # correct weird word#POS format
    #   correct_sentence = []
    #   for blank, wordpos in sentence:
    #     wordsplit = wordpos.split('#')
    #     correct_sentence.append((wordsplit[0], wordsplit[1]))
    #   sentence = correct_sentence
    translated_sentence = []
    for token, pos in sentence:
      # Get first char of tag since we only care about simplified tags
      if pos == 'DEC' or pos == 'DEG':
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
      elif pos == 'AS' or pos == 'DER':
      	translated_sentence.append('')
      	continue
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

    translated_sentence = self.postprocess_reorder(translated_sentence, sentence)
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



