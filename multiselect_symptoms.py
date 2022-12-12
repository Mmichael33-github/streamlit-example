## libraries
import pandas as pd
import streamlit as st
#import plotly.graph_objects as go

# load the datasets
drugs = pd.read_csv('drugs_df.csv', usecols = ['brand_name', 'generic_name'])
side_effects = pd.read_csv('side_effects.csv')

# rename columns
side_effects.columns = ['side_effect', 'patients', 'percentage', 'drug']

# remove empty values (as for this version, there is one NA in 'patients'):
side_effects = side_effects.dropna()

# clear out brand names of drugs (leave only the first word
# (I checked manually - it's the actual drug's name):
drugs['brand_name'] = drugs['brand_name'].apply(lambda x: x.split()[0])

# clear out "%" symbol from side effects' percentage before converting to 'int':
side_effects['percentage'] = side_effects['percentage'].apply(lambda x: x.split('%')[0])

# convert generic names to lowercase:
side_effects['drug'] = side_effects['drug'].str.lower()
drugs['generic_name'] = drugs['generic_name'].str.lower()

# replace the 'nan' strings:
side_effects['side_effect'] = side_effects['side_effect'].replace(
    {'NAN': 'Not enough data',
     'NAN*': 'Not enough data'})
side_effects[['patients', 'percentage']] = side_effects[['patients', 'percentage']].replace(
    {'NAN': 0,
     'NAN*': 0})

# convert relevant column types to numerical:
side_effects['patients'] = side_effects['patients'].astype('int')
side_effects['percentage'] = side_effects['percentage'].astype('int')

# clear out duplicates:
drugs = drugs.drop_duplicates()
side_effects = side_effects.drop_duplicates()

# create a list of unique generic names, without duplicated entries 
unq_drugs = drugs['brand_name'].unique().tolist()

user_selection = st.multiselect('Please enter the medication you want to check:', 
                                options = unq_drugs)

# make a list of generic names:
user_selection_gen = drugs.query('brand_name in @user_selection')

# create an output table:
output_df = side_effects.query('drug in @user_selection_gen.generic_name')

# check whether the drug has data from less than total of 20 patients:
min_patients = 20 #threshold of total patients

# sum the patients for each drug:
patients_per_drug = output_df.groupby('drug')['patients'].sum()

# filter drugs by total amount of patients, replace 'percentage' for drugs which don't have at least 20 patients' data:
for item in patients_per_drug.index.tolist():
    if patients_per_drug[item] < min_patients:
        output_df.loc[output_df['drug'] == item, 'percentage'] = 0
        
# add brand names:
output_df = output_df.merge(
    user_selection_gen, 
    how = 'right', 
    left_on = 'drug', 
    right_on = 'generic_name').drop(columns = ['drug'])

# calculate total patients per symptom and store it in column 'total_patients_s':
output_df = output_df.merge(
    output_df.groupby('side_effect')['patients'].sum()
    .reset_index().rename(columns = {'patients':'total_patients_s'}), 
                          how = 'left', on = 'side_effect')

# calculate total percentage of side effect among all patients who used this drug:
output_df['total_percentage'] = output_df['total_patients_s'] / output_df['patients'].sum()

# convert 'percentage' column for better display with pd.style():
output_df['percentage'] = output_df['percentage'] / 100

# rename 'percentage' column:
output_df = output_df.rename(columns = {'percentage': 'percentage_by_drug'})

# order by values:
output_df = output_df.sort_values(
    'total_percentage', ascending = False).reset_index(drop = True)


# print the output table:
st.dataframe(output_df[['brand_name', 
                        'side_effect',
                        st.bar_chart(int('total_percentage')), 
                        'percentage_by_drug']].style.format({'total_percentage': '{:.2%}',
                                                     'percentage': '{:.2%}'}),
             use_container_width = True)
