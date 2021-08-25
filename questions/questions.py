import nltk
import sys
import os
import string
import math

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    contents = dict()
    for (dirpath, dirnames, filenames) in os.walk(directory):
        for item in filenames:
            with open(os.path.join(dirpath, item), 'r', encoding='utf-8') as f:
                contents[str(item)] = f.read()
    return contents


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    punctuation = string.punctuation
    stop = nltk.corpus.stopwords.words("english")
    words = nltk.word_tokenize(document.lower())
    output = list()

    for word in words:
        if word not in punctuation and word not in stop:
            output.append(word)
    return output


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    # Dict mapping 'word' to how many times it appears across documents
    frequency = dict()
    for item in documents:
        known_words = set()
        for word in documents[item]:
            if word not in known_words:
                known_words.add(word)
                try:
                    frequency[word] += 1
                except KeyError:
                    frequency[word] = 1

    # Dict mapping 'words' to their respective 'idf value'
    word_idf = dict()
    for word in frequency:
        word_idf[word] = math.log(len(documents) / frequency[word])
    return word_idf

def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    f_scores = dict()
    for f, words in files.items():
        tf_idf = 0
        for word in query:
            tf_idf += words.count(word) * idfs[word]
        f_scores[f] = tf_idf

    # Return a list with 'f_scores' sorted according to tf-idf
    sort = sorted(f_scores.items(), key=lambda x : x[1], reverse=True)
    # Generate a ordered list containing the 'filenames' in order
    rank = [i[0] for i in sort]
    return rank[:n]


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    scores = dict()
    for sentence, words in sentences.items():
        # idf value of sentence
        score = 0
        for word in query:
            if word in words:
                score += idfs[word]
        # Query term density of sentence
        density = sum([words.count(x) for x in query]) / len(words)
        scores[sentence] = (score, density)

    sort = sorted(scores.items(), key=lambda x: (x[1][0], x[1][1]), reverse=True)
    rank = [k for k, v in sort]
    return rank[:n]


if __name__ == "__main__":
    main()
