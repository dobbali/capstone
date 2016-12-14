
# coding: utf-8

# In[1]:
import params as p
import pandas as pd
import numpy as np
import teradata
import getpass
from teradata import DatabaseError



def data_extract():    # In[7]:

    pw=getpass.getpass()
    udaExec = teradata.UdaExec(appName="Database access", version="1.0", logConsole=False)


    # In[8]:

    def query_to_df(query):
        with udaExec.connect(method="odbc", system="POEDW2", authentication="ldap", username="mdobbali",
                                  password=pw) as session:
            df = pd.read_sql(query, session)
        return df


    # In[17]:
    chat_trans = []
    for issue_number in p.all_issues:
        query = "SELECT  a.incdnt_note_desc" + \
                " FROM EDW_ACCESS_VIEWS.incdnt_note a" + \
                " JOIN  EDW_ACCESS_VIEWS.incdnt_catg b ON a.incdnt_id = b.incdnt_id" + \
                " AND b.incdnt_catg_typ_id =" +' '+ issue_number + ' '+ "AND CAST (a.create_dttm AS DATE)" + \
                "  BETWEEN " +'\''+ p.start_date +'\''+ ' AND ' +'\''+ p.end_date +'\''+ " AND a.note_typ_cd = 'INTRNLNT'" + \
                " AND incdnt_note_desc LIKE 'Full Transcript%' SAMPLE" + ' ' + p.sample_size + " ;"

        temp_df = query_to_df(query)
        chat_trans.append(temp_df)
    #Output is list of Dataframes.
    print(query)



    # Send a status message to #manoj
    message ='data extraction complete'
    if p.notification == 'Y':
        p.slack_notify(message)

    # In[18]:

    # In[8]: List of data frames is converted into dataframes of dataframes.
    all_data_labels = pd.DataFrame({'df_issues':chat_trans,'issue_num':p.all_issues})


    # In[19]:

    # In[9]: issue numbers to each chat
    a = 0
    for df in all_data_labels['df_issues']:
        df['issue_number'] = all_data_labels['issue_num'][a]
        a = a + 1


    all_chat_with_issue_num = pd.concat(list(all_data_labels['df_issues']),ignore_index=True)
    print(all_chat_with_issue_num.shape)


    for dictionary in p.issue_list_dict:
        for issue_num in list(dictionary.values())[0]:
            print(issue_num)
            print(list(dictionary.keys())[0])
            all_chat_with_issue_num.loc[all_chat_with_issue_num['issue_number']== str(issue_num), 'issue_name'] = list(dictionary.keys())[0]

    all_chat_with_issue_num.to_excel(p.path+p.output_file_name+'.xlsx')
    message ='data extraction complete and file saved'
    p.slack_notify(message)

    return all_chat_with_issue_num
