
# coding: utf-8
import params as p
import pandas as pd
import datetime
from openpyxl import Workbook # Workbook is a class object; a container for all other parts of the document
#import os # Operating System dependent module
import pandas as pd
#import numpy as np
import re
#import pprint
from string import punctuation
#from sklearn.feature_extraction.text import CountVectorizer
#from nltk.tokenize import RegexpTokenizer
from stop_words import get_stop_words
#from nltk.stem.porter import PorterStemmer
#from gensim import corpora, models
#mport gensim
import pandas as pd
import re
#from sklearn.preprocessing import MinMaxScaler
from nltk.corpus import stopwords
#import glob # glob module finds all the pathnames matching a specified pattern
#from collections import Counter
import rake
#import operator
import data_aggregate as da
import Rake_TF_IDF_Cleansing as bc
import data_collection as dc
#import pandas as pd
#import numpy as np
import teradata
import getpass
from teradata import DatabaseError
print('libraries imported')

# In[3]:

t1 = datetime.datetime.now()
#Point path to an excel file with chat transcripts
combinedData_all = dc.data_extract()
print('import done')
t2 = datetime.datetime.now()
print(t2 - t1)

#Comment one of the following
#output = 'combined' # if you want keywords related to all issues ;
#output = 'ind' # if you want individual issue keywords

issue_name = 'issue'
custoragent = 'customer'
#tf_idf_or_rake = 'rake' #No or Yes

#min_word_phrase_len = 4
#min_word_len = 4
#freq = 6
# In[6]:

combinedData_sample = combinedData_all.sample(frac= p.frac)
combinedData_sample = combinedData_sample.rename(index = str, columns={'incdnt_note_desc':'Chat','issue_name':'File_Name'})
if p.output == 'combined':
    combinedData_sample['File_Name'] = 'issue'

combinedData_sample.drop(combinedData_sample.columns[[1]], axis=1, inplace=True)


message = 'basic cleaning on data is done'
t1 = datetime.datetime.now()
clean_df_rake = bc.basic_cleaning(combinedData_sample,'Chat',p.tf_idf_or_rake )
t2 = datetime.datetime.now()
print(t2 - t1)
p.slack_notify( str(t2 - t1) + ' ' + message)

message = 'extracting customer chat in a list '
t1 = datetime.datetime.now()
clean_df_rake['cust_chat'] = da.get_chat_df(clean_df_rake,'Chat',p.custoragent)
t2 = datetime.datetime.now()
print('customer chat in list ')
print(t2 - t1)
p.slack_notify( str(t2 - t1) + ' ' + message)


message = 'getting rid of address'
t1 = datetime.datetime.now()
clean_df_rake['cust_chat'] = [bc.strip_address(lines,'/Users/mdobbali/Google Drive/Overstock/Projects/cs_text_classification/Final_Code/Data_Files/state_names.txt') for lines in clean_df_rake['cust_chat']]
t2  = datetime.datetime.now()
print('got rid of address ')
print(t2 - t1)
p.slack_notify( str(t2 - t1) + ' ' + message)


message = 'getting rid of one word sentences'
t1 = datetime.datetime.now()
clean_df_rake['cust_chat'] = [bc.get_one_word(lines) for lines in clean_df_rake['cust_chat']]
print('got rid of one word sentences ')
t2 = datetime.datetime.now()
print(t2 - t1)
p.slack_notify( str(t2 - t1) + ' ' + message)


message = 'stiriping numbers'
t1 = datetime.datetime.now()
clean_df_rake['cust_chat'] = [bc.strip_numbers_list(lines) for lines in clean_df_rake['cust_chat']]
t2 = datetime.datetime.now()
print(t2 - t1)
p.slack_notify( str(t2 - t1) + ' ' + message)


message ='customer chat in a paragraphs'
t1 = datetime.datetime.now()
clean_df_rake['cust_chat'] = [da.combine_list_of_items(chat,'') for chat in clean_df_rake['cust_chat']]
t2 = datetime.datetime.now()
print(t2 - t1)
p.slack_notify( str(t2 - t1) + ' ' + message)

message = 'customer chat in a single para issue level'
t1 = datetime.datetime.now()
just_chat = da.combine_list_of_items(list(clean_df_rake['cust_chat']),'')
t2 = datetime.datetime.now()
print(t2 - t1)
p.slack_notify( str(t2 - t1) + ' ' + message)


t1 = datetime.datetime.now()
dnew ={}
for item in set(clean_df_rake['File_Name']):
    list_of_chat = list(clean_df_rake[clean_df_rake['File_Name'] == item]['cust_chat'])
    dnew["{0}".format(item)]= da.combine_list_of_items(list_of_chat,'')
t2 = datetime.datetime.now()
print(t2 - t1)
p.slack_notify( str(t2 - t1) + ' ' + message)

df_issues = pd.DataFrame.from_dict(dnew, orient='index', dtype=None)

df_issues = df_issues.rename(index=str, columns={ 0 : "Chat_Para_Customer"})

if p.output == 'ind':
    issue_list_names = list(set(clean_df_rake['File_Name']))
else:
    issue_list_names = ['issue']
print(len(issue_list_names))
#issue_list_names = list(set(clean_df_rake['File_Name']) - set(['mastercard','coupon','store_card','orders']))

rake_object = rake.Rake(p.path + "SmartStoplist.txt",p.min_word_len, p.min_word_phrase_len, p.freq)

writer = pd.ExcelWriter(p.path+p.output_file_name+'Keyword_Extracted.xlsx')
for item in issue_list_names:
    t1 = datetime.datetime.now()
    print(item)
    message = 'rake started'
    p.slack.chat.post_message('@manoj', 'rake process started for ' + str(item) + ' at ' + str(t1))
    chat_para = df_issues.loc[[item]]['Chat_Para_Customer'][0]
    keywords_tuples = rake_object.run(chat_para)
    df = pd.DataFrame(keywords_tuples)
    df.to_excel(writer,str(item))
    #df.to_excel( str(item) + '.xlsx')
    t2 = datetime.datetime.now()
    message = 'rake is done'
    p.slack_notify( str(t2 - t1) + ' ' + message)
writer.save()

#writer = pd.ExcelWriter('Keyword_Extracted.xlsx')
#for chat_issue in clean_df_rake['File_Name']:
#    temp_df.to_excel(writer,'sheet name')
