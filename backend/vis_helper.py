import colorsys
import csv
import dateparser
import json
import numpy as np
import pandas as pd
import re
import requests
from io import StringIO
from scipy.spatial import distance
import config
from bs4 import BeautifulSoup

from algorithm.trend import *
import config

DW_COLORS = {
    0: '#18a1cd', 1: '#1d81a2', 2: '#15607a', 3: '#82f5cf',
    4: '#00dca6', 5: '#09bb9f', 6: '#c4c4c4', 7: '#c71e1d',
    8: '#fa8c00', 9: '#ffca76', 10: '#ffe59c'
}

def is_numerical(series):
    def is_date(element):
        try:
            dateparser.parse(element).date()
            return True
        except:
            return False
    
    return series.apply(is_date).all() or pd.api.types.is_numeric_dtype(series)
    

def general_trend(data):
    def moving_average(data, n=4) :
        ret = np.cumsum(data, dtype=float)
        ret[n:] = ret[n:] - ret[:-n]
        return ret[n - 1:] / n
    return np.all(np.diff(moving_average(np.array(data))) > 0)


def add_L1_description(response, chart, template) -> None:
    # type
    key = 'L1-0'
    chart_type = json.load(open('./assets/chartType.json'))[chart['type']]
    add_description(response, key, template[key]['tag'], template[key]['description'], [chart_type['en']], [chart_type['fr']])

    # title
    key = 'L1-1'
    if len(chart['title'].strip()) == 0:
        response['schema']['L1'][1]['show'] = False
    else:
        title = BeautifulSoup(chart['title'], 'lxml').text
        add_description(response, key, template[key]['tag'], template[key]['description'], [title], [title])
    
    # intro
    key = 'L1-2'
    if len(chart['metadata']['describe']['intro'].strip()) == 0:
        response['schema']['L1'][2]['show'] = False
    else:
        intro = BeautifulSoup(chart['metadata']['describe']['intro'], 'lxml').text
        add_description(response, key, template[key]['tag'], template[key]['description'], [intro], [intro])

    # notes
    key = 'L1-3'
    if len(chart['metadata']['annotate']['notes'].strip()) == 0:
        response['schema']['L1'][3]['show'] = False
    else:
        notes = BeautifulSoup(chart['metadata']['annotate']['notes'], 'lxml').text
        add_description(response, key, template[key]['tag'], template[key]['description'], [notes], [notes])


def add_L3_description(response: dict) -> None:
    key = 'L3-0'
    response['visDescription'][key] = {
        'id': key,
        'tag': {'en': "External information", 'fr': "Informations externes"},
        'text': {'en': "", 'fr': ""}
    }

def list2str(l: list, lang: str) -> str:
    l = [str(x).strip() for x in l]
    if len(l) == 0:
        return ''
    elif len(l) == 1:
        return l[0]
    else:
        match lang:
            case 'en':
                if len(l) == 2:
                    return l[0] + ' and ' + l[1]
                else:
                    return ', '.join(l[:-1]) + ', and ' + l[-1]
            case 'fr':
                if len(l) == 2:
                    return l[0] + ' et ' + l[1]
                else:
                    return ', '.join(l[:-1]) + ', et ' + l[-1]
            case _:
                raise Exception("unsupported language")
            
def find_dict_item(item, key: str):
    indices = key.split('-')
    for i, idx in enumerate(indices):
        if not idx.isnumeric():
            # idx is string
            item = item.get(idx)
        else:
            # idx is numeric
            item = item[int(idx)]
            if 'children' in item:
                item = item['children'] if i < len(indices) - 1 else item
    return item

def add_description(response, key, tag, template=None, kw_en=[], kw_fr=[], schema=None):
    if template:
        response['visDescription'][key] = {
            'id': key,
            'tag': tag,
            'text': {
                'en': template['en'].format(*kw_en),
                'fr': template['fr'].format(*kw_fr)
            }
        }
    elif kw_en and kw_fr:
        response['visDescription'][key] = {
            'id': key,
            'tag': tag,
            'text': {
                'en': kw_en,
                'fr': kw_fr
            }
        }
    elif schema:
        response['visDescription'][key] = {
            'id': key,
            'tag': tag,
            'text': {
                'en': '; '.join([x['values']['en'] for x in schema['comparison']]),
                'fr': '; '.join([x['values']['fr'] for x in schema['comparison']])
            }
        }
    else:
        response['visDescription'][key] = {
            'id': key,
            'tag': tag,
            'text': {
                'en': '',
                'fr': ''
            }
        }

def add_comparison(schema, label, value, selectKey, seriesKey, template, kw_en, kw_fr):
    if 'comparison' not in schema:
        schema['comparison'] = []
    schema['comparison'].append({
        'label': label,
        'value': value,
        'selectKey': selectKey,
        'seriesKey': seriesKey,
        'values': {
            'en': template['en'].format(*kw_en),
            'fr': template['fr'].format(*kw_fr)
        }
    })


def get_outlier_description_group_wise(df, outliers, chart_type, col=None):
    template_en = "{} has a potential outlier of {}, "
    template_fr = "{} a une valeur aberrante potentielle de {}, "

    if col:
        match chart_type:
            case 'd3-bars-split':
                kw_en = "For the column {}, ".format(col)
                kw_fr = "Pour la colonne {}, ".format(col)
            case 'd3-bars-stacked' | 'd3-bars-grouped' | 'grouped-column-chart' | 'stacked-column-chart':
                kw_en = "For the the category {}, ".format(col)
                kw_fr = "Pour la catégorie {}, ".format(col)
            case 'd3-area':
                kw_en = "For the cumulative totals of {}, ".format(col)
                kw_fr = "Pour les totaux cumulés de {}, ".format(col)
            case 'd3-lines':
                kw_en = "For the series {}, ".format(col)
                kw_fr = "Pour la séerie {}, ".format(col)
            case _:
                kw_en, kw_fr = '', ''
    else:
        match chart_type:
            case 'd3-bars-stacked' | 'stacked-column-chart':
                kw_en = 'For the aggreagate values, '
                kw_fr = 'Pour les valeurs agrégées, '
            case _:
                kw_en, kw_fr = '', ''

    for x in outliers:
        val, idx = x[0], x[1]
        kw_en += template_en.format(df.iloc[idx,0], val)
        kw_fr += template_fr.format(df.iloc[idx,0], val)
    
    kw_en = kw_en[:-2] + '.'
    kw_fr = kw_fr[:-2] + '.'

    return {'en': kw_en.capitalize(), 'fr': kw_fr.capitalize()}


def get_outlier_description_element_wise(df, outliers, chart_type, element=None):
    kw_en = ''
    kw_fr = ''

    template_en = "{} has a potential outlier of {}, "
    template_fr = "{} a une valeur aberrante potentielle de {}, "
    
    if element:
        match chart_type:
            case 'd3-bars-split':
                kw_en = 'For the row {}, '.format(element)
                kw_fr = 'Pour la rangée {}, '.format(element)
            case 'd3-bars-stacked':
                kw_en = 'For the element {}, '.format(element)
                kw_fr = "Pour l'élément {}, ".format(element)
            case 'stacked-column-chart':
                kw_en = 'For the column {}, '.format(element)
                kw_fr = 'Pour la colonne {}, '.format(element)

    for x in outliers:
        val, idx = x[0], x[1]
        kw_en += template_en.format(df.columns[idx+1], val)
        kw_fr += template_fr.format(df.columns[idx+1], val)

    kw_en = kw_en[:-2] + '.'
    kw_fr = kw_fr[:-2] + '.'
    
    return {'en': kw_en, 'fr': kw_fr}


def get_correlation_type(coefficient):
    if coefficient[0] > 0.6:
        return 'strong-positive'
    elif coefficient[0] > 0.2:
        return 'weak-positive'
    elif coefficient[0] > -0.2:
        return 'no-correlation'
    elif coefficient[0] > -0.6:
        return 'weak-negative'
    else:
        return 'strong-negative'
    

def get_correlation_description(coefficient, chart_type, stack=False):
    if coefficient[0] > 0.6:
        if stack:
            return {
                "en": "The stacked data show a strong positive correlation.",
                "fr": "Les données empilées montrent une forte corrélation positive."
            }
        else:
            return {
                "en": "The data for {} show a strong positive correlation.".format(col),
                "fr": "Les données pour {} montrent une forte corrélation positive.".format(col)
            }
    elif coefficient[0] > 0.2:
        if stack:
            return {
                "en": "The stacked data show a weak positive correlation.",
                "fr": "Les données empilées montrent une faible corrélation positive."
            }
        else:
            return {
                "en": "The data for {} show a weak positive correlation.".format(col),
                "fr": "Les données pour {} montrent une faible corrélation positive.".format(col)
            }
    elif coefficient[0] > -0.2:
        if stack:
            return {
                "en": "There is no correlation observed in the stacked data.",
                "fr": "Aucune corrélation n'est observée dans les données empilées."
            }
        else:
            return {
                "en": "There is no correlation observed in the data for {}.".format(col),
                "fr": "Aucune corrélation n'est observée dans les données pour {}.".format(col)
            }
    elif coefficient[0] > -0.6:
        if stack:
            return {
                "en": "The stacked data show a weak negative correlation.",
                "fr": "Les données empilées montrent une faible corrélation négative."
            }
        else:
            return {
                "en": "The data for {} show a weak negative correlation.".format(col),
                "fr": "Les données pour {} montrent une faible corrélation négative.".format(col)
            }
    else:
        if stack:
            return {
                "en": "The stacked data show a strong negative correlation.",
                "fr": "Les données empilées montrent une forte corrélation négative."
            }
        else:
            return {
                "en": "The data for {} show a strong negative correlation.".format(col),
                "fr": "Les données pour {} montrent une forte corrélation négative.".format(col)
            }

def add_univariate_trend(trend, df, chart_type, response, key, tag):
    for x in trend:
        i0, i1 = x['indices'][0], x['indices'][1]
        x['names'] = (df.iloc[i0,0], df.iloc[i1,0])
        x['values'] = (df.iloc[i0,1], df.iloc[i1,1])
        x['delta'] = (df.iloc[i1,1] - df.iloc[i0,1]) / (i1 - i0)

    if len(trend) > config.THRESHOLD_TOTAL_INTERVALS:
        n = config.THRESHOLD_SPECIFIC_INTERVALS
        intervals_asc = sorted([x for x in trend if x['delta'] > 0], key=lambda x: x['delta'], reverse=True)[:n]
        intervals_desc = sorted([x for x in trend if x['delta'] < 0], key=lambda x: x['delta'])[:n]

        schema = find_dict_item(response['schema'], key)
        if len(intervals_asc) == 0 and len(intervals_desc) == 0:
            schema['show'] = False
            return

        if len(intervals_asc) > 0:
            if 'children' not in schema: schema['children'] = []
            key_child = '{}-{}'.format(key, 0)
            schema['children'].append({'title': config.TAG_ASC, 'key': key_child})
            
            trend_text = get_trend_specific_description(intervals_asc, 'asc')
            add_description(
                response,
                key_child,
                {k: '{} - {}'.format(v, config.TAG_ASC[k]) for k, v in tag.items()},
                kw_en=[trend_text['en']],
                kw_fr=[trend_text['fr']]
            )
            response['visualCue'][key_child] = {'markArea': {'data': [     
                [{'xAxis': int(x['indices'][0]), 'yAxis': x['values'][0]}, {'xAxis': int(x['indices'][1]), 'yAxis': x['values'][1]}] for x in intervals_asc
            ]}}
        
        if len(intervals_desc) > 0:
            if 'children' not in schema: schema['children'] = []
            key_child = '{}-{}'.format(key, 1)
            schema['children'].append({'title': config.TAG_DESC, 'key': key_child})

            trend_text = get_trend_specific_description(intervals_desc, 'desc')
            add_description(
                response,
                key_child,
                {k: '{} - {}'.format(v, config.TAG_DESC[k]) for k, v in tag.items()},
                kw_en=[trend_text['en']],
                kw_fr=[trend_text['fr']]
            )
            response['visualCue'][key_child] = {'markArea': {'data': [
                [{'xAxis': int(x['indices'][0]), 'yAxis': x['values'][0]}, {'xAxis': int(x['indices'][1]), 'yAxis': x['values'][1]}] for x in intervals_desc
            ]}}

    else:
        trend_text = get_trend_description(trend, chart_type)
        add_description(response, key, tag, kw_en=[trend_text['en']], kw_fr=[trend_text['fr']])


def add_multivariate_trend(trend, df, idx, chart_type, response, key, tag):
    idx += 1
    col = df.columns[idx]

    for x in trend:
        i0, i1 = x['indices'][0], x['indices'][1]
        x['names'] = (df.iloc[i0,0], df.iloc[i1,0])
        x['values'] = (df.iloc[i0,idx], df.iloc[i1,idx])
        x['delta'] = (df.iloc[i1,idx] - df.iloc[i0,idx]) / (i1 - i0)

    if len(trend) > config.THRESHOLD_TOTAL_INTERVALS:
        n = config.THRESHOLD_SPECIFIC_INTERVALS
        intervals_asc = sorted([x for x in trend if x['delta'] > 0], key=lambda x: x['delta'], reverse=True)[:n]
        intervals_desc = sorted([x for x in trend if x['delta'] < 0], key=lambda x: x['delta'])[:n]
                    
        schema = find_dict_item(response['schema'], key)
        if len(intervals_asc) == 0 and len(intervals_desc) == 0:
            schema['show'] = False
            return

        if len(intervals_asc) > 0:
            if 'children' not in schema: schema['children'] = []
            key_child = '{}-{}'.format(key, 0)
            schema['children'].append({'title': config.TAG_ASC, 'key': key_child})
            
            tmp_tag = {k: '{} - {}'.format(v, config.TAG_ASC[k]) for k, v in tag.items()}
            trend_text = get_trend_specific_description(intervals_asc, 'asc', col=col)
            add_description(response, key_child, tmp_tag, kw_en=[trend_text['en']], kw_fr=[trend_text['fr']])

            response['visualCue'][key_child] = [
                {'markArea': {'data': [
                    [{'xAxis': int(x['indices'][0]), 'yAxis': x['values'][0]}, {'xAxis': int(x['indices'][1]), 'yAxis': x['values'][1]}] for x in intervals_asc
                ]}} if tmp_col == col else {} for tmp_col in df.columns[1:]
            ]

        if len(intervals_desc) > 0:
            if 'children' not in schema: schema['children'] = []
            key_child = '{}-{}'.format(key, 1)
            schema['children'].append({'title': config.TAG_DESC, 'key': key_child})
            
            tmp_tag = {k: '{} - {}'.format(v, config.TAG_DESC[k]) for k, v in tag.items()}
            trend_text = get_trend_specific_description(intervals_desc, 'desc', col=col)
            add_description(response, key_child, tmp_tag, kw_en=[trend_text['en']], kw_fr=[trend_text['fr']])

            response['visualCue'][key_child] = [
                {'markArea': {'data': [
                    [{'xAxis': int(x['indices'][0]), 'yAxis': x['values'][0]}, {'xAxis': int(x['indices'][1]), 'yAxis': x['values'][1]}] for x in intervals_desc
                ]}} if tmp_col == col else {} for tmp_col in df.columns[1:]
            ]
    else:
        trend_text = get_trend_description(trend, chart_type, col=col)
        add_description(response, key, tag, kw_en=[trend_text['en']], kw_fr=[trend_text['fr']])
        
        match chart_type:
            case 'd3-bars-stacked' | 'stacked-column-chart' | 'd3-area':
                response['visualCue'][key] = [{
                    'itemStyle': {'decal': config.DECAL}
                } if i < idx else {} for i in range(len(df.columns[1:]))]
            case 'd3-bars-grouped' | 'grouped-column-chart':
                response['visualCue'][key] = [{
                    'itemStyle': {'decal': config.DECAL}
                } if tmp_col == col else {} for tmp_col in df.columns[1:]]
            case 'd3-lines':
                response['visualCue'][key] = [{'lineStyle': {
                    'shadowColor': '#ffff00', 'shadowBlur': 10
                }} if tmp_col == col else {} for tmp_col in df.columns[1:]]