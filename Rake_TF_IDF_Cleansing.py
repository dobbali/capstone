#from openpyxl import Workbook # Workbook is a class object; a container for all other parts of the document
#import os # Operating System dependent module
import pandas as pd
import numpy as np
import re
#import pprint
from string import punctuation
#from sklearn.feature_extraction.text import CountVectorizer
#from nltk.tokenize import RegexpTokenizer
from stop_words import get_stop_words
#from nltk.stem.porter import PorterStemmer
import pandas as pd
import re
#from sklearn.preprocessing import MinMaxScaler
from nltk.corpus import stopwords
#import glob # glob module finds all the pathnames matching a specified pattern
#from collections import Counter
import rake
#import operator


#email id and links removal
def remove_link_email(text_with_email_links):
    no_email_text =re.sub('\<a.*?</a>','',text_with_email_links, flags=re.DOTALL)
    link_regex = re.compile(r'(?:(http://)|(www\.))(\S+\b/?)([!"#$%&\'()*+,\-./:;<=>?@[\\\]^_`{|}~]*)(\s|$)', re.I)
    no_email_no_link_text = link_regex.sub('',no_email_text)
    return re.sub(r'[\w\.-]+@[\w\.-]+','', no_email_no_link_text)

def basic_cleaning(chat_transcript_df, column_name, time_stamps_name_remove):

	"""
    Utility function to load stop words from a file and return as a list of words
    @param Dataframe with Chat Transcripts, Column name as string and 'Y' if you want names and to be remove
    @return list A list of stop words.
    """
	#Everything to Lowercase
	chat_transcript_df[column_name] = [chat.lower() for chat in chat_transcript_df[column_name]]

	#Replace few words/symbols/sentence in "whole" dataframe'
	#remove_exact_appearences
	remove_words = {'Data/CT' : '','<br>':'','<div>':'','</div>':'',
				'span':'','<br />':'','&#39;' : "",'&quot;':"",'&amp;':'',
				'  ':'','&nbsp;':'','club o':'clubO', 'Full Transcript (includes private messages) --------------------------------------------':''}

	chat_transcript_df = chat_transcript_df.replace(remove_words, regex= True)

	#Replace items with exact Regex match
	#remove_regex_matches = re.compile("full transcript(.*?)\-- ",flags = re.I)
	#chat_transcript_df[column_name] = [remove_regex_matches.sub('',chat_transcript) for chat_transcript in chat_transcript_df[column_name]]

	#Get rid of text after these phrases
	remove_content_after_these_phrases_regex = re.compile("\\b(thank you for contacting overstock(.*)\).|need a gift right now(.*)\ Click here for more details.|our chat reference number(.*)|have i address(.*)|have i answe(.*))\\W",flags=re.I)
	chat_transcript_df[column_name] = [remove_content_after_these_phrases_regex.sub("",chat_transcript) for chat_transcript in chat_transcript_df[column_name]]

	#email id and links removal
	chat_transcript_df[column_name] = [remove_link_email(chat) for chat in chat_transcript_df[column_name]]

	if time_stamps_name_remove == 'tf_idf':
		chat_transcript_df[column_name] = [re.sub('\[.*?\: ', '', chat) for chat in chat_transcript_df[column_name]]
		chat_transcript_df[column_name] = [re.sub('\[.*?\]', '', chat) for chat in chat_transcript_df[column_name]]

	else:
		print("names and time stamps have not been removed")


	#time stamp and name removal

	return chat_transcript_df

def strip_punctuation(s):
    return ''.join(c for c in s if c not in punctuation)

def strip_stopwords(s,toremove_set):
    return ' '.join(word for word in [i for i in s.lower().split() if i not in toremove_set])

def strip_numbers(s):
    return re.sub('[0-9]*','',s)

def strip_numbers_list(sent_list):
    no_num = []
    for sent in sent_list:
        no_num.append(re.sub('[0-9]*','',sent))
    return no_num


def load_stop_words(stop_word_file):

    stop_words = []
    for line in open(stop_word_file):
        if line.strip()[0:1] != "#":
            for word in line.split():  # in case more than one per line
                stop_words.append(word)
    return stop_words

def combine_list_of_items(list_of_items, withchar):

    return withchar.join(map(str, list_of_items))

def strip_address(list_of_sentences_with_address,state_names):
    states_short_full = load_stop_words(state_names)
    regex_states = [state.lower()+'(,|, |  | |\.)[0-9]{1,5}'for state in states_short_full]
    states_short_full_regex = combine_list_of_items(regex_states,'|')
    newlist = []
    big_state_regex = re.compile(states_short_full_regex, flags = re.I)
    for sent in list_of_sentences_with_address:
        addornot = re.search(big_state_regex, sent)
        if addornot is None:
            newlist.append(sent)
    return newlist

def get_one_word(list_of_chat):
    one_word_list = []
    more_word_list = []
    for item in list_of_chat:
        item = item.strip()
        new_item = item.split(' ')
        if len(new_item) == 1:
            one_word_list.append(item)
        else:
            more_word_list.append(item)
    return more_word_list

"""

def remove_bp_phrases_words(phrases):

    pattern = re.compile("\\b(wonderful|you have a very good taste|appreciate your business|appreciate your interest|valued new customer|first time customer|appreciate your valuable business|my name is|avoid our chat|uses of clubO are|visitor is|other concern|is this for the|shows information after your|contact number|account information|we will call or email you to follow-up within 1-2 business days|verifying your|please verify|how may i help|addressed all|referring to|privileged|would be happy to assist you with that|i would be happy to assist you today|thank you for being a valued customer of overstock|acknowledge|your day|billing address|patience|i hope this information is helpful to you|have the item number|apologize|thanks for|is there any change in the shipping address|valued customer like|leave a note on your account|is there any change in your shipping address|in addition to this you will be contacted by one of our specialized representative within 1-2 business days via email or over the phone|happy to help|disconnect|disappointment|order confirmation number|contact detail|email address|please be online|via email or phone|resolved all|chat reference number|how are|perfect! thank you for confirming|standard return policy|security purposes|welcome|great day|<a target|good morning|overstock.com|good evening|good aft|be glad to check and help you with the information|click here|feedback|bye|have i|how may i help|until disconnect|for security purposes)\\W",re.I)    #pattern = re.compile("\\b(of|the|in|for|at)\\W", re.I)
    return [phrase for phrase in phrases if pattern.search(phrase) is None]



def remove_bp_exact_phrases(phrases):


	Utility funciton to replace phrase with space
    @param list of phrases
    @return list without mentioned phrases


    pattern = re.compile("\\b(i am happy to assit you|confirmation|i am sorry|approximately|seconds|currently|visitor|for staying online|thank you|thanks|sorry|apologize|disappoint|email address|i am so sorry that i have not heard from you! as i have not received a response, our chat will now be disconnected|if you need further assistance please feel free to contact us back and we will be more than happy to assist you|have a wonderful rest of your day!|i am happy to assist \xa0you|\xa0|\xa0have i addressed your concerns for today|thank you|i apologize for the inconvenience this has caused to you|i do understand, and i apologize for the inconvenience this has caused to you|i understand and i apologize for the inconvenience this has caused to you|i apologize for the inconvenience this has caused to you|i apologize for the inconvenience this has caused to you|&nbsp;let me check and help you with this further|i apologize for the inconvenience this has caused to you|let me check and help you with this further|thank you so much|could you please copy and paste the|let me check your account and help you with the current order status|let me check and help you|i have initiated a trace with|have initiated trace|i will initiate a trace with|i will initiated a trace with|fedex|ups|dhl|usps|i'm sorry to know that|i'm sorry to hear that|i will help you with|i'll be glad to check and help you with|i am extremely sorry to hear that|i will be happy to assit you|item#|may i have the item number you wish to purchase)\\W",re.I)    #pattern = re.compile("\\b(of|the|in|for|at)\\W", re.I)
    return [pattern.sub("",phrase) for phrase in phrases]

"""
