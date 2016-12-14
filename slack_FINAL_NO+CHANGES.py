#slack
# coding: utf-8

# In[9]:

import params as p
import pandas as pd
import datetime
import pandas as pd
import re
from string import punctuation
import re
import rake
import data_aggregate as da
import Rake_TF_IDF_Cleansing as bc
import data_collection as dc
import time
import sys
from slackclient import SlackClient
from slacker import Slacker
print('libraries imported')
token ='xoxb-106983742324-cOVmqpTClEVkIpwcHxGY7x0X'
slack = Slacker(token)
sc = SlackClient(token)


# In[10]:

combinedData_all_init = pd.read_excel("/Users/mdobbali/Google Drive/Overstock/Projects/cs_text_classification/Capstone_Demo/Data_Files/input_file.xlsx")


# In[12]:

def slack_notify(message, name = '@textract'):

    if name:
        return slack.chat.post_message(name, message)


# In[13]:

path = "/Users/mdobbali/Google Drive/Overstock/Projects/cs_text_classification/Capstone_Demo/Data_Files/"


# In[14]:

def prod_key_word(inputlist):
    writer = pd.ExcelWriter('Keyword_Extract.xlsx')
    for issue in inputlist:
        df = pd.read_excel(path + issue + ".xlsx")
        df.to_excel(writer, issue)
    writer.save()


# In[26]:

def textract(channel,issue_name_list):

    df_issue_list = []
    for issue_name in issue_name_list:
        tempdf = combinedData_all_init.loc[combinedData_all_init['issue_name'] == issue_name]
        df_issue_list.append(tempdf)

    combinedData_all = pd.concat(df_issue_list)

    combinedData_sample = combinedData_all.sample(frac= 1)
    combinedData_sample = combinedData_sample.rename(index = str, columns={'incdnt_note_desc':'Chat','issue_name':'File_Name'})
    if p.output == 'combined':
        combinedData_sample['File_Name'] = 'issue'

    combinedData_sample.drop(combinedData_sample.columns[[1]], axis=1, inplace=True)

    message = 'Basic cleaning on data is done'
    #t1 = datetime.datetime.now()
    clean_df_rake = bc.basic_cleaning(combinedData_sample,'Chat',p.tf_idf_or_rake )
    sc.api_call("chat.postMessage", channel=channel,text=message, as_user=True)

    message = 'Extracting customer chat in a list '
    clean_df_rake['cust_chat'] = da.get_chat_df(clean_df_rake,'Chat',p.custoragent)
    sc.api_call("chat.postMessage", channel=channel,text=message, as_user=True)

    message = 'Identified and removed address from Chat transcripts'
    clean_df_rake['cust_chat'] = [bc.strip_address(lines,'/Users/mdobbali/Google Drive/Overstock/Projects/cs_text_classification/Capstone_Demo/Data_Files/state_names.txt') for lines in clean_df_rake['cust_chat']]
    sc.api_call("chat.postMessage", channel=channel,text=message, as_user=True)

    message = 'Removed One word sentences'
    clean_df_rake['cust_chat'] = [bc.get_one_word(lines) for lines in clean_df_rake['cust_chat']]
    sc.api_call("chat.postMessage", channel=channel,text=message, as_user=True)

    message = 'Removed Numbers'
    clean_df_rake['cust_chat'] = [bc.strip_numbers_list(lines) for lines in clean_df_rake['cust_chat']]
    sc.api_call("chat.postMessage", channel=channel,text=message, as_user=True)

    message ='Customer Chat in a Paragraph'
    clean_df_rake['cust_chat'] = [da.combine_list_of_items(chat,'') for chat in clean_df_rake['cust_chat']]
    sc.api_call("chat.postMessage", channel=channel,text=message, as_user=True)

    message = 'Customer Chat in a Single Paragraph for each issue'
    just_chat = da.combine_list_of_items(list(clean_df_rake['cust_chat']),'')
    sc.api_call("chat.postMessage", channel=channel,text=message, as_user=True)

    message = "Rake Cleaning done"
    dnew ={}
    for item in set(clean_df_rake['File_Name']):
        list_of_chat = list(clean_df_rake[clean_df_rake['File_Name'] == item]['cust_chat'])
        dnew["{0}".format(item)]= da.combine_list_of_items(list_of_chat,'')
    sc.api_call("chat.postMessage", channel=channel,text=message, as_user=True)

    df_issues = pd.DataFrame.from_dict(dnew, orient='index', dtype=None)
    df_issues = df_issues.rename(index=str, columns={ 0 : "Chat_Para_Customer"})

    if p.output == 'ind':
        issue_list_names = list(set(clean_df_rake['File_Name']))
    else:
        issue_list_names = ['issue']
    print(len(issue_list_names))

    rake_object = rake.Rake(p.path + "SmartStoplist.txt",p.min_word_len, p.min_word_phrase_len, p.freq)

    writer = pd.ExcelWriter('Data_Files/Keyword_Extracted_R.xlsx')
    for item in issue_list_names:
        t1 = datetime.datetime.now()
        sc.api_call("chat.postMessage", channel=channel,text='Rake process started for ' + str(item), as_user=True)
        chat_para = df_issues.loc[[item]]['Chat_Para_Customer'][0]
        keywords_tuples = rake_object.run(chat_para)
        df = pd.DataFrame(keywords_tuples)
        df.to_excel(writer,str(item))
        #df.to_excel( str(item) + '.xlsx')
        t2 = datetime.datetime.now()
        message = 'rake is done'
        sc.api_call("chat.postMessage", channel=channel,text= message + " for "+ str(item), as_user=True)
    writer.save()


# In[27]:

# starterbot's ID as an environment variable
BOT_ID = "U34UXMU9J"

# constants
AT_BOT = "<@" + BOT_ID + ">"
print(AT_BOT)
EXAMPLE_COMMAND = "do"
date_pattern = re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}(,| |, )[0-9]{4}-[0-9]{2}-[0-9]{2}')
x = 27429

greeting_list = ['hi','hello','are you there?','what can you do?','what do you do?','who are you?']
size_sample = re.compile('^-?[0-9]+$')
issues_list = "Accessing_Account | ClubO | Coupon|"         +"International | Master_Card |"         +"Missing_Parts | Orders |"         +"Payments | Refund | Store_Card | Tracking"


issues_list = [item.strip() for item in issues_list.split("|")]
issues_list = [item.lower() for item in issues_list]

def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "Not sure what you mean.I am not that smart, YET. \nIf you want to know legal commands, Try legal commands"
    attach = None

    if command.lower() in greeting_list:
        response = "Hi, I am Textrat. I can do Keyword extraction.\nPlease enter start date and end date of data to be extracted seperated by comma"
        attach = [
                             {
                                            "fallback": "Required plain-text summary of the attachment.",
                                            "color": "#f74f40",
                                            "pretext": "Here are few details about algorithm",
                                            "author_name": "Manoj and Deepthi",
                                            "title": "Keyword Extraction",
                                            "text": "This will extract keywords from the data provided ",
                                            "fields": [
                                                {
                                                    "title": "Parameters requried",
                                                    "value": "Date Range(YYYY-MM-DD),Sample size, issues",
                                                    "short": False
                                                }
                                            ]
                                        }
                                    ]

    if bool(date_pattern.match(command)):
        date = command.split(',')
        start_date = date[0]
        end_date = date[1]
        response ="will extract data for "+str(start_date)+", "+str(end_date)+" What is the sample size that you want me to consider?"
        attach = None

    if bool(size_sample.match(command)):
        frac_num = (int(command) / 22429)

        response = "Will extract data for requested sample size "

        attach = [
                                        {
                                            "fallback": "Required plain-text summary of the attachment.",
                                            "color": "#f74f40",
                                            "pretext": "These are the issues available",
                                            "title": "List of Issues",
                                            "text": "Accessing_Account | ClubO | Coupon|\n" \
        +"International | Keyword_Extracted | Master_Card |\n" \
        +"Missing_Parts | Orders|\n" \
        +"Payments | Refund |Store_Card | Tracking\n"
        +"Select one or more issues seperated by comma",
                                            "fields": [
                                                {
                                                    "title": "Select one or more issues",
                                                    "value": "Eg: ClubO,Coupon,Orders,Refund",
                                                    "short": False
                                                }
                                            ]
                                        }
                                    ]





    issues_list_set = set(issues_list)
    command_list_set = set(command.split(","))
    if command_list_set.issubset(issues_list_set):
        textract(channel,command.split(","))
        print("text extraction done")
        response = "Keyword Extraction is DONE"
        prod_key_word(command.split(","))
        file_ad = "/Users/mdobbali/Google Drive/Overstock/Projects/cs_text_classification/Capstone_Demo/Keyword_Extract_R.xlsx"
        slack.files.upload(file_ad, channels=channel)

    if command == "legal commands":
        response = "There are the legal commands \n Hi \nHello,Are you there? \nWho are you? \nWhat do you do? \nWhat can you do?"
        attach = None



    sc.api_call("chat.postMessage", channel=channel,attachments = attach
                          ,text=response, as_user=True)

def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                print(output['text'])
                print(channel)
                return output['text'].split(AT_BOT)[1].strip().lower(),                        output['channel']
    return None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if sc.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel = parse_slack_output(sc.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
