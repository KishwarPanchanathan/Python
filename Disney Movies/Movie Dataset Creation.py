#!/usr/bin/env python
# coding: utf-8

# # Scraping Disney Movies Data from Wikipedia Website.

# In[46]:


# Importing required Libaries.
import requests as req
from bs4 import BeautifulSoup as bs
import pandas as pd
import json
import re
from datetime import datetime
import pickle


# Scraping the table from website into dictionary data type.

# In[2]:


def get_content_val(row):
    if row.find('li'):
        return [li.get_text(" ",strip=True).replace("\xa0"," ") for li in row.find_all('li')]
    elif row.find('br'):
        return [br for br in row.stripped_strings]
    else:
        return row.get_text(" ",strip=True).replace("\xa0"," ")

def clean_tags(soup):
    for tag in soup.find_all(['sup','span']):
        tag.decompose()
    return soup

# Getting each table from the website.
def get_info_box(urls):
    url = urls

    webpage = req.get(url)

    soup  = bs(webpage.content,'html.parser')
    table = soup.find(class_='infobox vevent')
    info_row = table.find_all('tr')
    clean_tags(soup)

    movie = {}
    for index,row in enumerate(info_row):
        if index == 0:
            movie['Title'] = row.text
        else:
            header = row.find('th')
            if header:
                content_key = row.find('th').get_text(" ",strip=True)
                content_value = get_content_val(row.find('td'))
                movie[content_key] = content_value
    
    return movie


# In[3]:


get_info_box("https://en.wikipedia.org/wiki/Ponyo")


# # Data Extraction
# * Scraping from all the movies in the list of disney Movies

# In[4]:


url = 'https://en.wikipedia.org/wiki/List_of_Walt_Disney_Pictures_films'

webpage = req.get(url)

soup  = bs(webpage.content,'html.parser')
movies = soup.select('.wikitable.sortable i a')
base_path = 'https://en.wikipedia.org/'

movie_info_box = []
for index,movie in enumerate(movies):
    if index % 10 ==0:
        print(index,"Done")
    try:
        link = movie['href']
        full_path = base_path + link
        title = movie['title']
        movie_info_box.append(get_info_box(full_path))
    except Exception as e:
        continue


# Saving the data into json format

# In[5]:


def save_data(title,data):
    with open(title , 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# In[6]:


def load_data(title):
    with open(title,encoding='utf-8') as f:
        return json.load(f)


# In[7]:


save_data('movie_data_cleaned.json',movie_info_box)


# In[8]:


movies = load_data('movie_data_cleaned.json')


# ## Data Cleaning 

# * Changing running time into integers from object data type
# * Converting Budget and Box office into float using regex
# * Changing date column into datetime object 

# In[11]:


def minute_to_int(running_time):
    if running_time == 'N/A':
        return None
    if isinstance(running_time,list):
        return int ((running_time[0]).split(' ')[0])
    else:
        return int(running_time.split(' ')[0])


# In[12]:


for movie in movies:
    movie['Running time (int)'] = minute_to_int(movie.get('Running time','N/A'))


# In[14]:


# Function to  change the money conversion
amounts = r"million|thounsand|billion|crore"
number = r"\d+(,\d{3})*\.*\d*"

word_re = rf"\$*{number}(-|\sto\s)?({number})?\s({amounts})"
value_re = rf"\${number}"

def word_to_number(word):
    value_dict  = {'million':1000000,'thousand':1000,'billion':1000000000,'crore':10000000}
    return value_dict[word]

def parse_word_syntax(string):
    value = float(re.search(number,string,flags=re.I).group().replace(',',''))
    word = word_to_number(re.search(amounts,string,flags=re.I).group())
    return value*word
    

def parse_value_syntax(string):
    value = float(re.search(number,string,flags=re.I).group().replace(',',''))
    return value
    
def money_conversion(money):
    if money == 'N/A':
        return None
    
    if isinstance(money,list):
        if len(money) >= 3:
            money = money[-1]
        else:
            money = money[0]
        
    word_syntax = re.search(word_re,money,flags=re.I)
    value_syntax = re.search(value_re,money)
    
    if word_syntax:
        return parse_word_syntax(word_syntax.group().lower())
        
    elif value_syntax:
        return parse_value_syntax(value_syntax.group())
    else:
        return None
    


# In[ ]:





# In[15]:


for movie in movies:
    movie['Budget (float)'] = money_conversion(movie.get('Budget','N/A'))
    movie['Box office (float)'] = money_conversion(movie.get('Box office','N/A'))


# In[ ]:





# In[16]:


def clean_date(date):
    cleaned_date =  date.split("(")[0].strip()
    if '–' in cleaned_date:
        return cleaned_date.split('–')[0]
    else:
        return cleaned_date
    
def date_conversion(date):
    if isinstance(date,list):
        date = date[0]
    else:
        date = date
    if date == 'N/A':
        return None
    
    date_str = clean_date(date)
    
    fmts=('%B %d, %Y',"%Y","%B %d %Y")
    for fmt in fmts:
        try:
            return datetime.strptime(date_str,fmt).date()
        except ValueError :
            pass


# In[ ]:





# In[17]:


for movie in movies:
    movie['Release date(datetime)'] = date_conversion(movie.get('Release date','N/A'))


# # Saving data as a pickle format.

# In[29]:


import pickle

def save_data(name,data):
    with open(name, 'wb') as f:
        pickle.dump(data, f)


# In[30]:


def load_data(name):
    with open(name, 'rb') as f:
         return pickle.load(f)


# In[31]:


save_data('disney_data-cleande.pickle',movies)


# In[38]:


movies_data = load_data('disney_data-cleande.pickle')


# ## DataFrame

# In[41]:


df = pd.DataFrame(movies)


# In[44]:


df.head()


# In[ ]:




