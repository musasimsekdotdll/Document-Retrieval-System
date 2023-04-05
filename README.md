# A Simple Search System for Phrase and Proximity Queries

This project is written in Python 3.10.10. Since I used only built-in libraries in the project, correct version of the Python is enough to run the scripts.


## Before Running
To be able to run the preprocessor so the dictionary, inverted index, stopwords, etc. can be created, Reuters-21578 data set(all _.sgm_ files like _reut2-000.sgm_) should be in a folder named _reuters21578_. That folder should be in the same directory with _preprocessor.py_ and _query_processor.py_. 


## How to Run
Open a terminal in your computer and navigate to the project folder. In order to run the preprocessor, type in the terminal simply:
```
python3.10 preprocessor.py
 ```
 
 Wait until the code terminates. After the code terminates, you will realize that some new files are created in the project folder. Those files are used in query processor.

Similar with preprocessor, type the following command in your terminal to run the query processor:
```
python3.10 query_processor.py
 ```

After you hit the enter, you will see that the terminal is waiting your input. Type your query in the specified format. As an example, if you want to search the phrase query 'demand totalled', type the following in your open terminal:
```
"demand totalled"
 ```
Similarly, if you want to search a proximity query 'stop 2 flow', type the following command in your open terminal
```
stop 2 flow
 ```

If you want to end the query processor, type just a dot and hit the enter button:
```
.
 ```