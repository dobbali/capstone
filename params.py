# Notification settings
notification ='Y'
token = 'xoxb-99772612293-4wjEIFbHeK4Q7SgcqWZNn7X5' # Developer token for Slack
from slacker import Slacker
slack = Slacker(token)

def slack_notify(message, name = '@manoj'):
    
    if name:
        return slack.chat.post_message(name, message)

#Query Settings

start_date = '2015-10-01'
end_date = '2015-12-31'
sample_size = '100'

#Data Set
tracking = [2,187, 183,657, 174, 161, 660, 656, 186 ]
refund = [173, 1, 1282, 333]
international = [358]
account = [188, 189, 5]
missing_parts = [168]
coupon = [120, 406, 1020, 124]
store_card = [1021]
mastercard = [145]
payment = [4]
orders = [3,408,745,908,789, 746,774,747,748,749,750,429,775,764,912,470,711,751]
clubo =[620]

###issue_list_dict = [{'tracking':tracking}, {'refund':refund}, {'international':international}, {'account':account}, {'missing_parts':missing_parts}, {'coupon':coupon}, {'store_card':store_card}, {'mastercard':mastercard}, {'payment':payment}, {'orders':orders},{'clubo':clubo}]
issue_list_dict = [{'clubo':clubo},{'international':international}]
output_file_name = 'club_international.xlsx' # Change output file name here
###all_issues = tracking + refund + international + account + missing_parts + coupon + store_card + mastercard + payment + orders + clubo
all_issues = clubo + international
all_issues = [str(issue_number) for issue_number in all_issues]

#Keyword Extraction
path = '/Users/mdobbali/Google Drive/Overstock/Projects/cs_text_classification/Final_Code/Data_Files/'
output = 'ind'
 # if you want individual issue keywords try 'combined' else 'ind'
issue_name = 'issue'

#Clearning and algorithm selection
custoragent = 'customer' # 'agent' or 'cust'
tf_idf_or_rake = 'rake'
min_word_phrase_len = 4
min_word_len = 4
freq = 6
frac = 0.3
