This is the README file for A0116733J-A0115696W's submission

== General Notes about this assignment ==

your system architecture and how your system deals with each of the optional components (query expansion, utilizing external resources, field/zone treatment, run-time optimizations,

<<<Mini Patent Retrieval System Architecture Overview>>>

As known, there are two main components in the system: Indexing and Searching.

In pre-processing, the Indexing component does the following:
1. Use xml.etree.ElementTree to parse patsnap corpus XML files.
2. Index only Title and Abstract of the patent files
3. Use Porter Stemmer and Stopword list filtering for text processing
4. Use Gensim library to implement topic modeling

When user query the system, the Searching component does the following:
1. Dissect query into a bag of words
2. Use tf-idf weighting with query terms
3. Model the query with Latent Semantic Indexing 
4. Compare query with LSI models (???)
 

---- Failed attempts (hence not included in final build) ----

Main Points For Previous Attempts:

I) We attempted the use of the Latent Dirichlet Allocation model, but the performance results fared worse-off as compared to the use of Latent Semantic Indexing. As a result, we decided against it and chose to use Latent Semantic Indexing instead.

II) We attempted query expansion, by indexing all the words in title and abstract from the top 1% of the results, but it did not work very well possibly due to the extra noise produced by the additional words in the patents. May work better if we are able to determine the key words, instead of indexing all the words in the patent files.

III) Our code for other previous attempts can be found in our index.py and search.py files (Commented out)

---- Allocation of Work ----
I) Choo Jia Le: Did research on Latent Semantic Indexing heuristics, testing of cases and brainstorming on further ideas to improve precision and accuracy.

II) Lim Jing Rong: Did debugging, testing of cases and research of Latent Dirichlet Allocation modeling heuristics.

III) Nelson Goh: Did research on the ideas of topic modeling and implementation on Python. Found relevant libraries and models to use for this assignment.

All members participated and contributed equally and carried out pair-programming during the period of this assignment.


---- Misc -----
We also created a function (is_ascii) to detect non-ascii characters during the reading of our patent documents, and subsequently ignore it, as part of processing.

Things that we could have done better:

I) Could have carried out more queries and conducted more experiements to find out a more accurate distribution of topics for our corpus, for better modeling.
 
== Files included with this submission ==

List the files in your submission here and provide a short 1 line
description of each file.  Make sure your submission's files are named
and formatted correctly.

-gensim					// Third-party library that does topic modelling 
-dictionary.txt 		// Dictionary object from gensim written to this file 
-filenames.txt 			// (Not included in submission, appears only when running index.py) This is a list of the patent names in the patsnap-corpus
-index.py 				// The file that indexes patsnap-corpus. Generates dictionary.txt and postings.txt
-ipc_subclass.txt 		// ??????
-postings.txt 			// Matrix from gensim written to this file
-README.md 				// self-explanatory
-search.py 				// The file that returns a ranked results based of xml search query


== Statement of individual work ==

Please initial one of the following statements.

[X] I, A0116733J, certify that my partners (A0115696W) and I have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I
expressly vow that I have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[X] I, A0116733J-A0115696W, did not follow the class rules regarding homework
assignment, because of the following reason:

// text

I suggest that I should be graded as follows:

// text

== References ==

Discussed with Nelson, who has previously taken this module.