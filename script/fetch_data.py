#!/usr/bin/env python
# coding: utf-8

# ## Generate covid19 data from Google SpreadSheet
# 

# In[36]:


import pandas as pd
import os
from datetime import datetime

pd.precision = 5
INPUT_PATH = 'input'
OUTPUT_PATH = 'dataset'

#POPULATION_CSV_PATH = os.path.join(INPUT_PATH, 'un', 'population_2020.csv')
CSV_PATH = os.path.join(INPUT_PATH,'angola.csv')


ANGOLA_POPULATION = 32866268


# In[37]:


os.system("mkdir -p '$OUTPUT_PATH'")


# In[38]:


os.system("curl -Lo $INPUT_PATH/angola.csv 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTyuD092U1peHEGTL4y3QW5dw5sy3t3sxvraveh7sr0HbhG-yqGDD8mEabQmSRW0nNFSI-HqvN4Ij5i/pub?gid=1952696069&single=true&output=csv'")


# In[39]:


data = pd.read_csv(CSV_PATH)


# In[40]:


data.drop(['Sintomas Leves','UTI','Acompanhamento Domiciliar', 'Total Hospitalizado'], axis=1, inplace=True)
data.rename(columns={
    'date':'data',
    'Total Activos': 'activos',
    'Novos Casos': 'novos_casos',
    'Total Cumulativo': 'total_de_casos',
    'Mortos':'novas_mortes',
    'Recuperados':'novos_recuperados'
}, inplace=True)
data.tail()


# In[41]:


data['total_deaths']=data['novas_mortes'].cumsum()
data['total_recovered']=data['novos_recuperados'].cumsum().astype('Int64')


# #### Calculate per population

# In[42]:


data['total_cases_per_capita'] = data['total_de_casos'] / (ANGOLA_POPULATION / 1e5)
data['total_deaths_per_capita'] = data['total_deaths'] / (ANGOLA_POPULATION / 1e5)
data['new_cases_per_capita'] = data['novos_casos'] / (ANGOLA_POPULATION / 1e5)
data['new_deaths_per_capita'] = data['novas_mortes'] / (ANGOLA_POPULATION / 1e5)


# #### Grapher data

# In[43]:


df_grapher = data.copy()
df_grapher['days'] = pd.to_datetime(df_grapher['data']).map(lambda date: (date - datetime(2020, 3, 21)).days) #Day since first reported case

df_grapher = df_grapher[[
    'data','days',
    'novos_casos','novas_mortes',
    'novos_recuperados','total_de_casos',
    'total_deaths','total_recovered',
    'new_cases_per_capita','new_deaths_per_capita',
    'total_cases_per_capita','total_deaths_per_capita'
    ]].rename(columns={
        'data': 'Date',
        'days':'Days Since First Case',
        'novos_casos': 'New Confirmed Cases',
        'total_de_casos':'Total Confirmed Cases',
        'novos_recuperados': 'Recovered Cases',
        'total_recovered': 'Total Recovered Cases',
        'novas_mortes':'New Deaths',
        'total_deaths': 'Total Confirmed Deaths',
        'new_cases_per_capita':'New Confirmed Cases per 100.000 people',
        'total_cases_per_capita': 'Total Confirmed Cases per 100.000 people',
        'new_deaths_per_capita': 'New Confirmed Deaths per 100.000 people',
        'total_deaths_per_capita': 'Total Confirmed Deaths per 100.000 people'

    })


# ## Write output files

# In[44]:


data.columns


# In[45]:


summary_data = data[[
    'data',
    'novos_casos', 'total_de_casos', 
    'novas_mortes', 'total_deaths',
    'novos_recuperados','total_recovered'
    ]].rename(columns={
        'data': 'Data',
        'novos_casos':'Novos Casos',
        'total_de_casos':'Total de Casos', 
        'novas_mortes':'Novos Óbitos',
        'total_deaths':'Total de Óbitos',
        'novos_recuperados':'Novos Recuperados',
        'total_recovered':'Total de Recuperados'
    })

summary_data.to_csv(OUTPUT_PATH + '/summary.csv', index=False)
summary_data.to_json(OUTPUT_PATH + '/summary.json', orient='records')


# In[46]:


tdate = datetime.today()
today = tdate.strftime('%Y-%m-%d')


# In[47]:


filename = datetime.today().strftime('%Y%m%d')
today_file = summary_data.iloc[-1:]


today_file=today_file.assign(UltimaActualizacao={tdate.strftime('%Y-%m-%d %H:%M:%S')})

today_file.to_csv(os.path.join(OUTPUT_PATH, '%s_summary.csv' % filename), index=False)
today_file.to_json(os.path.join(OUTPUT_PATH, '%s.json' % filename), orient='records')

today_file.to_csv(os.path.join(OUTPUT_PATH, 'latest.csv'), index=False)
today_file.to_json(os.path.join(OUTPUT_PATH, 'latest.json'), orient='records')


# In[48]:


# %summary_data.loc[summary_data['date'] =='2020-04-22']


# In[49]:


df_grapher.to_csv(os.path.join(OUTPUT_PATH, 'grapher.csv'), index=False)


# In[50]:


# Just the first time

def create_single_days(df, today):
    i = pd.date_range('2020-03-21', today)
    for x in i:
        dt = x.strftime('%Y-%m-%d')
        date_file = df.loc[df['Data'] ==dt]
        date_file.to_csv(os.path.join(OUTPUT_PATH, '%s_summary.csv' % x.strftime('%Y%m%d')), index=False)


# In[51]:


create_single_days(summary_data, today)


# In[ ]:





# 

# In[ ]:




