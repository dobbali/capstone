
from __future__ import absolute_import
from __future__ import print_function
import re
import operator
import six
from six.moves import range
import datetime
import time
token = 'xoxb-99772612293-4wjEIFbHeK4Q7SgcqWZNn7X5'
from slacker import Slacker
slack = Slacker(token)


debug = False
test = False

def is_number(s):
    try:
        float(s) if '.' in s else int(s)
        return True
    except ValueError:
        return False


def load_stop_words(stop_word_file):

    stop_words = []
    for line in open(stop_word_file):
        if line.strip()[0:1] != "#":
            for word in line.split():  # in case more than one per line
                stop_words.append(word)
    return stop_words


def separate_words(text, min_word_return_size):

    splitter = re.compile('[^a-zA-Z0-9_\\+\\-/]')
    words = []
    for single_word in splitter.split(text):
        current_word = single_word.strip().lower()
        #leave numbers in phrase, but don't count as words, since they tend to invalidate scores of their phrases
        if len(current_word) > min_word_return_size and current_word != '' and not is_number(current_word):
            words.append(current_word)
    return words


def split_sentences(text):

    sentence_delimiters = re.compile(u'[\\[\\]\n.!?,;:\t\\-\\"\\(\\)\\\'\u2019\u2013]')
    sentences = sentence_delimiters.split(text)
    return sentences


def build_stop_word_regex(stop_word_file_path):
    stop_word_list = load_stop_words(stop_word_file_path)
    stop_word_regex_list = []
    for word in stop_word_list:
        word_regex = '\\b' + word + '\\b'
        stop_word_regex_list.append(word_regex)
    stop_word_pattern = re.compile('|'.join(stop_word_regex_list), re.IGNORECASE)
    return stop_word_pattern


def generate_candidate_keywords(sentence_list, stopword_pattern, min_char_length=1, max_words_length=5):
    phrase_list = []
    for s in sentence_list:
        tmp = re.sub(stopword_pattern, '|', s.strip())
        phrases = tmp.split("|")
        for phrase in phrases:
            phrase = phrase.strip().lower()
            if phrase != "" and is_acceptable(phrase, min_char_length, max_words_length):
                phrase_list.append(phrase)
    return phrase_list


def is_acceptable(phrase, min_char_length, max_words_length):

    # a phrase must have a min length in characters
    if len(phrase) < min_char_length:
        return 0

    # a phrase must have a max number of words
    words = phrase.split()
    if len(words) > max_words_length:
        return 0

    digits = 0
    alpha = 0
    for i in range(0, len(phrase)):
        if phrase[i].isdigit():
            digits += 1
        elif phrase[i].isalpha():
            alpha += 1

    # a phrase must have at least one alpha character
    if alpha == 0:
        return 0

    # a phrase must have more alpha than digits characters
    if digits > alpha:
        return 0
    return 1


def calculate_word_scores(phraseList):
    word_frequency = {}
    word_degree = {}
    for phrase in phraseList:
        word_list = separate_words(phrase, 0)
        word_list_length = len(word_list)
        word_list_degree = word_list_length - 1

        for word in word_list:
            word_frequency.setdefault(word, 0)
            word_frequency[word] += 1
            word_degree.setdefault(word, 0)
            word_degree[word] += word_list_degree  #orig.

    for item in word_frequency:
        word_degree[item] = word_degree[item] + word_frequency[item]


    word_score = {}
    for item in word_frequency:
        word_score.setdefault(item, 0)
        word_score[item] = word_degree[item] / (word_frequency[item] * 1.0)

    return word_score


def generate_candidate_keyword_scores(phrase_list, word_score, min_keyword_frequency=1):
    keyword_candidates = {}
    t = 0
    a = 0
    for phrase in phrase_list:
        if min_keyword_frequency > 1:
            if phrase_list.count(phrase) < min_keyword_frequency:
                continue
        keyword_candidates.setdefault(phrase, 0)
        t1 = time.time()
        word_list = separate_words(phrase, 0)
        t2 = time.time()
        candidate_score = 0
        t = t + t2-t1
        a += 1
        for word in word_list:
            candidate_score += word_score[word]
        keyword_candidates[phrase] = candidate_score
    slack.chat.post_message('@manoj', str(t) + ' ' + 'candidate keyword scores')
    print(a)
    return keyword_candidates


class Rake(object):
    def __init__(self, stop_words_path, min_char_length=1, max_words_length=5, min_keyword_frequency=1):
        self.__stop_words_path = stop_words_path
        self.__stop_words_pattern = build_stop_word_regex(stop_words_path)
        self.__min_char_length = min_char_length
        self.__max_words_length = max_words_length
        self.__min_keyword_frequency = min_keyword_frequency

    def run(self, text):
        t1 = datetime.datetime.now()
        sentence_list = split_sentences(text)
        t2 = datetime.datetime.now()
        print(t2-t1)
        slack.chat.post_message('@manoj', str(t2-t1) + ' ' + 'Sentence Split')
        t1 = datetime.datetime.now()
        phrase_list = generate_candidate_keywords(sentence_list, self.__stop_words_pattern, self.__min_char_length, self.__max_words_length)
        t2 = datetime.datetime.now()
        print(t2-t1)
        slack.chat.post_message('@manoj', str(t2-t1) + ' ' + 'candidate keywords generated')

        t1 = datetime.datetime.now()
        word_scores = calculate_word_scores(phrase_list)
        t2 = datetime.datetime.now()
        print(t2-t1)
        slack.chat.post_message('@manoj', str(t2-t1) + ' ' + 'word scores')

        t1 = datetime.datetime.now()
        keyword_candidates = generate_candidate_keyword_scores(phrase_list, word_scores, self.__min_keyword_frequency)
        t2 = datetime.datetime.now()
        print(t2-t1)
        slack.chat.post_message('@manoj', str(t2-t1) + ' ' + 'word scores + phrase list')

        t1 = datetime.datetime.now()
        sorted_keywords = sorted(six.iteritems(keyword_candidates), key=operator.itemgetter(1), reverse=True)
        t2 = datetime.datetime.now()
        print(t2-t1)
        slack.chat.post_message('@manoj', str(t2-t1) + ' ' + 'sorting done')


        return sorted_keywords


if test:
    text = "Compatibility of systems of linear constraints over the set of natural numbers. Criteria of compatibility of a system of linear Diophantine equations, strict inequations, and nonstrict inequations are considered. Upper bounds for components of a minimal set of solutions and algorithms of construction of minimal generating sets of solutions for all types of systems are given. These criteria and the corresponding algorithms for constructing a minimal supporting set of solutions can be used in solving all the considered types of systems and systems of mixed types."

    # Split text into sentences
    sentenceList = split_sentences(text)
    #stoppath = "FoxStoplist.txt" #Fox stoplist contains "numbers", so it will not find "natural numbers" like in Table 1.1
    stoppath = "RAKE/SmartStoplist.txt"  #SMART stoplist misses some of the lower-scoring keywords in Figure 1.5, which means that the top 1/3 cuts off one of the 4.0 score words in Table 1.1
    stopwordpattern = build_stop_word_regex(stoppath)

    # generate candidate keywords
    phraseList = generate_candidate_keywords(sentenceList, stopwordpattern)

    # calculate individual word scores
    wordscores = calculate_word_scores(phraseList)

    # generate candidate keyword scores
    keywordcandidates = generate_candidate_keyword_scores(phraseList, wordscores)
    if debug: print(keywordcandidates)

    sortedKeywords = sorted(six.iteritems(keywordcandidates), key=operator.itemgetter(1), reverse=True)
    if debug: print(sortedKeywords)

    totalKeywords = len(sortedKeywords)
    if debug: print(totalKeywords)
    print(sortedKeywords[0:(totalKeywords // 3)])

    rake = Rake("SmartStoplist.txt")
    keywords = rake.run(text)
    print(keywords)
