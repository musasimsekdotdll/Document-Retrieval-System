from bs4 import BeautifulSoup
import os.path
import re


documents = []
source_folder = os.path.join('.', 'reuters21578')   # join two strings with path specifier independent from the OS


# get the documents as articles, 
def getDocuments():
    for file in os.listdir(source_folder):
        if file.endswith('.sgm'):
            f = open(os.path.join(source_folder, file), 'r')
            # s = f.read().encode("latin-1")

            soup = BeautifulSoup(f, features="html.parser", from_encoding="latin-1")
            # pretty_soup = soup.prettify()

            reuters = soup.find_all('reuters')
            for news in reuters:
                doc_id = news['newid']
                doc = ""

                title = news.find('title')
                if title is not None:
                    doc += title.text
                doc += "\n"

                body = news.find('body')
                if body is not None:
                    doc += body.text
                
                lines = doc.split('\n')[:-2]
                lines.append(doc_id)
                documents.append(lines)

            f.close()



def tokenizeDocument():
    print('hello')

getDocuments()
print(documents[0])

# # print(news_paper[258])
# for i in range(10, 1000, 35):
#     print(news_paper[i][-3:])
# # bodies = news_paper[1].find_all('body')
# # doc_id = news_paper[1]['newid']
# # print(doc_id)
# # for body in bodies:
# #     text = body.get_text()
# #     lines = text.split('Reuter\n\x03')
# #     print(lines)