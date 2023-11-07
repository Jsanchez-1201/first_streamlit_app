import pandas as pd
import numpy as np
import sys
import re

def page_2():
    st.title("Page 2: Automated Functions")

    # Access data from st.session_state
    revision_file = st.session_state.df
    reference_columns = st.session_state.reference_columns

    def job_title(revision_file):
      
      try:
          data = pd.read_csv(revision_file)
          missing_job = data['Title'].isna().sum()
          count = data['Title'].count() + missing_job
      
          percentage = (missing_job/count)
      
          if percentage <= 0.25:
              df = data[data['Title'].notna()]
              print ('All the records with missing information were deleted. Job Title has their 75% with information.')
              return df
              
          else:
              print('In this dataset, less than 75% does not have Job Title completed')
              return data
      
      except OSError as e:
              print(f"Unable to open {revision_file} because: {e}", file=sys.stderr)
              return
    if df is not None:
      cleaned_job = job_title(revision_file)
      
    def split_name(revision_file):
      
      try:
      
          data = pd.read_csv(revision_file)
          if data['Last Name'].isnull().values.any() == True:
      
          # replace any character on the Name column for a whitespace
              data = data.replace('[-| .,\/_]+',' ', regex = True)
          
              # new data frame with split value columns
              new = data["Name"].str.split(" ", n=1, expand = True)
          
              # making separate first name column from new data frame
              data["Name"] = new[0]
              
              # making separate last name column from new data frame
              data["Last Name"] = new[1]
                  
              return data
          
          else:
              print("This database already has both Name and Last Name in different columns.")
              return data
      
      except OSError as e:
              print(f"Unable to open {revision_file} beacuse: {e}", file=sys.stderr)
              return

    def validate_names(revision_file):
      
      try:
          data = pd.read_csv(revision_file)
          data_temp = data
          
          data = data[data['Name'].notna()]
      
          lenght = data['Name'].str.len()
          mask = lenght >= 2
          data = data[mask]
      
          name_nulls = data_temp['Name'].isna().sum()
          count_total_temp = data_temp['Name'].count() + name_nulls
      
          count_rows = data['Name'].count()
      
          percentage = count_rows/count_total_temp
          
          if percentage <= 0.25:
              print('All the records with missing information were deleted. Name has their 75% with information.')
              return data
          else:
              print('In this dataset, less than 75% does not have a valid Name')
              return data_temp
      
      except OSError as e:
              print(f"Unable to open {revision_file} beacuse: {e}", file=sys.stderr)
              return
