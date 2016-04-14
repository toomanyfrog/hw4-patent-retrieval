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

stop_list = stopwords.words('english')
stemmer = PorterStemmer()

def build_index(directory_doc, dict_file, postings_file):

	# count = 1

	dictionary_title = {}
	dictionary_abstract = {}

	ipc_subclass_file = open('ipc_subclass.txt', 'w')

	for filename in os.listdir(directory_doc):
		# count += 1
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


def tokenize(text):

	tokenized_text = []
	text = re.sub(r'(\-)|(\/)', " ", text) #replace hyphens and slash with space
	text = word_tokenize(text)
	for word in text:
		stripped_word = word.strip(string.punctuation)
		if stripped_word:
			tokenized_text.append(stripped_word)

	# text = [word.strip(string.punctuation) for word in text]

	return tokenized_text


def usage():
	print 'usage: ' + sys.argv[0] + '-i directory-of-documents -d dictionary-file -p postings-file'
	#python index.py -i /Users/vincenttan/Documents/patsnap-extract -d dictionary.txt -p postings.txt
	#python index.py -i /Users/vincenttan/Documents/CS3245/Assign4/patsnap-corpus -d dictionary.txt -p postings.txt

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

build_index(directory_doc, dict_file, postings_file)
