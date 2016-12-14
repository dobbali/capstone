#import glob # glob module finds all the pathnames matching a specified pattern
import pandas as pd
#from openpyxl import Workbook
#import xlrd
import re


def get_chat(Chat_Transcript,agentORcust):

    nameofAgent = re.findall('Hi, my name is (.*?)\. How may I help you?',Chat_Transcript,flags=re.IGNORECASE)
    list_nameofCust = re.findall(']\ (.*?):',Chat_Transcript)
    cust_name = [item for item in set(list_nameofCust) if item not in nameofAgent]
    if agentORcust == 'agent':
        temp_totalChat_agent = []
        for items in nameofAgent:
            regexforchat = re.compile('%s:(.*?)\['%items)
            chatofAgent = re.findall(regexforchat,Chat_Transcript)
            temp_totalChat_agent.append(chatofAgent)
        totalChat = []
        for item in temp_totalChat_agent:
            totalChat = totalChat + item

    elif agentORcust == 'customer':
        for items in cust_name:
            if len(items) < 38 and len(items) > 3 and 'currently' not in items and 'Coupon' not in items:
                regexforchat = re.compile('%s:(.*?)\['%items)
                totalChat = re.findall(regexforchat,Chat_Transcript)

    else:
        print("invalid parameters")
    return totalChat

def get_chat_df(Chat_Transcript_df,column_name,agentORcust):

    Chat = []
    for chats in Chat_Transcript_df[column_name]:
        try:
            Chat.append(get_chat(chats,agentORcust))
        except:
            if len(chats) >100:
                Chat.append('EN')
            else:
                Chat.append('No chat')
    return Chat


def combine_list_of_items(list_of_items, withchar):

    return withchar.join(map(str, list_of_items))


def combine_chat(Chat_Transcript):
    try:
        agent_sentences = sep_chats(Chat_Transcript, 'agent')
        cust_sentences = sep_chats(Chat_Transcript,'customer')
    except:
        agent_sentences = ['ignore']
        cust_sentences = ['ignore']

    merge_chat = agent_sentences+cust_sentences
    return merge_chat


def issue_chat_to_para(data_frame,column_name,issue_names):
    all_sentences_cust_coupon = []
    for items in combinedData_sample[data_frame[column_name]==issue_names]['cust_Chat']:
        all_sentences_cust_coupon += items
    return (all_sentences_cust_coupon)

"""

def export_chat_a
dnew ={}
for item in set(combinedData_sample['File_Name']):
    dnew["string_{0}".format(item)]= keywords_output(item)
"""
