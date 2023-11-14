import csv
import numpy as np
import pandas as pd
import pprint as pp
import json
import requests
import re
from pickleshare import stat
from ast import Pass
from bs4 import BeautifulSoup


def data_parser(fin):
  """
  Clean HPI dataset and output aggregated data for each state.

  :param fin: the input filename for the HPI dataset
  """
  
  with open(fin) as f1:
    # Opening Dataset as Pandas DataFrame
    dataset = pd.read_csv(fin, delimiter = ',')

    # INCONSISTENCY #1 : Many rows have missing 'index_sa' values.
    # 
    # While we could simply just use the 'index_nsa' values, the seasonally
    # adjusted 'index_sa' values are more accurate. 
    # 
    # Therefore, to adjust for this inconsistency, we will relace 'index_nsa' 
    # values with 'index_sa' values where 'index_sa' exist. After, we will rename
    # the remaining 'index_nsa' column to 'index' to display the existing changes.

    dataset['index_nsa'] = np.where(~np.isnan(dataset['index_sa']), dataset['index_sa'], dataset['index_nsa'])
    dataset.drop('index_sa', axis = 1, inplace = True)
    dataset.rename(columns = {'index_nsa' : 'index'}, inplace = True)


    # INCONSISTENCY #2 : The 'place_id' column holds both strings and string-casted ints as potential values.
    # Typically, the numeric 'place_id's are zip codes, and the alphabetic ones are region or state abbreviations.
    # 
    # Since we cannot use both state and city- / region-specific data, we must first decide which of these data 
    # are more important for our analysis. Due to the nature of our other datasets and our final comparative analysis, 
    # we will ultimately make the decision to use the state data to adjust for this inconsistency.
    # 
    # To successfully determine which data is state data, we must essentially find which 'place_id's are
    # state abbreviations. One approach could be to create a list of the 50 state name abbreviations, but 
    # this seems very inefficient with 50*n comparisons being made (where n is the number of rows within our
    # altered dataset). Another approach is to remove those entries which are numerical, and then remove those
    # entries which are longer than 2 characters. Finally, we will make sure to remove the two outlier entries,  
    # 'DC' (District of Columbia) and 'PR' (Puerto Rico), as these territories are not considered to be states in our analysis. This will result 
    # in a maximum of n*(2+k) comparisons, where k is the number of 2-character alphabetic entries that are not state
    # abbreviations.

    # Removing non-numerical entries
    dataset = dataset[~dataset['place_id'].str.isdigit()]

    # Removing entries over 2 characters long
    dataset = dataset[dataset['place_id'].str.len() <= 2]

    # Removing entries where 'place_id' == 'PR'
    dataset = dataset[dataset['place_id'] != 'PR']
    # Removing entries where 'place_id' == 'DC'
    dataset = dataset[dataset['place_id'] != 'DC']
    
    # print(len(set(dataset['place_id']))) Just to check that there are exactly 50 states in the data!

    # Now we must group the data by state, using the rounded averages of the index values for our consolidated state index value.
    dataset = round(dataset.groupby('place_name')['index'].mean(), 3)
    
    dsdict = {a : b for a, b in zip(dataset.index, list(dataset))}
    
    # Convert to Pandas Series and remove any existing NaN values.
    ser = pd.Series(dsdict)
    ser = ser[~pd.isna(ser)]

    # Finally, we will need to write our cleaned DataFrame to a csv file. 
    ser.to_csv('HPI_cleaned.csv', index=True)

    return ser   
    

def web_parser1(url):
  """
  Web-scrapes, reads, sorts, cleans, and outputs BLS income for Data Scientists for each state
  Data found at: https://www.bls.gov
  Most recently confirmed as working data source: 11/14/2023
  
  :param url: the input url for the BLS data homepage 
  """
  
  # Opening the home page of tables
  resp = requests.get(url)
  bs = BeautifulSoup(resp.text)
  
  # Narrow our text down to the body text
  bs = bs.find('div', {'id' : 'bodytext'})
  
  # Then, finding the most recent post for State data (In this case, May 2021). To do this, we can implement a short trick:
  # Since we just need to find the first occurrence of the State-grouped data, and the entries are sorted in order of decreasing recency,
  # we can just create a list of all link tags, and then search for the first instance of the link tag holding the word 'State': this
  # should be the most recent one.
  link_tags = bs.find_all('li')
  for tag in link_tags:
    if 'state' in tag.text.lower().strip(): # This addresses potential inconsistencies of whitespace and capitalization.
      state_link_tag = tag
      break
  
  # Now, let's dive into our most recent state information by finding the link.
  recent_data_url = 'https://www.bls.gov' + state_link_tag.a['href']
  
  # Opening a new BeautifulSoup object for our new link
  resp = requests.get(recent_data_url)
  bsnew = BeautifulSoup(resp.text)
  
  
  # Now is the more tricky part. We want to open a new page for each of our state data
  # so that we can properly retrieve all state information. The ordered-by-first-letter
  # data is in the 'a-z-list' div tag, so we will get that first.
  bsnew = bsnew.find('div', {'class' : 'a-z-list'})
  
  # Now we will go through the list of link tags in the table set, and store them in a list.
  state_link_tags = bsnew.find_all('li')
  
  # Now, we must adjust our list and remove the tags for the following:
  # District of Columbia (DC), Guam (GU), Puerto Rico (PR), Virgin Islands (VI), and Washington DC (DC)
  # INCONSISTENCY: Whitespace
  # To do the above, we will first need to address another inconsisency in the website: whitespace. If you run
  # the following command, you can see that some of these texts and headers can contain 
  # inconsistent amounts of spacing, especially at the end. We will adjust these by using the strip() method.
  
  # print([state_link_tags[2].text, state_link_tags[3].text, state_link_tags[4].text, state_link_tags[6].text])
  
  # Now we will use the above knowledge to eliminate the non-state entries from our list.
  not_wanted = ['District of Columbia (DC)', 'Guam (GU)', 'Puerto Rico (PR)', 'Virgin Islands (VI)', 'Washington DC (DC)']
  state_link_tags = [tag for tag in state_link_tags if tag.text.strip() not in not_wanted]
  # print(len(state_link_tags))  # Just to check that we have exactly 50 entries
  
  # Now we must create a dictionary mapping the state names to their links.
  # Using this, we will check for state data regarding Data Scientist mean salaries.
  state_data_links_dict = {tag.text : 'https://www.bls.gov/oes/current/' + tag.a['href'] for tag in state_link_tags}
  
  
  # Next, we need to create a list of the average salary of Data Scientists in each state. To do this,
  # we must iteravely able to find the data for each state. Therefore, it would make most sense to use
  # a helper method. This method will intake a url and return an int representing the state's 
  # mean annual salary for Data Scientists.
  def find_ds_salary(state_url):
    resp = requests.get(state_url)
    bs_state = BeautifulSoup(resp.text)
        
    # Narrow down searchable area
    bs_state = bs_state.find('td', {'id' : 'main-content-td'})
  
    # Now find the row which holds all 'Data Scientist' info
    role_tags = bs_state.find_all('tr')
    ds_tag = [tag for tag in role_tags if 'Data Scientist' in tag.text]
  
    # Finally, retrieve and return the mean annual salary
    # INCONSISTENCY: Wyoming does not recognize Data Scientists as a job, 
    # and Arkansas does not release salary estimates for Data Scientists, 
    # represented by the string '(8)'.
    # To address this inconsistency, in these cases, the helper method will
    # return a None value.
  
    if ds_tag == None or len(ds_tag) == 0:
      return None
    
    salary = ds_tag[0].find_all('td')[-2].text
    
    if salary[0] != '$':
      return None
  
    # Last, we want to convert the string value into an integer.
    salary = int(''.join(re.findall('[\d]', salary)))
    
    return salary
  
  # Now, we will create a dictionary mapping our state name
  salary_dict = {text : find_ds_salary(link) for text, link in state_data_links_dict.items()}
  
  ser = pd.Series(salary_dict)
  # ser = ser[~pd.isna(ser)]  # We decided that having 50 states in all of our returned DataFrames is better than removing NaN values
  #                             which may make the state counts inconsistent.
  
  
  # Finally, we will need to write our cleaned DataFrame to a csv file. 
  ser.to_csv('Salary_cleaned.csv', index=True)
  
  return ser


def web_parser2(url):
  """
  Web-scrapes, reads, sorts, cleans, and outputs NCEI NOAA temperature data for each state
  Data found at: https://www.ncei.noaa.gov/access/monitoring/climate-at-a-glance/statewide/mapping/110-tavg-202101-12.json
  Most recently confirmed as working data source: 11/14/2023

  :param url: the input url for the NCEI NOAA temperature data source (json file)
  """
  
  resp = requests.get(url)

  js = json.loads(resp.text)
  
  # Put 'data' data into dict matching the state name to the mean temperature value
  try:
    jsdict = {item['location'] : item['mean'] for key, item in js['data'].items()}
  except:
    with open('temperature.json', 'r') as f:
      js = json.load(f)
    jsdict = {item['location'] : item['mean'] for key, item in js['data'].items()}

  # INCONSISTENCY: This dataset only uses the contiguous United States. Therefore we will add 
  # Alaska and Hawaii to the dictionary as NaN values to include all 50 recognized states.
  jsdict['Alaska'] = None
  jsdict['Hawaii'] = None

  # Convert the dictionary to a Pandas DataFrame.
  ser = pd.Series(jsdict)

  # Finally, we will need to write our cleaned DataFrame to a csv file. 
  ser.to_csv('Temperature_cleaned.csv', index=True)

  return ser




