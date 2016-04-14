import getopt
import sys
import xml.etree.ElementTree as ET
import nltk
import string
import gensim
from nltk.stem.porter import *
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

stop_list = stopwords.words('english')
stemmer = PorterStemmer()

linenum_to_offset = []
term_to_linenum_title = dict()
term_to_linenum_abstract = dict()
docfreq_title = dict()
docfreq_abstract = dict()

postings = None

def main():
    parse_ipc()
    global postings
    postings = open(postings_file, 'r')
    read_dict()                             # reads dictionary into memory
    parse_offsets()                         # makes one pass through the postings file to store offset positions in memory
    with open(query_file, 'r') as queries:
        with open(out_file, 'w') as out:
            ans = process_query(queries)
            for item in ans:
                out.write(item + "\n")

#   Retrieves and returns the list of relevant documents to the query.
#   Ranks matches for words in title before that of the body.
#   No tf-idf yet.
def process_query(query_file):
    tree = ET.parse(query_file)
    root = tree.getroot()
    q_title = stem_and_tokenize(root[0].text.strip().lower())
    q_description = stem_and_tokenize(root[1].text.strip().lower())
    results = []
    for head_word in q_title:
        pl = get_postings(head_word,'title')
        for item in pl:
            if item[0] not in results:
                results.append(item[0])
    for body_word in q_description:
        pl = get_postings(body_word,'abstract')
        for item in pl:
            if item[0] not in results:
                results.append(item[0])
    return results

#   Stems, strips punctuations, tokenizes
#   Returns an array of tokens to be searched for.
def stem_and_tokenize(line):
    tokens = tokenize(line)
    tokens = [stemmer.stem(token) for token in tokens if token not in stop_list]
    return tokens

#   Tokenizes the text and strips punctuations
#   Written by Tricia in index.py
def tokenize(text):
    tokenized_text = []
    text = re.sub(r'(\-)|(\/)', " ", text) #replace hyphens and slash with space
    text = word_tokenize(text)
    for word in text:
        stripped_word = word.strip(string.punctuation)
        if stripped_word:
            tokenized_text.append(stripped_word)
    return tokenized_text


#   Converts each line number to a file-offset for seeking in postings.txt
#   Stores the file-offset for line i into linenum_to_offset[i]
def parse_offsets():
    offset = 0
    for line in postings:
        linenum_to_offset.append(offset)
        offset += len(line)
    postings.seek(0)


#   Retrieves the postings list for the term from either the TITLE or ABSTRACT field
#   Returns an array of (str,int) pairs: [ patentID, term-freq ]
def get_postings(term, title_or_abstract):
    postings.seek(0)
    if title_or_abstract == "title":
        postings.seek(linenum_to_offset[term_to_linenum_title[term]])
    elif title_or_abstract == "abstract":
        postings.seek(linenum_to_offset[term_to_linenum_abstract[term]])
    postlist = postings.readline().strip(' \n')
    postlist = postlist.split(' ')
    for i in range(0, len(postlist)):
        item = postlist[i]
        postlist[i] = item.split(',')
        postlist[i][1] = int(postlist[i][1])
    return postlist


#   Reads dictionary.txt into 2 Python dictionaries: TITLE and ABSTRACT
#   Key: term - Value: line number in file
def read_dict():
    with open(dict_file, 'r') as file:
        i = 0
        for line in file:
            arr = line.split(' ')
            key = arr[0].split('.')
            if key[1] == 'title':
                docfreq_title[key[0]] = arr[1]
                term_to_linenum_title[key[0]] = i
            elif key[1] == 'abstract':
                docfreq_abstract[key[0]] = arr[1]
                term_to_linenum_abstract[key[0]] = i
            i += 1


def parse_ipc():
    tree = ET.parse('ipc_definitions.xml')
    root = tree.getroot()
    for definition in root.iter():
        if "GLOSSARYOFTERMS" in definition.tag:
            for xhtml_p in definition.iter():
                if "{http://www.w3.org/1999/xhtml}p" in xhtml_p.tag:
                    print xhtml_p.text

def usage():
    print 'usage: ' + sys.argv[0] + '-d dictionary-file -p postings-file -q query-file -o out-file'
    # python search.py -d dictionary.txt -p postings.txt -q q1.xml -o out.txt

dict_file = postings_file = query_file = out_file = None
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
        out_file = sys.argv[8]
    else:
        assert False, 'unhandled option'
if dict_file == None or postings_file == None or query_file == None or out_file == None:
    usage()
    sys.exit(2)

main()
