""" Generate covid19 data from Google SpreadSheet. """

import pandas as pd
import os
from datetime import datetime

pd.precision = 5
INPUT_PATH = 'input'
OUTPUT_PATH = 'dataset'
CSV_PATH = os.path.join(INPUT_PATH, 'angola.csv')
ANGOLA_POPULATION = 32866268


def prepare_data():
    os.system("mkdir -p '$OUTPUT_PATH'")

    data = pd.read_csv(
        "https://docs.google.com/spreadsheets/d/e/2PACX-1vTyuD092U1peHEGTL4y3QW5dw5sy3t3sxvraveh7sr0HbhG-yqGDD8mEabQmSRW0nNFSI-HqvN4Ij5i/pub?gid=1952696069&single=true&output=csv")
    data.drop(['Sintomas Leves', 'UTI( Estado Critico)', 'Acompanhamento Domiciliar',
               'Total Hospitalizado'], axis=1, inplace=True)
    data.rename(columns={
        'date': 'data',
        'Total Activos': 'activos',
        'Novos Casos': 'novos_casos',
        'Total Cumulativo': 'total_de_casos',
        'Mortos': 'novas_mortes',
        'Recuperados': 'novos_recuperados'
    }, inplace=True)

    data['total_deaths'] = data['novas_mortes'].cumsum()
    data['total_recovered'] = data['novos_recuperados'].cumsum().astype('Int64')

    # Calculate per population
    data['total_cases_per_capita'] = data['total_de_casos'] / \
        (ANGOLA_POPULATION / 1e5)
    data['total_deaths_per_capita'] = data['total_deaths'] / \
        (ANGOLA_POPULATION / 1e5)
    data['new_cases_per_capita'] = data['novos_casos'] / \
        (ANGOLA_POPULATION / 1e5)
    data['new_deaths_per_capita'] = data['novas_mortes'] / \
        (ANGOLA_POPULATION / 1e5)

    return data


def generate_grapher(data):
    df_grapher = data.copy()
    df_grapher['days'] = pd.to_datetime(df_grapher['data']).map(lambda date: (
        date - datetime(2020, 3, 21)).days)  # Day since first reported case

    df_grapher = df_grapher[[
        'data', 'days',
        'novos_casos', 'novas_mortes',
        'novos_recuperados', 'total_de_casos',
        'total_deaths', 'total_recovered',
        'new_cases_per_capita', 'new_deaths_per_capita',
        'total_cases_per_capita', 'total_deaths_per_capita'
    ]].rename(columns={
        'data': 'Date',
        'days': 'Days Since First Case',
        'novos_casos': 'New Confirmed Cases',
        'total_de_casos': 'Total Confirmed Cases',
        'novos_recuperados': 'Recovered Cases',
        'total_recovered': 'Total Recovered Cases',
        'novas_mortes': 'New Deaths',
        'total_deaths': 'Total Confirmed Deaths',
        'new_cases_per_capita': 'New Confirmed Cases per 100.000 people',
        'total_cases_per_capita': 'Total Confirmed Cases per 100.000 people',
        'new_deaths_per_capita': 'New Confirmed Deaths per 100.000 people',
        'total_deaths_per_capita': 'Total Confirmed Deaths per 100.000 people'

    })
    df_grapher.to_csv(os.path.join(OUTPUT_PATH, 'grapher.csv'),
                      index=False, float_format='%.3f')


def generate_summary(data):
    summary_data = data[[
        'data',
        'novos_casos', 'total_de_casos',
        'novas_mortes', 'total_deaths',
        'novos_recuperados', 'total_recovered'
    ]].rename(columns={
        'data': 'Data',
        'novos_casos': 'Novos Casos',
        'total_de_casos': 'Total de Casos',
        'novas_mortes': 'Novos Óbitos',
        'total_deaths': 'Total de Óbitos',
        'novos_recuperados': 'Novos Recuperados',
        'total_recovered': 'Total de Recuperados'
    })

    summary_data.to_csv(OUTPUT_PATH + '/summary.csv', index=False)
    summary_data.to_json(OUTPUT_PATH + '/summary.json',
                         orient='records')

    return summary_data


def generate_daily_file(summary_data):
    tdate = datetime.today()
    today = tdate.strftime('%Y-%m-%d')

    filename = datetime.today().strftime('%Y%m%d')
    today_file = summary_data.iloc[-1:]

    today_file = today_file.assign(
        UltimaActualizacao={tdate.strftime('%Y-%m-%d %H:%M:%S')})

    today_file.to_csv(os.path.join(
        OUTPUT_PATH, '%s.csv' % filename), index=False)
    today_file.to_json(os.path.join(OUTPUT_PATH, '%s.json' %
                                    filename), orient='records')

    today_file.to_csv(os.path.join(OUTPUT_PATH, 'latest.csv'), index=False)
    today_file.to_json(os.path.join(
        OUTPUT_PATH, 'latest.json'), orient='records')


# Just the first time

def create_single_days(df, today):
    i = pd.date_range('2020-03-21', today)
    for x in i:
        dt = x.strftime('%Y-%m-%d')
        date_file = df.loc[df['Data'] == dt]
        date_file.to_csv(os.path.join(OUTPUT_PATH, '%s.csv' %
                                      x.strftime('%Y%m%d')), index=False)

        date_file.to_json(os.path.join(OUTPUT_PATH, '%s.json' %
                                       x.strftime('%Y%m%d')), orient='records')


def main():
    today = datetime.today()
    data = prepare_data()
    generate_grapher(data)
    summary_data = generate_summary(data)
    generate_daily_file(summary_data)
    create_single_days(summary_data, today)


if __name__ == '__main__':
    main()
