import getopt
import sys
import xml.etree.ElementTree as ET
import nltk
import string
import logging, gensim, bz2
import operator

from gensim import corpora, models, similarities
from nltk.stem.porter import *
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import defaultdict
from gensim import corpora, models, similarities

stop_list = stopwords.words('english')
stemmer = PorterStemmer()

patent_list = []                            # index to patent file name
linenum_to_offset = []
term_to_linenum_title = dict()
term_to_linenum_abstract = dict()
docfreq_title = dict()
docfreq_abstract = dict()
subclass_to_docs = defaultdict(list)        # dictionary mapping an IPC subclass to a list of patents
subclass_of_doc = dict()

chosen_topic_num = 350                      # how many topics to generate for each document?
chosen_threshold = 0.15                     # how similar must a document be for us to consider it relevant?
to_tdfidf = True                            # will we weight the corpus using tf-idf?

postings = None

def main():
    global postings
    # postings = open(postings_file, 'r')
    # read_dict()                             # reads dictionary into memory
    # parse_offsets()                         # makes one pass through the postings file to store offset positions in memory
    # with open(query_file, 'r') as queries:
    #     with open(out_file, 'w') as out:
    #         ans = process_query(queries)
    #         for item in ans:
    #             out.write(item + "\n")
    read_ipc()
    read_filelist()
    global postings
    postings = open(postings_file, 'r')
    #read_dict()                             # reads dictionary into memory
    #parse_offsets()                         # makes one pass through the postings file to store offset positions in memory
    with open(query_file, 'r') as queries:
        with open(out_file, 'w') as out:
            ans = process_query(queries)
            for item in ans:
                out.write(patent_list[item[0]] + "\n")


def process_query(query_file):

    # Parse query.xml
    tree = ET.parse(query_file)
    root = tree.getroot()
    q_title = stem_and_tokenize(root[0].text.strip().lower())
    q_description = stem_and_tokenize(root[1].text.strip().lower())
    words = q_title + q_description

    # Retrieve the similarity vector for all documents
    ranked_index = rank_lsi(words, to_tdfidf)
    ranked_list = []

    # Add the items from the IPC subclass that appears the most in the top n results
    for item in ranked_index[0]:
        ranked_list.append(patent_list[item[0]])
    subclass_items = subclass_to_docs[get_top_subclass(ranked_list)]
    final = filter(lambda x: x[1] > chosen_threshold or patent_list[x[0]] in subclass_items, ranked_index[1])

    # Sort by similarity again and return
    return sorted(final, key=lambda x: -x[1])


#   Creates the Gensim LSI model, using the dictionary and postings file.
#   Parameters:
#       - words         : a list of words to map the query to an LSI space
#       - with_tfidf    : a boolean to indicate if tf-idf is turned on
#   Returns a list of patents for which the similarity score is more than chosen_threshold and a complete ranked list
def rank_lsi(words, with_tfidf):
    # Read in dictionary.txt and postings.txt
    dictionary = corpora.Dictionary.load(dict_file)
    postings = corpora.MmCorpus(postings_file)

    bag_of_query = dictionary.doc2bow(words)

    if with_tfidf:
        tfidf_model = models.TfidfModel(postings, normalize=True)
        postings = tfidf_model[postings]
    lsi_model = models.LsiModel(postings, id2word=dictionary, num_topics=chosen_topic_num)
    ls_index = similarities.MatrixSimilarity(lsi_model[postings])
    lsi_query = lsi_model[bag_of_query]
    total_lsi_rank = enumerate(ls_index[lsi_query])
    similar_to_query = sorted(total_lsi_rank, key=lambda x: -x[1])
    return [filter(lambda x: x[1] > chosen_threshold, similar_to_query), similar_to_query]

#   Retrieves and returns the list of documents containing words that appear in the query.
#   This list is considered 'large' - contains many irrelevant documents.
def word_matches(q_title, q_abstract):
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

#   Stems, strips punctuations, tokenizes, removes stopwords
#   Returns an array of tokens to be searched for.
def stem_and_tokenize(line):
    tokens = tokenize(line)
    tokens = filter(lambda x: x not in stop_list, tokens)
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

#   Reads ipc_subclass.txt into a (string, list) dictionary, subclass_to_docs
#   Key: subclass - Value: list of patents in the corpus in the subclass
def read_ipc():
    with open('ipc_subclass.txt', 'r') as doc_to_ipc:
        for line in doc_to_ipc:
            arr = line.split(' ')
            patId = arr[0].strip('\n')
            subclass = arr[1].strip('\n')
            subclass_to_docs[subclass].append(patId)
            subclass_of_doc[patId] = subclass

#   For a given list of patents, retrieves the IPC subclasses that the patents are in
#   Returns the most frequently appeared IPC subclass
def get_top_subclass(list_of_patents):
    count = {}
    for patent in list_of_patents:
        if subclass_of_doc.has_key(patent):
            subclass = str(subclass_of_doc[patent]).strip(' \n')
            if subclass in count:
                count[subclass] += 1
            else:
                count[subclass] = 1
    sorted_count = sorted(count.items(), key=operator.itemgetter(1))
    top_subclass = sorted_count[-1][0]
    return top_subclass

#   Reads in the list of files into a list
#   This is for sorted numeric access to a patent name: e.g. patent_list[0]
def read_filelist():
    with open('filenames.txt', 'r') as filenames:
        for filename in filenames:
            filename = filename.replace('.xml', '').strip()
            patent_list.append(filename)

def usage():
    print 'usage: ' + sys.argv[0] + '-d dictionary-file -p postings-file -q query-file -o out-file'
    # python search.py -d dictionary.txt -p postings.txt -q q2.xml -o out.txt

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
