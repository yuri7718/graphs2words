import numpy as np
from scipy.stats import pearsonr
from vis_helper import *
from algorithm.color import *
from algorithm.trend import *
from stats import *
import config


def add_d3_bars_option(response, chart, df, color):
    
    HIGHLIGHTED_SERIES = chart['metadata']['visualize']['highlighted-series']

    # ECharts option
    BAR_WIDTH = 30
    GAP = 5
    
    option = {}

    option['tooltip'] = {'trigger': 'axis'}
    
    label_width = df.iloc[:,0].astype(str).str.len().max()
    label_width = (np.log(label_width) + 1) * 35
    
    option['grid'] = {
        'left': label_width,
        'height': (BAR_WIDTH + GAP) * len(df)
    }

    option['xAxis'] = {'type': 'value'}
    option['yAxis'] = {
        'type': 'category', 
        'inverse': True,
        'data': df.iloc[:,0].tolist(),
        'axisLabel': {
            'formatter': HIGHLIGHTED_SERIES,
            'rich': {'highlighted': {'fontWeight': 'bold'}},
            'align': 'left',
            'overflow': 'break',
            'margin': label_width,
            'width': label_width
        },
        'axisTick': {'show': False},
        'zLevel': 1
    }

    if color:
        option['color'] = color

    option['series'] = [{
        'type': 'bar',
        'data': df.iloc[:,1].tolist(),
        'colorBy': 'data',
        'barWidth': BAR_WIDTH
    }]

    response['visualize']['option'] = option


def add_d3_bars_description(response, chart, df, color, template):
    add_L1_description(response, chart, template['L1-info'])
    template = template['d3-bars']

    stats = df.iloc[:,1].describe()

    # x-axis
    key = 'L1-4-0'
    kw = [df.columns[1], min(df.iloc[:,1].min().round(2), 0), max(0, df.iloc[:,1].max().round(2))]
    add_description(response, key, template[key]['tag'], template[key]['description'], kw, kw)

    # y-axis
    key = 'L1-4-1'
    y_numerical = is_numerical(df.iloc[:,0])
    if y_numerical:
        kw = [df.columns[0], df.iloc[0,0], df.iloc[-1,0]]
        add_description(response, key, template[key]['tag'], template[key]['description']['numerical'], kw, kw)
    else:
        kw_en = [df.columns[0], list2str(df.iloc[:,0].tolist(), 'en')]
        kw_fr = [df.columns[0], list2str(df.iloc[:,0].tolist(), 'fr')]
        add_description(response, key, template[key]['tag'], template[key]['description']['categorical'], kw_en, kw_fr)
    
    # color
    key = 'L1-5'
    schema = find_dict_item(response['schema'], key)
    match len(set(color)):
        case 0:
            schema['show'] = False
        case 1:
            color_name = ColorName()
            name = color_name.nearest_neighbor_search(next(iter(color)))
            add_description(response, key, template[key]['tag'], template[key]['description']['single-color'], [name['en']], [name['fr']])
        case _:
            color_name = ColorName()
            color_map = {}
            for i, c_node in enumerate(color):
                if c_node not in color_map:
                    c_name = color_name.nearest_neighbor_search(c_node)
                    color_map[c_node] = {'name': c_name, 'indices': [i]}
                else:
                    color_map[c_node]['indices'].append(i)

            schema['children'] = []
            for i, (_,c_info) in enumerate(sorted(color_map.items(), key=lambda item: len(item[1]['indices']))):
                key_child = '{}-{}'.format(key, i)
                schema['children'].append({'title': c_info['name'], 'key': key_child})
                
                tag = {k: '{} - {}'.format(v, c_info['name'][k]) for k, v in template[key]['tag'].items()}
                
                if i < len(color_map) - 1:
                    elements = df.iloc[c_info['indices'],0].tolist()
                    kw_en = [c_info['name']['en'], list2str(elements, 'en')]
                    kw_fr = [c_info['name']['fr'], list2str(elements, 'fr')]
                    add_description(response, key_child, tag, template[key]['description']['multi-color'], kw_en, kw_fr)
                else:
                    kw_en = [c_info['name']['en']]
                    kw_fr = [c_info['name']['fr']]
                    add_description(response, key_child, tag, template[key]['description']['last-element'], kw_en, kw_fr)

                response['visualCue'][key_child] = {
                    'enabled': True,
                    'decal': {
                        'show': True,
                        'decals': [config.DECAL if j in c_info['indices'] else {'symbol': 'none'} for j in range(len(df))]
                    }
                }

    # data points
    key = 'L2-0'
    data_points = [' '.join(x) for x in df.astype(str).values]
    kw_en = [list2str(data_points, 'en')]
    kw_fr = [list2str(data_points, 'fr')]
    add_description(response, key, template[key]['tag'], template[key]['description'], kw_en, kw_fr)

    # maximum
    key = 'L2-1-0'
    idx, max_ = df.iloc[:,1].idxmax(), stats['max'].round(2)
    kw = [df.iloc[idx,0], max_]
    add_description(response, key, template[key]['tag'], template[key]['description'], kw, kw)
    response['visualCue'][key] = {'markPoint': {
        'data': [{
            'type': 'max',
            'symbolRotate': 270 if max_ >= 0 else 90,
            'label': {'offset': [6,3] if max_ >= 0 else [-6,3]},
            'itemStyle': {'color': color[idx]} if len(color) > idx else {}
        }]
    }}

    # minimum
    key = 'L2-1-1'
    idx, min_ = df.iloc[:,1].idxmin(), stats['min'].round(2)
    kw = [df.iloc[idx,0], min_]
    add_description(response, key, template[key]['tag'], template[key]['description'], kw, kw)
    response['visualCue'][key] = {'markPoint': {
        'data': [{
            'type': 'min',
            'symbolRotate': 270 if min_ >= 0 else 90,
            'label': {'offset': [6,3] if min_ >= 0 else [-6,3]},
            'itemStyle': {'color': color[idx]} if len(color) > idx else {}
        }]
    }}

    # mean
    key = 'L2-2-0'
    kw = [stats['mean'].round(2)]
    add_description(response, key, template[key]['tag'], template[key]['description'], kw, kw)

    # std
    key = 'L2-2-1'
    kw = [stats['std'].round(2)]
    add_description(response, key, template[key]['tag'], template[key]['description'], kw, kw)

    # median
    key = 'L2-2-2'
    kw = [stats['50%'].round(2)]
    add_description(response, key, template[key]['tag'], template[key]['description'], kw, kw)

    # outliers
    key = 'L2-3'
    outliers = get_outliers(df.iloc[:,1].tolist())
    if len(outliers) == 0:
        schema = find_dict_item(response['schema'], key)
        schema['show'] = False
    else:
        outlier_text = get_outlier_description_group_wise(df, outliers, chart['type'])
        add_description(
            response,
            key,
            template[key]['tag'],
            kw_en=[outlier_text['en']],
            kw_fr=[outlier_text['fr']]
        )
        response['visualCue'][key] = {'markPoint': {
            'data': [{
                'coord': [x[0], x[1]],
                'value': x[0],
                'symbolRotate': 270 if x[0] >= 0 else 90,
                'label': {'offset': [6,3] if x[0] >= 0 else [-6,3]},
                'itemStyle': {'color': color[x[1]]} if len(color) > x[1] else {}
            } for x in outliers]
        }}

    # correlation
    key = 'L2-4'
    schema = find_dict_item(response['schema'], key)
    if y_numerical == False:
        schema['show'] = False
    else:
        coefficient = pearsonr(np.arange(len(df)), df.iloc[:,1].tolist())
        if coefficient[1] >= 0.05:
            # correlation coefficient is not statistically significant
            schema['show'] = False
        else:
            correlation_type = get_correlation_type(coefficient)
            add_description(response, key, template[key]['tag'], template[key]['description'][correlation_type])
    
    # trend
    key = 'L2-5'
    schema = find_dict_item(response['schema'], key)
    if y_numerical == False:
        schema['show'] = False
    else:
        data = df.iloc[:,1].tolist()
        trend_type = is_monotonic_function(data)
        if trend_type != 'non-monotonic':
            add_description(response, key, template[key]['tag'], template[key]['description'][trend_type])
        else:
            trend = get_trend(data)
            if len(trend) > config.THRESHOLD_TOTAL_INTERVALS:
                schema['show'] = False
            else:
                for x in trend:
                    x['names'] = (df.iloc[x['indices'][0],0], df.iloc[x['indices'][1],0])
                trend_text = get_trend_description(trend, chart['type'])
                add_description(response, key, template[key]['tag'], kw_en=[trend_text['en']], kw_fr=[trend_text['fr']])
