import sys
import getopt
import os
import re
import math
import xml.etree.ElementTree as ET
import string
import nltk
from nltk.stem.porter import *
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from gensim import corpora, models, similarities

stop_list = stopwords.words('english')
stemmer = PorterStemmer()

# This function builds dictionary and postings list using third party library gensim.
# Pre-condition : patsnap corpus
# Post-condition: return dictionary.txt and postings.txt in gensim objects (Dictionary object and a matrix respectively)
def build_gensim_index(directory_doc, dict_file, postings_file):
	
	patsnap_bow = []
	temp_bow = []
	title_tokens = []
	abstract_tokens = []

	for filename in os.listdir(directory_doc):
		f = os.path.join(directory_doc, filename)
		tree = ET.parse(f) # parse XML file into a tree
		root = tree.getroot()
		for child in root:
			temp_bow = []
			
			if child.attrib['name'] == 'Title':
				title = child.text.strip().lower()
				title_tokens = tokenize(title)
				title_tokens = [stemmer.stem(token) for token in title_tokens if token not in stop_list]

			if child.attrib['name'] == 'Abstract':
				abstract = child.text.strip().lower()
				abstract_tokens = tokenize(abstract)
				abstract_tokens = [stemmer.stem(token) for token in abstract_tokens if token not in stop_list]
			
			temp_bow = title_tokens + abstract_tokens

		patsnap_bow.append(temp_bow)

	dictionary = corpora.Dictionary(patsnap_bow)
	dictionary.save(dict_file)  # write to dict_file

	corpus = [dictionary.doc2bow(doc) for doc in patsnap_bow]   # Coverts to dictionary to bag of words model
	corpora.MmCorpus.serialize(postings_file, corpus) # Write to postings_file

# This function creates a list of all the filenames in the patsnap corpus for search.py to use
def build_patsnap_filename_list(directory_doc):

	f = open('filenames.txt', 'w')

	for filename in os.listdir(directory_doc):
		filename = filename.replace('.xml', '')
		f.write(filename + '\n')

# This function creates dictionary, postings list and ipc subclasses using our customized format
# E.g. word.title doc_freq <-- this is in dictionary.txt
# E.g. (filename, term_freq) (filename, term_freq) <-- this is in postings.txt
# Each line from both txt files corresponds to each other.
# For ipc subclass, the format is: <<patent-filename ipc-subclass>>
# Pre-condition : Patsnap corpus
# Post-condition: return dictionary.txt, postings.txt in the above format and ipc_subclass.txt
def build_index(directory_doc, dict_file, postings_file):

	dictionary_title = {}
	dictionary_abstract = {}

	ipc_subclass_file = open('ipc_subclass.txt', 'w')

	for filename in os.listdir(directory_doc):
		f = os.path.join(directory_doc, filename)
		tree = ET.parse(f)
		root = tree.getroot()
		for child in root:

			if child.attrib['name'] == 'Title':
				title = child.text.strip().lower()
				dictionary_title.update(index_title(filename, title, dictionary_title))

			if child.attrib['name'] == 'Abstract':
				abstract = child.text.strip().lower()
				dictionary_abstract.update(index_abstract(filename, abstract, dictionary_abstract))

			if child.attrib['name'] == 'IPC Subclass':
				ipc_sc = nltk.word_tokenize(child.text)
				ipc_sc = str(ipc_sc)
				ipc_sc = re.sub(r'(\')|(\[)|(\])', "", ipc_sc)
				filename = filename.replace('.xml', '')
				ipc_subclass_file.write(filename + ' ' + ipc_sc + '\n')

		print filename

	p = open(postings_file, 'w')
	d = open(dict_file, 'w')

	for word in dictionary_title:
		try:
			doc_freq = len(dictionary_title[word])
			d.write(word + '.title ' + str(doc_freq) + ' \n')
		except UnicodeEncodeError:
			continue
		for filename in dictionary_title[word]:
			term_freq = dictionary_title[word][filename]
			p.write(filename + ',' + str(term_freq) + ' ')
		p.write('\n')
	print 'titles written'

	for word in dictionary_abstract:
		try:
			doc_freq = len(dictionary_abstract[word])
			d.write(word + '.abstract ' + str(doc_freq) + ' \n')
		except UnicodeEncodeError:
			continue
		for filename in dictionary_abstract[word]:
			term_freq = dictionary_abstract[word][filename]
			p.write(filename + ',' + str(term_freq) + ' ')
		p.write('\n')
	print 'abstracts written'

# This function does the indexing for title tag in the patsnap xml file
# Pre-condition : The current filename, string of words from title tag and a dictionary for titles
# Post-condition: return updated dictionary of titles (key1: term, key2: corresponding filename, value: term frequency)
#				  									       **term should be stemmed and not in the stopword list**
def index_title(filename, title, dictionary_title):

	filename = filename.replace('.xml', '')

	tokens = tokenize(title)
	tokens = [stemmer.stem(token) for token in tokens if token not in stop_list]
	for token in tokens:
		if token in dictionary_title and filename in dictionary_title[token]:
			dictionary_title[token][filename] += 1
		elif token in dictionary_title and not filename in dictionary_title[token]:
			dictionary_title[token][filename] = 1
		else:
			dictionary_title[token] = {}
			dictionary_title[token][filename] = 1

	return dictionary_title

# This function does the indexing for abstract tag in the patsnap xml file and is similar to index_title()
# Pre-condition : The current filename, string of words from abstract tag and a dictionary for abstract
# Post-condition: return updated dictionary of titles (key1: term, key2: corresponding filename, value: term frequency)
#				  									       **term should be stemmed and not in the stopword list**
def index_abstract(filename, abstract, dictionary_abstract):

	filename = filename.replace('.xml', '')

	tokens = tokenize(abstract)
	tokens = [stemmer.stem(token) for token in tokens if token not in stop_list]
	for token in tokens:
		if token in dictionary_abstract and filename in dictionary_abstract[token]:
			dictionary_abstract[token][filename] += 1
		elif token in dictionary_abstract and not filename in dictionary_abstract[token]:
			dictionary_abstract[token][filename] = 1
		else:
			dictionary_abstract[token] = {}
			dictionary_abstract[token][filename] = 1

	return dictionary_abstract

# This function tokenizes a string of text
# Pre-condition : A string of text
# Post-condition: returns a list of tokens, which are text that has been split by nltk word_tokenize method and stripped of any punctuations
def tokenize(text):

	tokenized_text = []
	text = re.sub(r'(\-)|(\/)', " ", text) # replace hyphens and slash with space
	text = word_tokenize(text)
	for word in text:
		stripped_word = word.strip(string.punctuation)
		if stripped_word:
			tokenized_text.append(stripped_word)

	return tokenized_text


def usage():
	print 'usage: ' + sys.argv[0] + '-i directory-of-documents -d dictionary-file -p postings-file'
	# python index.py -i /Users/vincenttan/Documents/patsnap-extract -d dictionary.txt -p postings.txt
	# python index.py -i /Users/vincenttan/Documents/CS3245/Assign4/patsnap-corpus -d dictionary.txt -p postings.txt

directory_doc = dict_file = postings_file = None
try:
	opts, args = getopt.getopt(sys.argv[1:], 'i:d:p')
except getopt.GetoptError, err:
	usage()
	sys.exit(2)
for o, a in opts:
	if o == '-i':
		directory_doc = a
	elif o == '-d':
		dict_file = a
	elif o == '-p':
		postings_file = sys.argv[6] # no idea why postings_file = a renders postings_file empty. That's why I used sys.argv[6] instead.
	else:
		assert False, 'unhandled option'
if directory_doc == None or dict_file == None or postings_file == None:
	usage()
	sys.exit(2)

build_gensim_index(directory_doc, dict_file, postings_file)
build_patsnap_filename_list(directory_doc)
