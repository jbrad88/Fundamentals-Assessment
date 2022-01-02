#!/usr/bin/env python
# coding: utf-8

# # CAO Points Analysis
# 
# ***
# ## Introduction
# We have been tasked with creating a Jupyter notebook which contains the following:
# 
# * A clear and concise overview of how to load CAO points information from the CAO website into a pandas data frame.
# * A detailed comparison of CAO points in 2019, 2020, and 2021 using the functionality in pandas.
# * Appropriate plots and other visualisations to enhance your notebook for viewers.
# 
# ## Web Scraping
# "Web Scraping" allows us to pull a large amount of data from a website in a quick and efficient manner. The purpose of this Jupyter notebook is to provide a clear and concise overview of how to load CAO points information from the CAO website into a pandas data frame.
# 
# ## Importing required packages
# We will need to import a number of packages to help us with this task.
# 
# #### Regular Expression
# A Regular Expression is a sequence of characters that forms a search pattern. It can be used to check if a string contains a specific search patter [https://www.w3schools.com/python/python_regex.asp]
# 
# #### Requests
# The requests module allows us to send a HTTP request using Python. It returns a Response Object with all the response data (content, encoding, status, etc.) [https://www.w3schools.com/python/module_requests.asp]
# 
# #### DateTime
# This module allows us to work with dates as data objects [https://www.w3schools.com/python/python_datetime.asp].
# 
# #### Pandas
# Pandas is a Python library used for working with data sets. It has functions for analyzing, cleaning, exploring and manipulating data [https://www.w3schools.com/python/pandas/pandas_intro.asp].
# 
# #### Urllib
# The Urllib package is used for fetching and handling URLs [https://www.geeksforgeeks.org/python-urllib-module/]. We'll be using urllib.request for downloading.

# In[1]:


# Convenient HTTP requests.
import requests as rq

# Regular expressions.
import re

# Dates and times.
import datetime as dt

# Data frames.
import pandas as pd

# For downloading.
import urllib.request as urlrq

# For plotting.
import matplotlib.pyplot as plt


# ### Get the current date and time
# 
# We'll be using the datetime function to give our saved files a unique name when scraping the data from the CAO website. First, let's get the current date and time and format it as a string. 

# In[2]:


# Get the current date and time.
now = dt.datetime.now()

# Format as a string.
nowstr = now.strftime('%Y%m%d_%H%M%S')


# <br>
# 
# ## 2021 Points
# 
# http://www.cao.ie/index.php?page=points&p=2021
# 
# ***
# In this section we will download the 2021 data from the CAO website.

# In[3]:


# Fetch the CAO points URL.
resp = rq.get('http://www2.cao.ie/points/l8.php')

# Have a quick peek. 200 means OK.
resp


# <br>
# 
# ## Save original data set
# 
# ***

# In[4]:


# Create a file path for the original data.
pathhtml = 'data/cao2021_' + nowstr + '.html'


# <br>
# 
# **Error on server**
# 
# 
# Technically, the server says we should decode as per:
#     
# ```
# Content-Type: text/html; charset=iso-8859-1
# ```
# 
# However, one line uses \x96 which isn't defined in iso-8859-1.
# 
# Therefore we use the similar decoding standard cp1252, which is very similar but includes #x96.

# In[5]:


# The server uses the wrong encoding, fix it.
original_encoding = resp.encoding

# Change to cp1252.
resp.encoding = 'cp1252'


# In[6]:


# Save the original html file.
with open(pathhtml, 'w') as f:
    f.write(resp.text)


# <br>
# 
# ## Use regular expressions to select lines we want
# 
# ***

# In[7]:


# Compile the regular expression for matching lines.
re_course = re.compile(r'([A-Z]{2}[0-9]{3})(.*)')


# <br>
# 
# #### Loop through the lines of the response
# 
# ***

# In[8]:


# The file path for the csv file.
path2021 = 'data/cao2021_csv_' + nowstr + '.csv'


# In[9]:


# Keep track of how many courses we process.
no_lines = 0

# Open the csv file for writing.
with open(path2021, 'w') as f:
    # Write a header row.
    f.write(','.join(['code', 'title', 'pointsR1', 'pointsR2']) + '\n')
    # Loop through lines of the response.
    for line in resp.iter_lines():
        # Decode the line, using the wrong encoding!
        dline = line.decode('cp1252')
        # Match only the lines representing courses.
        if re_course.fullmatch(dline):
            # Add one to the lines counter.
            no_lines = no_lines + 1
            # The course code.
            course_code = dline[:5]
            # The course title.
            course_title = dline[7:57].strip()
            # Round one points.
            course_points = re.split(' +', dline[60:])
            if len(course_points) != 2:
                course_points = course_points[:2]
            # Join the fields using a comma.
            linesplit = [course_code, course_title, course_points[0], course_points[1]]
            # Rejoin the substrings with commas in between.
            f.write(','.join(linesplit) + '\n')

# Print the total number of processed lines.
print(f"Total number of lines is {no_lines}.")


# <br>
# 
# **NB:** it was verified as of 03/11/2021 that there were 949 courses exactly in the CAO 2021 points list.
# 
# ***

# In[10]:


df2021 = pd.read_csv(path2021, encoding='cp1252')


# In[11]:


df2021


# <br>
# 
# ## 2020 Points
# 
# https://www.cao.ie/index.php?page=points&p=2020
# 
# ***

# In[12]:


url2020 = 'http://www2.cao.ie/points/CAOPointsCharts2020.xlsx'


# <br>
# 
# #### Save Original File
# 
# ***

# In[13]:


# Create a file path for the original data.
pathxlsx = 'data/cao2020_' + nowstr + '.xlsx'


# In[14]:


urlrq.urlretrieve(url2020, pathxlsx)


# <br>
# 
# #### Load Spreadsheet using pandas
# 
# ***

# In[15]:


# Download and parse the excel spreadsheet.
df2020 = pd.read_excel(url2020, skiprows=10)


# In[16]:


df2020


# In[17]:


# Remove "#+matric" from pandas df to help us out further on.
# code adapted from: https://www.geeksforgeeks.org/pandas-remove-special-characters-from-column-names/
df2020['R1 POINTS'] = df2020['R1 POINTS'].replace({'[#+matric]':'0'}, regex=True)
df2020['R1 POINTS'] = df2020['R1 POINTS'].replace({'AQA':'0'}, regex=True)


# In[18]:


df2020


# In[19]:


# Create a file path for the pandas data.
path2020 = 'data/cao2020_' + nowstr + '.csv'


# In[20]:


# Save pandas data frame to disk.
df2020.to_csv(path2020)


# <br>
# 
# ## 2019 Points
# 
# https://www.cao.ie/index.php?page=points&p=2019
# 
# ***

# In[21]:


df2019 = pd.read_excel('data/cao2019_20211230_edited.xlsx')


# In[22]:


df2019


# <br>
# 
# ## concat and join
# 
# ***

# In[23]:


courses2021 = df2021[['code', 'title']]
courses2021


# In[24]:


courses2020 = df2020[['COURSE CODE2','COURSE TITLE']]
courses2020.columns = ['code', 'title']
courses2020


# In[25]:


courses2019 = df2019[['code', 'course']]
courses2019.columns = ['code', 'title']
courses2019


# In[26]:


allcourses = pd.concat([courses2021, courses2020, courses2019], ignore_index=True)
allcourses


# In[27]:


allcourses.sort_values('code')


# In[28]:


allcourses.loc[175]['title']


# In[29]:


allcourses.loc[949]['title']


# In[30]:


# Finds all extra copies of duplicated rows.
allcourses[allcourses.duplicated()]


# In[31]:


# Returns a copy of the data frame with duplciates removed.
allcourses.drop_duplicates()


# In[32]:


# Finds all extra copies of duplicated rows.
allcourses[allcourses.duplicated(subset=['code'])]


# In[33]:


# Returns a copy of the data frame with duplciates removed - based only on code.
allcourses.drop_duplicates(subset=['code'], inplace=True, ignore_index=True)


# In[34]:


allcourses


# <br>
# 
# ## Join to the points
# 
# ***

# In[35]:


# Set the index to the code column.
df2021.set_index('code', inplace=True)
df2021.columns = ['title', 'points_r1_2021', 'points_r2_2021']
df2021


# In[36]:


# Set the index to the code column.
allcourses.set_index('code', inplace=True)


# In[37]:


allcourses = allcourses.join(df2021[['points_r1_2021']])
allcourses


# In[38]:


df2020_r1 = df2020[['COURSE CODE2', 'R1 POINTS']]
df2020_r1.columns = ['code', 'points_r1_2020']
df2020_r1


# In[39]:


# Set the index to the code column.
df2020_r1.set_index('code', inplace=True)
df2020_r1


# In[40]:


# Join 2020 points to allcourses.
allcourses = allcourses.join(df2020_r1)
allcourses


# In[41]:


df2019_r1 = df2019[['code', 'points']]
df2019_r1.columns = ['code', 'points_r1_2019']
df2019_r1


# In[42]:


# Set the index to the code column.
df2019_r1.set_index('code', inplace=True)
df2019_r1


# In[43]:


# Join 2019 points to allcourses.
allcourses = allcourses.join(df2019_r1)
allcourses


# In[44]:


# Replace NA with 0
allcourses.fillna(0)


# In[45]:


#allcourses['points_r1_2021'] = allcourses['points_r1_2021'].str.replace(r'\D', '')
#allcourses['points_r1_2020'] = allcourses['points_r1_2020'].str.replace(r'\D', '')
#allcourses['points_r1_2019'] = allcourses['points_r1_2019'].str.replace(r'\D', '')

cols_to_check = ['points_r1_2021', 'points_r1_2020', 'points_r1_2019']
allcourses[cols_to_check] = allcourses[cols_to_check].replace({'[#,*]':''}, regex=True)
#allcourses[cols_to_check] = allcourses[cols_to_check].replace({'=+matric':''}, regex=True)


# In[46]:


# Print all course to CSV so we can check the stats. 
allcourses.to_csv("allcourses.csv")


# In[49]:


import matplotlib.pyplot as plt


# In[ ]:





# In[ ]:





# In[ ]:





# ***
# 
# ## End
