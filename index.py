import sys
import getopt
import os
import re
import math
import xml.etree.ElementTree as ET
import nltk
from nltk.stem.porter import *
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer

def build_index(directory_doc, dict_file, postings_file):

	count = 1

	for filename in os.listdir(directory_doc):
		count += 1
		f = os.path.join(directory_doc, filename)
		tree = ET.parse(f)
		root = tree.getroot()
		for child in root:
			if child.attrib['name'] == 'Title':
				title = child.text.strip().lower()
				index_title(title, postings_file)
			if child.attrib['name'] == 'Abstract':
				abstract = child.text.strip().lower()
				index_abstract(abstract, postings_file)

		#print count

def index_title(title):

	p = open(postings_file, 'w')

	tokens = tokenize(title)
		for token in tokens:
			p.write(token + '.title' + '\n')
			# william.title [doc_freq] [patent_no., term_freq] [patent_no.] 

def index_abstract(abstract):
	return 0

def tokenize(text):

	remove_punctuations = RegexpTokenizer(r'((?<=[^\w\s])\w(?=[^\w\s])|(\W))+', gaps=True)

	return remove_punctuations.tokenize(text)

def usage():
	print 'usage: ' + sys.argv[0] + '-i directory-of-documents -d dictionary-file -p postings-file'
	#python index.py -i /Users/vincenttan/Documents/patsnap-extract -d dictionary.txt -p postings.txt

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
