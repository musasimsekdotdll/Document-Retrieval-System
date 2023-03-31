import os.path
import re
import html


documents = []
source_folder = os.path.join('.', 'reuters21578')   # join two strings with path specifier independent from the OS


# get every article as a document where the id of the document is NEWID parameter of the article
def getDocuments():


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
                if title_search is not None: # if title is not found
                    doc += title_search.group(2)

                ### get the body
                # find the pattern "<TEXT...<BODY>[body_text]</BODY>..." and get the body_text from the string
                body_search = re.search(r'<TEXT(.|\n)*<BODY>((.|\n)*)</BODY>', reuter)
                if body_search is not None: # if the body is not found
                    doc += body_search.group(2)

                # if both title and body cannot be found, that means that the article is in UNPROC format and it contains
                # only <TEXT> parameter, not <TITLE> or <BODY>
                if (title_search is None) and (body_search is None):
                    try:
                        ### get the text
                        # find the pattern "<TEXT...[body_text]</TEXT>" and get the body_text from the string
                        text_search = re.search(r'<TEXT.+\n((.|\n)+)</TEXT>', reuter)
                        doc = text_search.group(1)
                    except:
                        print(reuter, '\nerror')
                        return

                ### get rid of "reuter" at the end
                # if the document contains "Reuter" or "REUTER" with some whitespace characters at the end, cut that part away from the document 
                reuter_finish_search = re.search('((.|\n)+)(REUTER|Reuter)\s*\Z', doc)
                doc = reuter_finish_search.group(1) if reuter_finish_search is not None else doc

                # gather the documents in an array
                documents.append([doc_id, doc])

            f.close()

    



def tokenizeDocument():
    print('hello')

getDocuments()