import csv
import json
import re
import requests
import pandas as pd
from io import StringIO
import config

def fetch_chart(chart_id, token):
    url = 'https://api.datawrapper.de/v3/charts/{}'.format(chart_id)
    headers = {
        'accept': '*/*',
        'Authorization': 'Bearer {}'.format(token)
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(response.text)
    return json.loads(response.text)


def fetch_chart_data(chart_id, token):
    url = 'https://api.datawrapper.de/v3/charts/{}/data'.format(chart_id)
    headers = {
        'accept': 'text/csv',
        'Authorization': 'Bearer {}'.format(token)
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(response.text)
    return response.text


def export_chart(chart_id, token):
    url = 'https://api.datawrapper.de/v3/charts/{}/export/svg'.format(chart_id)
    headers = {
        'accept': 'image/png',
        'Authorization': 'Bearer {}'.format(token),
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        return None


class ChartList:
    def __init__(self, token):
        self.ALL_CHART_TYPES = [
            'd3-bars',
            'd3-bars-split',
            'd3-bars-stacked',
            'd3-bars-grouped',
            'd3-bars-bullet',
            'd3-dot-plot',
            'd3-range-plot',
            'd3-arrow-plot',
            'column-chart',
            'grouped-column-chart',
            'stacked-column-chart',
            'd3-area',
            'd3-lines',
            'd3-pies',
            'd3-donuts',
            'd3-multiple-pies',
            'd3-multiple-donuts',
            'd3-scatter-plot',
            'election-donut-chart',
            'd3-maps-choropleth',
            'd3-maps-symbols',
            'locator-map',
            'tables'
        ]
        self.EXCLUDED_TYPES = ['d3-maps-choropleth', 'd3-maps-symbols', 'locator-map', 'tables']
        self.QUERY = '/v3/charts?published=true&order=DESC&orderBy=createdAt&limit=100&offset=0&expand=true'
        
        self.__token = token
        self.__chart_list = []

    def __d3_bars_rules(self, chart):
      rules = [
          chart['metadata']['data']['horizontal-header']  # first row is column names
      ]
      return all(rules)
    
    def __column_chart_rules(self, chart):
        rules = [
            chart['metadata']['data']['horizontal-header']
        ]
        return all(rules)

    def __rules(self, chart):
        if chart['type'] in self.EXCLUDED_TYPES:
            return False
        match chart['type']:
            case 'd3-bars':
                return self.__d3_bars_rules(chart)
            case 'column-chart':
                return self.__column_chart_rules(chart)
            case _:
                return True

    def __fetch_chart_list_helper(self, query):
        url = 'https://api.datawrapper.de' + query
        headers = {
            'accept': '*/*',
            'Authorization': 'Bearer {}'.format(self.__token)
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception(response.text)

        charts = json.loads(response.text)

        if 'next' in charts:
            return [x for x in charts['list'] if self.__rules(x)] + self.__fetch_chart_list_helper(charts['next'])
        else:
            return [x for x in charts['list'] if self.__rules(x)]

    def fetch_chart_list(self):
        self.__chart_list = self.__fetch_chart_list_helper(self.QUERY)
        return self.__chart_list

    def get_chart_list(self):
        return self.__chart_list

    def filter_chart_list(self, selected_types):
        if not set(selected_types).issubset(set(self.ALL_CHART_TYPES)):
            raise Exception('selected_types is not a subset of ALL_CHART_TYPES')
        return [x for x in self.__chart_list if x['type'] in selected_types]