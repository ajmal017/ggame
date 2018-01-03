# -*- coding: utf-8 -*-

from ib_insync import *
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np

def xml2df(xml_data):
    root = ET.XML(xml_data) # element tree
    all_records = [] #This is our record list which we will convert into a dataframe
    for i, child in enumerate(root): #Begin looping through our root tree
        record = {} #Place holder for our record
        for subchild in child: #iterate through the subchildren to user-agent, Ex: ID, String, Description.
            record[subchild.tag] = subchild.text #Extract the text create a new dictionary key, value pair
            all_records.append(record) #Append this record to all_records.
    return pd.DataFrame(all_records) #return records as DataFrame

def xml2df2(xml_data):
    parsed_xml_root = ET.XML(xml_data) # element tree
    dfcols = ['Date', 'period','Revenue']
    df_xml = pd.DataFrame(columns=dfcols)
    for i, child in enumerate(parsed_xml_root):
        for node in child:
            period = node.attrib.get('period')
            if period == '12M':
                continue;
            Date = node.attrib.get('asofDate')
            Revenue = node.text
 
            df_xml = df_xml.append(
                pd.Series([Date, period, Revenue], index=dfcols),ignore_index=True)
    return df_xml

def is_commpany_inside_tonrado(revenue_data):
    temp = 0
    for row in revenue_data.itertuples():
        val =float(row.Revenue)
        if val == 0:
            return 0
        if temp == 0:
            temp = val
            continue
        if temp/val > 1.1:
            temp = val
            continue
        else:
            return 0
    return 1 

def get_company_summary(name):
    contract = Stock(name,'SMART','USD')
    Summary = ib.reqFundamentalData(contract, 'ReportsFinSummary', None)
    #Snap = ib.reqFundamentalData(contract, 'ReportSnapshot', None)
    #Finance = ib.reqFundamentalData(contract, 'ReportsFinStatements', None)#
    return xml2df2(Summary)    

# read stock symbol list to pandas df object
nyse_symbol = pd.read_table('./data/NYSE.txt', delim_whitespace=True, names=('name', 'description'))
nasdaq_symbol = pd.read_table('./data/NASDAQ.txt', delim_whitespace=True, names=('name', 'description'))
players = pd.concat([nyse_symbol, nasdaq_symbol], ignore_index=True)
ggcandidate = []

# Todo: remove sybmol with "-" or "."

# connect to IB
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)

# enumrate stock symbol and build contract for look up
for row in nyse_symbol[1:].itertuples():
    if ('-' in row.name) or ('.' in row.name):
        continue
    print (row.name)
    try:
        Summary_df = get_company_summary(row.name)
    except Exception:
        continue
    if Summary_df.shape[0] < 4:
        continue
    if is_commpany_inside_tonrado(Summary_df[0:6]):
        ggcandidate.append(row.name)
        
# caculate revenuegrowth rate in the last 6 quarters
# if every quarter gain signifcant increasement (>20%)
# {
#    check gross margin
#    check profit margin
#    check debt ratio
#    check free cashflow
#    check working captial
#    check market share
#    analyze 5 force
#    analyze S curve
#    analyze technology adoption cycle stage
#    analyze switching cost / architecture privacy (competency advantage)
#    check managment team credential
#    put it into the candidate list if it is a gorilla or king
#    review every quarter to qualify maximum 8 candidates across 4 segment only 
# } 

# exit
ib.disconnect()



