This is the README file for A0116733J-A0115696W's submission

== General Notes about this assignment ==

==============================================================================================
<<<  Mini Patent Retrieval System Architecture Overview  >>>
==============================================================================================
As known, there are two main components in the system: Indexing and Searching.

In pre-processing, the Indexing component does the following:
    1. Use xml.etree.ElementTree to parse patsnap corpus XML files.
    2. Retrieve the words from the title and abstract zones of the corpus patents.
    3. Remove punctuation, stopwords, and conduct stemming
    4. Create a gensim-compatible Dictionary and Postings: the dictionary object is provided by gensim,
       and the Postings is represented in the Matrix Market format.
    5. Create a document-to-IPC-subclass mapping.
    6. Create an index of patent file names (to be used in search.py).

At query-time, our algorithm does the following:
    1. Collect all the words from the title and description part of the XML query
    2. Utilize gensim library to generate the LSI space for the corpus
    3. Do tf-idf weighting on this corpus
    4. Generate the topic space for the bag of words created from the query file
    5. For each document in the corpus, compute a similarity score between the document and the query file
    6. Retrieve a list of those documents for which the similarity score is above a certain threshold(1) and
       find out what the most frequent IPC subclass is amongst these documents.
    7. Retrieve all the documents that are classified under that IPC subclass and include this in the final list.
    8. Sort the final list by similarity (higher similarity scores appear higher)


==============================================================================================
Strategy    
==============================================================================================
Our rationale for this strategy is based on the following observations:
    - patent retrieval is a high-recall task
    - many synonyms are used; patents using different words could be describing the same things
    - these different words may not all appear in the query file
    - removing stopwords is not sufficient to narrow down the idea of the query file, many different words are used (e.g.
        'technology' which are not central to the topic)

Based on these observations, we decided to use topic modelling after doing some research into patent retrieval.
The idea we wanted to implement was a way to decide what topics a certain document was discussing, and compare based on that.

Further, our topic modelling strategy is dependent on a few parameters:
    1. number of topics
    2. chosen_threshold

(1) We would tweak the number of topics and chosen_threshold based on heuristic testing.


==============================================================================================
Limitations:
==============================================================================================
Since our parameters are chosen based on limited data (q1 and q2), it is likely that the threshold and number chosen is
not a good gauge. Secondly, since we do our evaluation manually and we are not patent experts, we may not classify documents
the same way as an expert might, and it takes very long.

Additionally, LSI requires high computational performance and memory compared to other IR techniques. And, there is difficulty
in determining optimal number of dimensions to use



==============================================================================================
Previous attempts:
==============================================================================================
We tried to do zone/field indexing according to the lecture, such as term.title, term.abstract as seen in build_index() function. However we realise that building a data structure and handling accuracy of retrieval on our own is not going to be efficient and accurate. This was further proved with the output we generated. Therefore we decided to use the third party library to improve accuracy drastically.
We have included the code in the file.


==============================================================================================
Files included with this submission:
==============================================================================================
List the files in your submission here and provide a short 1 line
description of each file.  Make sure your submission's files are named
and formatted correctly.

- gensim				// Third-party library used for topic modelling: needs to be installed.
- dictionary.txt 		// Dictionary object from gensim written to this file
- filenames.txt 	    // (Not included in submission, appears only when running index.py) This is a list of the patent names in the -   patsnap-corpus
- index.py 				// The file that indexes patsnap-corpus. Generates dictionary.txt and postings.txt
- ipc_subclass.txt 		// Contains the document-subclass mapping
- postings.txt 			// Matrix from gensim written to this file
- README.md 			// self-explanatory
- search.py 			// The file that returns ranked results based of xml search query


== Statement of individual work ==

Please initial one of the following statements.

[X] I, A0116733J, certify that my partners (A0115696W) and I have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I
expressly vow that I have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[ ] I, A0116733J-A0115696W, did not follow the class rules regarding homework
assignment, because of the following reason:


I suggest that I should be graded as follows:


== References ==

Discussed with Nelson, who has previously taken this module (the Facebook rule was strictly adhered to).
Referred to this a lot for the strategy https://en.wikipedia.org/wiki/Latent_semantic_indexing
API reference for gensim library https://radimrehurek.com/gensim/apiref.html
