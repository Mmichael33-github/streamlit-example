## libraries
import pandas as pd
import streamlit as st

# upload the datasets
drugs = pd.read_csv('drugs.csv')
side_effects = pd.read_csv('side_effects.csv')

# clear 'drugs' dataset - remove unnecessary columns
drugs = drugs[['input', 'specific drug', 'generic name']]
drugs = drugs.dropna()

# rename dataset's columns
side_effects.columns = ['side_effect', 'patients', 'percentage', 'drug']
drugs.columns = ['input', 'specific_drug', 'generic_name']

# create a list of unique generic names, without duplicated entries 
unq_generic = drugs['generic_name'].unique().tolist()

# create multiselect:
user_generics = st.multiselect('Please enter the medication you want to check:',
                               options = unq_generic)

# create a list of unique drug names for user's generics:
user_drugs = drugs.query('generic_name in @user_generics')['specific_drug'].unique().tolist()

user_side_effects = side_effects.query('drug in @user_drugs').sort_values(
    'percentage', ascending = False)

#st.write('The drugs you entered are: ', 
#         user_side_effects['side_effect'].unique().tolist())
st.dataframe(user_side_effects, width = use_container_width)
