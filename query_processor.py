from pickle import load as pickle_load
from helper_functions import binarySearch, getClitics, normalize, returnTopK
from re import search as regex_search
from re import sub as regex_substitute
from re import split as regex_split


with open('dictionary.pickle', 'rb') as dictionary_file:
    dictionary = pickle_load(dictionary_file)

dictionary_file.close()


with open('index.pickle', 'rb') as index_file:
    inverted_index = pickle_load(index_file)

index_file.close()


with open('stopwords.pickle', 'rb') as stopword_file:
    stopword_list = pickle_load(stopword_file)
    stopwords = set([dictionary[index] for index in stopword_list])

stopword_file.close()

clitics = getClitics()



# This function takes two lists and returns their intersection, i.e., the elements that are common to both lists.
# It takes as input:
# - first_list: the first list of elements
# - second_list: the second list of elements
# It returns:
# - result: a list of elements that are present in both the input lists.

def intersect(first_list, second_list):
    result = []

    # Initialize index variables to traverse the lists
    first_index = 0
    second_index = 0

    # Traverse the lists and append common elements to the result list
    while first_index < len(first_list) and second_index < len(second_list):
        
        if first_list[first_index] == second_list[second_index]:
            result.append(first_list[first_index])
            first_index += 1
            second_index += 1
        
        # If the current element in the first list is smaller, move the first index forward
        elif first_list[first_index] < second_list[second_index]:
            first_index += 1

        # If the current element in the second list is smaller, move the second index forward
        else:
            second_index += 1

    # Return the list of common elements
    return result




# This function merges lists of document IDs into one resulting list by computing the intersection of lists.
# It takes as input:
# - document_id_lists: a list of lists, where each inner list contains the IDs of documents in which a term appears
# It returns:
# - result_list: a list of document IDs that is common in all the input lists.

def mergeLists(document_id_lists):

    if not document_id_lists:
        return []
    
    # Calculate the length of each list and store it in postings_length list with its index
    # so that the index of a list does not disappear while sorting postings lists by their length
    postings_length = [(index, len(document_id_lists[index])) for index in range(len(document_id_lists))]
    

    # Sort postings_length in descending order of length and store the index of a postings list with it
    length_order = returnTopK(postings_length, len(postings_length))


    # Initialize the result list with the IDs from the shortest list
    result_list = document_id_lists[length_order[-1][0]]


    # Iterate over the remaining lists and compute their intersection with result_list
    for i in range(len(length_order) - 2, -1, -1):
        index_second = length_order[i][0]
        second_list = document_id_lists[index_second]

        # Compute the intersection of result_list and the current list
        result_list = intersect(result_list, second_list)


        # If the intersection is empty, return an empty list
        if len(result_list) == 0:
            return []


    # Return the list of common document IDs
    return result_list



# This function executes a phrase query by finding the documents that contain all the terms no matter their location
# It takes as input:
# - normalized_query: a list of terms representing the query
# It returns:
# - a tuple consisting of:
#   - document_ids: a list of IDs of documents that contain the phrase
#   - dictionary_positions: positions in the dictionary of the normalized versions of the tokens(terms) in the query 

def phraseQuery(normalized_query):
    
    global clitics, inverted_index, dictionary


    # Initialize variables to store the document ID lists and dictionary positions of each term
    document_id_lists = []
    dictionary_positions = []

    # Iterate over each term in the normalized query
    for term in normalized_query:
        # Find the position of the term in the dictionary using binary search
        position = binarySearch(dictionary, term)

        # If the term is not in the dictionary, return an empty list
        if position == -1:
            return [], None
        # If the term is in the dictionary, get the list of document IDs that contain the term
        else:
            document_ids = list(inverted_index[position][1].keys())
            document_id_lists.append(document_ids)

            # Add the position of the term in the dictionary to the list of dictionary positions
            dictionary_positions.append(position)

    # Merge the document ID lists to find the documents that contain all the terms in the query
    # and return ids of those documents
    return mergeLists(document_id_lists), dictionary_positions



# This function finds documents where two query terms appear within a distance of k words of each other
# It takes as input:
# - first_word: the first query term
# - second_word: the second query term
# - k: an integer specifying the maximum distance(number of words) allowed between the two query terms
# It returns:
# - result: a list of document ids where the two query terms appear within a distance of k words of each other

def proximityQuery(first_word, second_word, k):
    
    global inverted_index
    
    # Get the document lists where the two query terms appear using the phraseQuery function
    lookup_lists, dictionary_indexes = phraseQuery([first_word, second_word])
    result = []

    # For each document in the lookup lists, find the positions of the two query terms
    # and check if they appear within a distance of k words of each other
    for document_id in lookup_lists:
        positions_first = inverted_index[dictionary_indexes[0]][1][document_id]
        positions_second = inverted_index[dictionary_indexes[1]][1][document_id]

        index_first = 0
        index_second = 0
        while index_first < len(positions_first) and index_second < len(positions_second):
            
            first_position = positions_first[index_first]
            second_position = positions_second[index_second]
            distance = abs(first_position - second_position)

            # If the distance between the two query terms is within k, add the document id to the result list
            if distance <= k + 1:
                result.append(document_id)
                break
            
            # If the first query term appears before the second in the document, move to the next position of the first term
            elif first_position < second_position:
                index_first += 1
            # If the second query term appears before the first in the document, move to the next position of the second term
            else:
                index_second += 1

    return result



while True:
    inp = input("Enter your query:\n")
    
    if inp == ".":
        break
    
    # Use regex to check if the input query is a phrase or proximity query
    search = regex_search(r'\"(.+)\"|(\A\w+\s+\d\s+\w+\Z)', inp)
    
    if search:
        if search.group(1): # Phrase query
            tokens = regex_split(r'\s+', search.group(1))
            
            # Normalize the query as documents are normalized
            normalized_query, _ = normalize(tokens, clitics)

            # add terms that are not in the stopwords set
            query = []
            for term in normalized_query:
                if term not in stopwords:
                    query.append(term)

            # Call the phraseQuery function to get the list of matching documents
            result, _ = phraseQuery(query)
            print(result)

        else: # Proximity query
            tokens = regex_split(r'\s+', search.group(2))

            # Extract the first term, second term, and proximity value
            first_term = tokens[0]
            second_term = tokens[2]
            k = int(tokens[1])

            # Normalize the query terms
            normalized_query, _ = normalize([first_term, second_term], clitics)

            # Call the proximityQuery function to get the list of matching documents
            result = proximityQuery(normalized_query[0], normalized_query[1], k)
            print(result)

