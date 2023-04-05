from string import punctuation as string_punctuation
from re import search as regex_search
from re import split as regex_split
from re import sub as regex_substitute
from heapq import heapify, heappop, heappush
from os import path as os_path



def normalize(token_list, clitics_set):

    # regular expression that will detect either a word, words with hyphens included, or a token composing of numbers
    # with special characters('/', ':', '.', ',') like 16/20, 19.02.2021, etc.
    shave_string = f'[{string_punctuation}]*([\d/:.,]+\d+)|([\w-]+)[{string_punctuation}]*'

    # a sentence will probably end with one of the following punctuation marks: '.', '!', '?', '...'
    end_of_sentence = r'[.?!]|[...]'
    # a flag that will show that the previous word is the last word of the sentence, which means the current word is the beginning of the sentence
    sentence_beginning = False

    # final document as a list of its tokens
    final_document = []

    tokens_after_normalization = 0

    for word in token_list:
            
        if word.lower() not in clitics_set:

            # shave the token
            shaved = regex_search(shave_string, word)
            if shaved is not None:
                # as described in the definition of shave_string, token can be in one of the 2 different forms
                token = shaved.group(1) if shaved.group(1) is not None else shaved.group(2)

                # # keep terms before the normalization
                # dictionary_before_normalization.add(token)

                # detect hyphenated words
                dash_search = regex_search('-', token)

                # after this conditional block, we will have a list of tokens named as token_splitted
                if dash_search:
                    # if the first character of the hyphenated word is upper, like Hewett-Pickard or New York-San Fransisco, then they should be 
                    # splitted and taken as different strings. if the first character is lower, then all hyphens should be deleted and the result will be
                    # one word('know-how' to 'knowhow')
                    tokens_splitted = regex_split('-', token) if token[0].isupper() else [regex_substitute('-', '', token)]
                else:
                    # if no hyphen detected, then the token is taken directly
                    tokens_splitted = [token]

                for splitted in tokens_splitted:
                    if splitted:
                        # if the first character of the token is upper and it is not the beginning of the sentence, then keep the token with uppercase letters.
                        # otherwise, lower the letters
                        splitted = splitted if (splitted[0].isupper() and (not sentence_beginning)) else splitted.lower()
                        
                        # # keep terms after normalization
                        # dictionary_after_normalization.add(splitted)
                        # keep the number of tokens after normalization
                        tokens_after_normalization += 1

                        final_document.append(splitted)

            end_of_sentence_search = regex_search(end_of_sentence, word)
            sentence_beginning = end_of_sentence_search is not None
        else:
            # # keep terms before the normalization
            # dictionary_before_normalization.add(word)

            token = word.lower()

            # # keep terms after normalization
            # dictionary_after_normalization.add(word)
            # keep the number of tokens after normalization
            tokens_after_normalization += 1
            
            final_document.append(token)

    return final_document, tokens_after_normalization



## this algorithm is taken from https://www.geeksforgeeks.org/python-program-for-binary-search/

# Iterative Binary Search Function
# It returns index of search_element in given dictionary arr if present,
# else returns -1
def binarySearch(dictionary, search_element):
    low = 0
    high = len(dictionary) - 1
    mid = 0
 
    while low <= high:
 
        mid = (high + low) // 2
 
        # If search_element is greater, ignore left half
        if dictionary[mid] < search_element:
            low = mid + 1
 
        # If search_element is smaller, ignore right half
        elif dictionary[mid] > search_element:
            high = mid - 1
 
        # means search_element is present at mid
        else:
            return mid
 
    # If we reach here, then the element was not present
    return -1



def returnTopK(elements, k):

    # Create a max heap of tuples containing the negative frequency and the index of the term in the dictionary
    # Note that we negate the frequency, which is our sorting base.
    # That is because built-in Python libraries support only min heaps. 
    # minimum among the negative frequencies is the maximum among the actual ones, which are positives definitely.
    max_heap = [(-sort_base, return_element) for return_element, sort_base in elements]
    heapify(max_heap)

    # Create an empty list to hold the top k elements
    result = []

    # Initialize a counter to keep track of how many elements have been added to the result list
    counter = 0
    # Get the length of the elements list to ensure we don't try to add more elements than there are
    elements_length = len(elements)

    # Loop until either k elements have been added to the result list or all elements have been processed
    while counter < k and counter < elements_length:
        # Pop the minimum element from the heap (which has the highest positive sort base)
        sort_base, return_element = heappop(max_heap)
        # Append the element to the result list along with its actual base
        result.append((return_element, -sort_base))
        # Increment the counter
        counter += 1

    # Return the list of top k elements
    return result



def getClitics():
    # Create an empty set to store the clitics
    clitics = set()
    
    # Create a path to the file containing the clitics
    clitic_path = os_path.join('.', 'clitics.txt')

    # Open the file containing the clitics
    with open(clitic_path) as stop_file:
        # Read all the lines in the file
        stop_lines = stop_file.readlines()

    # Loop over each line in the file
    for line in stop_lines:
        # Remove the newline character from the end of the line
        stopword = line[:-1]
        # Add the clitic to the set of clitics
        clitics.add(stopword)

    # Return the set of clitics
    return clitics