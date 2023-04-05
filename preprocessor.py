import os.path
import re
import html
from math import log10
import pickle
from time import time
from helper_functions import binarySearch, getClitics, normalize, returnTopK


documents_initial = []
source_folder = os.path.join('.', 'reuters21578')   # join two strings with path specifier independent from the OS


# get every article as a document where the id of the document is NEWID parameter of the article
def getDocuments():
    global source_folder, documents_initial

    for file in os.listdir(source_folder):
        
        # get all files with an extension .sgm
        if file.endswith('.sgm'):
            with open(os.path.join(source_folder, file), 'r') as f:
                file_as_string = f.read()

            # while splitting based on </REUTERS> tag, we will have (# of articles) + 1 elements in the list named reuters.
            # the last element in the list does not contain any information because regular expression finds the closing tag
            # for an article and splits from that point, resulting in that the last element is below the last article.
            reuters = re.split('</REUTERS>', file_as_string)

            # traverse articles one by one
            for reuter in reuters[:-1]:

                ### get the docid
                # find the pattern NEWID="[number]"> and get the number from the string.
                # then, convert the string to an integer
                doc_id_search = re.search(r"NEWID=\"([0-9]+)\">", reuter)
                doc_id = int(doc_id_search.group(1))
                

                # get rid of html escape characters like '&lt;', '&#3;'
                reuter = html.unescape(reuter)
                doc = ""

                ### get the title
                # find the pattern "<TEXT...<TITLE>[title_text]</TITLE>..." and get the title_text from the string
                title_search = re.search(r'<TEXT(.|\n)*<TITLE>((.|\n)*)</TITLE', reuter)
                if title_search is not None: # if title is found
                    title = title_search.group(2)
                    doc += title.lower()

                ### get the body
                # find the pattern "<TEXT...<BODY>[body_text]</BODY>..." and get the body_text from the string
                body_search = re.search(r'<TEXT(.|\n)*<BODY>((.|\n)*)</BODY>', reuter)
                if body_search is not None: # if the body is found
                    body = body_search.group(2)
                    doc += " " + body[0].lower() + body[1:]

                # if both title and body cannot be found, that means that the article is in UNPROC format and it contains
                # only <TEXT> parameter, not <TITLE> or <BODY>
                if (title_search is None) and (body_search is None):
                    try:
                        ### get the text
                        # find the pattern "<TEXT...[body_text]</TEXT>" and get the body_text from the string
                        text_search = re.search(r'<TEXT.+\n((.|\n)+)</TEXT>', reuter)
                        body = text_search.group(1)
                        doc = body[0].lower() + body[1:]
                    except:
                        print(reuter, '\nerror')
                        return

                # gather the documents in an array
                documents_initial.append([doc_id, doc])

            f.close()





def getDictionary(documents):
    # Create an empty set to store the tokens
    dictionary = set()

    # Loop over each document in the list of documents
    for document_pair in documents:
        # Get the document text from the document pair
        document = document_pair[1]

        # Loop over each token in the document
        for token in document:
            # If the token is not empty, add it to the dictionary set
            if token:
                dictionary.add(token)
    
    # Return the set of tokens
    return dictionary


def splitTokens(documents, splitted):
    splitted = []
    # Loop over each document in the list of documents
    for document_pair in documents:
        # Split the document text into a list of tokens using a regular expression
        token_list = re.split('\s+', document_pair[1])
        # Add the document ID and the list of tokens to the output list
        splitted.append([document_pair[0], token_list])

    return splitted


def normalizeDocuments(documents):
    # Get a set of clitics (words like "we're", "I'm", etc.)
    clitics = getClitics()

    # Initialize variables to keep track of token counts before and after normalization
    tokens_before_normalization = 0
    tokens_after_normalization = 0

    # Create an empty list to store the normalized documents
    normalized_documents = []

    # Split the input documents into lists of tokens
    splitted_documents = splitTokens(documents, [])

    # Get the set of unique tokens(terms) in the input documents
    dictionary_before_normalization = getDictionary(splitted_documents)

    # Loop over each document in the list of tokenized documents
    for document_pair_index in range(len(splitted_documents)):
        # Get the list of tokens for the current document
        word_list = splitted_documents[document_pair_index][1]
        # Increment the count of tokens before normalization
        tokens_before_normalization += len(word_list)

        # Normalize the list of tokens
        normalized_document, normalization_tokens = normalize(word_list, clitics)
        # Increment the count of tokens after normalization
        tokens_after_normalization += normalization_tokens

        # Add the normalized document to the list of normalized documents, along with its original ID
        normalized_documents.append((documents[document_pair_index][0], normalized_document))
    
    # Return the list of normalized documents, along with the counts of tokens before and after normalization,
    # and the size of the dictionary before normalization
    return normalized_documents, tokens_before_normalization, tokens_after_normalization, len(dictionary_before_normalization)



def createInvertedIndex(term_list, normalized_documents):
    # Create an empty list to hold the final inverted index
    final_inverted_index = []
    for _ in range(len(term_list)):
        # Keep the record of frequency and a dictionary which will map
        # the document ids with the list of positions where the term occures 
        final_inverted_index.append([0, {}])

    # Loop over each document in the list of normalized documents
    for document_pair in normalized_documents:
        # Get the ID and token list of the current document
        document_id = document_pair[0]
        document = document_pair[1]

        # Loop over each token in the document
        for token_index in range(len(document)):
            token = document[token_index]

            # Check if the token is not empty
            if token:
                # Use binary search to find the position of the token in the dictionary
                # since the dictionary is sorted in ascending order
                position = binarySearch(term_list, token)

                # If the token is in the dictionary
                if position != -1:
                    # Increase the frequency of the term by 1
                    final_inverted_index[position][0] += 1

                    # Try to append the token position to the posting list of the current document
                    try:
                        final_inverted_index[position][1][document_id].append(token_index)
                    # If the posting list for the current document doesn't exist yet, create it
                    except:
                        final_inverted_index[position][1][document_id] = [token_index]

    # Return the final inverted index
    return final_inverted_index



# This function retrieves the term frequency for each term from the inverted index.
# It takes as input:
# - inverted_index: a list of lists where each inner list contains the term frequency and postings lists
# It returns:
# - result: a list of tuples containing the index of the term in the dictionary and its frequency in the corpus

def getFrequencies(inverted_index):
    
    result = []

    # Iterate over each term in the inverted index and retrieve its frequency
    for index in range(len(inverted_index)):

        # Add the term's index and frequency to the result list as a tuple
        result.append((index, inverted_index[index][0]))

    # Return the list of term frequencies
    return result


# This function calculates the TF-IDF score for each term in the inverted index and returns the TF-IDF scores and document frequencies.
# It takes as input:
# - inverted_index: a list of lists where each inner list contains the term frequency and postings lists
# - num_of_documents: an integer representing the total number of documents in the corpus
# It returns:
# - tf_idf_scores: a list of tuples containing the index of the term in the dictionary and the TF-IDF score for that term
# - document_frequencies: list of document frequencies for each term

def calculateScores(inverted_index, num_of_documents):
    
    tf_idf_scores = []
    document_frequencies = []

    # Iterate over each index for the corresponding term in the inverted index 
    # and calculate TF-IDF score and document frequency of the term
    for term_id in range(len(inverted_index)):

        # Calculate IDF for the term
        idf = num_of_documents / len(inverted_index[term_id][1])

        # Calculate TF-IDF score for the term
        score = inverted_index[term_id][0] * log10(idf)
        
        # Add the term's TF-IDF score to the list of tf-idf scores
        tf_idf_scores.append((term_id, score))

        # Calculate and add the document frequency for the term to the list of document frequencies
        document_frequencies.append(1 / idf)

    # Return the lists of TF-IDF scores and document frequencies
    return tf_idf_scores, document_frequencies


# This function determines the stop words based on their TF-IDF score and document frequency.
# It takes as input:
# - tf_idf_scores: a list of tuples containing the index of the term in the dictionary and the TF-IDF score for each term
# - threshold: a float value between 0 and 1 to find the terms that cover the given fraction of total tf-idf scores of all terms given
# - document_frequencies: list of document frequency for each term
# It returns:
# - stopword_list: a list of stop words, which are identified by their TF-IDF score and document frequency.

def determineStopWords(tf_idf_scores, threshold, document_frequencies):

    # Calculate the total score
    total_score = 0
    for id, score in tf_idf_scores:
        total_score += score 

    # get the tf-idf score of each term and add it to the stopword list
    # if the document frequency of that term is not less than 0.4
    # if the tf-idf scores of collected terms exceeds the threshold, terminate the collection.
    stopword_scores = 0
    stopword_list = []
    for id, score in tf_idf_scores:
        document_frequency = document_frequencies[id]

        # Skip terms with a low document frequency
        if document_frequency < 0.4:
            continue

        # Add the term to the stopword list and update the total stopword score
        stopword_scores += score
        stopword_list.append(id)
       
        # If the stopword score exceeds the threshold, stop adding terms to the list
        if stopword_scores >= total_score * threshold:
            break

    # Return the list of stop words
    return stopword_list



# Get the start time to calculate the total execution time of the program
start_time = time()


# Get the raw documents
getDocuments()


# Normalize the documents, derive the dictionary after normalization and the number of terms before and after normalization
normalized_documents, num_of_tokens_before_normalization, num_of_tokens_after_normalization, num_of_terms_before_normalization = normalizeDocuments(documents_initial)
dictionary_after_normalization = getDictionary(normalized_documents)


# Write preprocessing metrics to a file
with open('preprocessing_metrics.txt', 'w') as metric_file:
    lines = [
                f'Number of tokens before normalization: {num_of_terms_before_normalization}\n',
                f'Number of tokens after normalization: {num_of_tokens_after_normalization}\n',
                f'Number of terms before normalization: {num_of_terms_before_normalization}\n',
                f'Number of terms after normalization: {len(dictionary_after_normalization)}\n'
            ]
    
    metric_file.writelines(lines)

metric_file.close()


# Create the final dictionary and sort it to prepare it for the searching operations(binary search)
final_dictionary = list(dictionary_after_normalization)
final_dictionary.sort()


# Create the final inverted index
final_inverted_index = createInvertedIndex(final_dictionary, normalized_documents)


# Get the frequencies of terms in the inverted index and return the top 100 frequent terms
frequencies = getFrequencies(final_inverted_index)
top_k_terms = returnTopK(frequencies, 100)

# Write the top 100 frequent terms to a file
with open('top_100_frequent_terms.txt', 'w') as f:
    for index, frequency in top_k_terms:
        f.write(f'Term {final_dictionary[index]} appeared {frequency} times in documents\n')

f.close()


# Calculate the TF-IDF scores for the terms and get the top 1000 terms based on TF-IDF scores
tf_idf_list, document_frequencies = calculateScores(final_inverted_index, len(normalized_documents))
top_k_tf_idf = returnTopK(tf_idf_list, 1000)

# Determine the stop words based on TF-IDF scores and document frequency of top 1000 term found
stop_word_list = determineStopWords(top_k_tf_idf, 0.1, document_frequencies)


# Save the final dictionary, inverted index and stop words in pickle files
with open('dictionary.pickle', 'wb') as dictionary_file:
    pickle.dump(final_dictionary, dictionary_file)

with open('index.pickle', 'wb') as index_file:
    pickle.dump(final_inverted_index,index_file)

with open('stopwords.pickle', 'wb') as stopword_file:
    pickle.dump(stop_word_list, stopword_file)


# Get the end time and calculate the total execution time of the program
end_time = time()
print(f'\n\nPreprocessing took {end_time - start_time} seconds')
