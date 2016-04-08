import getopt
import sys
import xml.etree.ElementTree as ET
import nltk
from nltk.stem.porter import *
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer

stop_list = stopwords.words('english')
stemmer = PorterStemmer()

def main():
    process_query(query_file)

def process_query(query_file):
    tree = ET.parse(query_file)
    root = tree.getroot()
    q_title = root[0].text.strip()
    q_description = root[1].text.strip()



def usage():
    print 'usage: ' + sys.argv[0] + '-d dictionary-file -p postings-file -q query-file -o output-positive-results-file -n output-negative-results-file'
    #python search.py -d dictionary.txt -p postings.txt -q q1.xml -o q1-qrels+ve.txt q1-qrels-ve.txt  

dict_file = postings_file = query_file = positive_out_file = negative_out_file = None
try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o')
except getopt.GetoptError, err:
    usage()
    sys.exit(2)
for o, a in opts:
    if o == '-d':
        dict_file = a
    elif o == '-p':
        postings_file = a
    elif o == '-q':
        query_file = a
    elif o == '-o':
        positive_out_file = a
        negative_out_file = sys.argv[9]
    else:
        assert False, 'unhandled option'
if dict_file == None or postings_file == None or query_file == None or positive_out_file == None or negative_out_file == None:
    usage()
    sys.exit(2)

main()