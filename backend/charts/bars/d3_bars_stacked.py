from copy import deepcopy
from scipy.stats import pearsonr
import numpy as np
from charts.bars.d3_bars import add_d3_bars_description
from vis_helper import *
from algorithm.color import *
from stats import get_outliers
from algorithm.trend import *
import config

N_DATA_THRESHOLD = 5

def add_d3_bars_stacked_option(response, chart, df, color):
    n = len(df.columns) - 1

    option = {}

    # option['dataset'] = {
    #     'source': df.to_numpy().tolist(),
    #     'dimensions': df.columns.tolist()
    # }

    option['tooltip'] = {}
    
    option['grid'] = {'containLabel': True}

    option['xAxis'] = {'type': 'value'}
    option['yAxis'] = {
        'type': 'category',
        'inverse': True,
        'data': df.iloc[:,0].tolist()
    }

    option['color'] = color

    # option['series'] = [{'type': 'bar', 'stack': 'stacked'}] * n
    option['series'] = []
    for col in df.columns[1:]:
        option['series'].append({
            'type': 'bar',
            'stack': 'stacked',
            'data': df[col].map(lambda x: {'value': x}).tolist()
        })

    response['visualize']['threshold'] = np.max(np.abs(df.to_numpy()[:,1:])) / 5

    response['visualize']['option'] = option




def add_d3_bars_stacked_description(response, chart, df, color, template):

    if len(df.columns) == 2:
        chart['type'] = 'd3-bars'
        add_d3_bars_description(response, chart, df, color, template)
        return
    
    add_L1_description(response, chart, template['L1-info'])
    template = template['d3-bars-stacked']

    df_totals = pd.concat([df.iloc[:,0], df.iloc[:,1:].cumsum(axis=1)], axis=1)
    y_numerical = is_numerical(df.iloc[:,0])

    # x-axis
    key = 'L1-4-0'
    min_, max_ = df_totals.iloc[:,-1].min().round(2), df_totals.iloc[:,-1].max().round(2)
    kw_en = [list2str(df.columns[1:].tolist(), 'en'), min(min_, 0), max(0, max_)]
    kw_fr = [list2str(df.columns[1:].tolist(), 'fr'), min(min_, 0), max(0, max_)]
    add_description(response, key, template[key]['tag'], template[key]['description'], kw_en, kw_fr)

    # y-axis
    key = 'L1-4-1'
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
            c_name = color_name.nearest_neighbor_search(next(iter(color)))
            add_description(response, key, template[key]['tag'], template[key]['description']['single-color'], [c_name['en']], [c_name['fr']])         
            response['visualCue'][key] = [{'itemStyle': {'decal': config.DECAL}} for _ in df.columns[1:]]
        case _:
            color_name = ColorName()
            color_map = {}
            for i, c_node in enumerate(color):
                if c_node not in color_map:
                    c_name = color_name.nearest_neighbor_search(c_node)
                    color_map[c_node] = {'name': c_name, 'groups': [df.columns[i+1]]}
                else:
                    color_map[c_node]['groups'].append(df.columns[i+1])
            
            schema['children'] = []
            for i, (_,c_info) in enumerate(color_map.items()):
                key_child = '{}-{}'.format(key, i)
                schema['children'].append({'title': c_info['name'], 'key': key_child})

                tag = {k: '{} - {}'.format(v, c_info['name'][k]) for k, v in template[key]['tag'].items()}
                kw_en = [c_name['en'], list2str(c_info['groups'], 'en')]
                kw_fr = [c_name['fr'], list2str(c_info['groups'], 'fr')]
                add_description(response, key_child, tag, template[key]['description']['multi-color'], kw_en, kw_fr)
                
                response['visualCue'][key_child] = [
                    {'itemStyle': {'decal': config.DECAL}} if col in c_info['groups'] else {} for col in df.columns[1:]
                ]
     
    # data points - aggregate values
    key = 'L2-0-0'
    data_points = [' '.join(x) for x in df_totals[[df.columns[0], df.columns[-1]]].round(2).astype(str).values]
    kw_en = [list2str(data_points, 'en')]
    kw_fr = [list2str(data_points, 'fr')]
    add_description(response, key, template[key]['tag'], template[key]['description'], kw_en, kw_fr)
    response['visualCue'][key] = [{'itemStyle': {'decal': config.DECAL}} for _ in df.columns[1:]]

    # data points - category wise
    key = 'L2-0-1'
    schema = find_dict_item(response['schema'], key)
    for i, col in enumerate(df.columns[1:]):
        key_child = '{}-{}'.format(key, i)
        schema['children'].append({'title': {'en': col, 'fr': col}, 'key': key_child})

        data_points = [' '.join(x) for x in df[[df.columns[0], col]].round(2).astype(str).values]

        tag = {k: '{} - {}'.format(v, col) for k, v in template[key]['tag'].items()}
        kw_en = [col, list2str(data_points, 'en')]
        kw_fr = [col, list2str(data_points, 'fr')]
        add_description(response, key_child, tag, template[key]['description'], kw_en, kw_fr)
        
        response['visualCue'][key_child] = [{
            'itemStyle': {'decal': config.DECAL}
        } if tmp_col == col else {} for tmp_col in df.columns[1:]]

    # maximum - aggregate values
    key = 'L2-1-0-0'
    idx, max_ = df_totals.iloc[:,-1].idxmax(), df_totals.iloc[:,-1].max().round(2)
    kw = [df.iloc[idx,0], max_]
    add_description(response, key, template[key]['tag'], template[key]['description'], kw, kw)
    response['visualCue'][key] = {'markPoint': {
        'data': [{
            'coord': [max_, idx],
            'value': max_,
            'symbolRotate': 270,
            'label': {'offset': [6,3]}
        }]
    }}

    # maximum - group wise
    key = 'L2-1-0-1'
    schema = find_dict_item(response['schema'], key)
    response['visualCue'][key] = []
    for i, col in enumerate(df.columns[1:]):
        idx, max_ = df[col].idxmax(), df[col].max().round(2)
        kw = [col, df.iloc[idx,0], max_]
        add_comparison(schema, col, col, key, i, template[key]['description'], kw, kw)
    add_description(response, key, template[key]['tag'], schema=schema)
    response['visualCue'][key] = df.iloc[:,1:].to_numpy().argmax(axis=0).tolist()
    
    # maximum - element wise
    key = 'L2-1-0-2'
    schema = find_dict_item(response['schema'], key)
    for i in range(len(df)):
        idx, max_ = df.iloc[i,1:].to_numpy().argmax(), df.iloc[i,1:].max().round(2)
        kw = [df.iloc[i,0], df.columns[idx+1], max_]
        add_comparison(schema, df.iloc[i,0], df.iloc[i,0], key, i, template[key]['description'], kw, kw)
    add_description(response, key, template[key]['tag'], schema=schema)
    response['visualCue'][key] = df.iloc[:,1:].to_numpy().argmax(axis=1).tolist()

    # minimum - aggregate values
    key = 'L2-1-1-0'
    idx, min_ = df_totals.iloc[:,-1].idxmin(), df_totals.iloc[:,-1].min().round(2)
    kw = [df.iloc[idx,0], min_]
    add_description(response, key, template[key]['tag'], template[key]['description'], kw, kw)
    response['visualCue'][key] = {'markPoint': {
        'data': [{
            'coord': [min_, idx],
            'value': min_,
            'symbolRotate': 270,
            'label': {'offset': [6,3]}
        }]
    }}

    # minimum - group wise
    key = 'L2-1-1-1'
    schema = find_dict_item(response['schema'], key)
    for i, col in enumerate(df.columns[1:]):
        idx, min_ = df[col].idxmin(), df[col].min().round(2)
        kw = [col, df.iloc[idx,0], min_]
        add_comparison(schema, col, col, key, i, template[key]['description'], kw, kw)
    add_description(response, key, template[key]['tag'], schema=schema)
    response['visualCue'][key] = df.iloc[:,1:].to_numpy().argmin(axis=0).tolist()

    # minimum - element wise
    key = 'L2-1-1-2'
    schema = find_dict_item(response['schema'], key)
    for i in range(len(df)):
        idx, min_ = df.iloc[i,1:].to_numpy().argmin(), df.iloc[i,1:].min().round(2)
        kw = [df.iloc[i,0], df.columns[idx+1], min_]
        add_comparison(schema, df.iloc[i,0], df.iloc[i,0], key, i, template[key]['description'], kw, kw)
    add_description(response, key, template[key]['tag'], schema=schema)
    response['visualCue'][key] = df.iloc[:,1:].to_numpy().argmin(axis=1).tolist()

    # mean
    key = 'L2-2-0'
    mean_ = df_totals.iloc[:,-1].mean().round(2)
    kw = [mean_]
    add_description(response, key, template[key]['tag'], template[key]['description'], kw, kw)
    response['visualCue'][key] = {'markLine': {'data': [{'xAxis': mean_}]}}

    # std
    key = 'L2-2-1'
    std_ = df_totals.iloc[:,-1].std().round(2)
    kw = [std_]
    add_description(response, key, template[key]['tag'], template[key]['description'], kw, kw)

    # median
    key = 'L2-2-2'
    median_ = df_totals.iloc[:,-1].median().round(2)
    kw = [median_]
    add_description(response, key, template[key]['tag'], template[key]['description'], kw, kw)
    response['visualCue'][key] = {'markLine': {'data': [{'xAxis': median_}]}}

    # outliers
    outliers_totals = get_outliers(df_totals.iloc[:,-1].tolist())

    outlier_map_group = {}
    for col in df.columns[1:]:
        outliers = get_outliers(df[col].tolist())
        if len(outliers) > 0: outlier_map_group[col] = outliers
    
    outlier_map_element = {}
    for i in range(len(df)):
        outliers = get_outliers(df.iloc[i,1:].tolist())
        if len(outliers) > 0: outlier_map_element[i] = outliers
    
    if all(len(x) == 0 for x in [outliers_totals, outlier_map_group, outlier_map_element]):
        key = 'L2-3'
        schema = find_dict_item(response['schema'], key)
        schema['show'] = False
    else:
        # aggregate values
        key = 'L2-3-0'
        if len(outliers_totals) == 0:
            schema = find_dict_item(response['schema'], key)
            schema['show'] = False
        else:
            outlier_text = get_outlier_description_group_wise(df, outliers_totals, chart['type'])
            add_description(response, key, template[key]['tag'], kw_en=outlier_text['en'], kw_fr=outlier_text['fr'])
            response['visualCue'][key] = {'markPoint':{
                'data': [{
                    'coord': [x[0], x[1]],
                    'value': x[0],
                    'symbolRotate': 270,
                    'label': {'offset': [6,3]}
                } for x in outliers_totals]
            }}

        # group wise
        key = 'L2-3-1'
        schema = find_dict_item(response['schema'], key)
        if len(outlier_map_group) == 0: schema['show'] = False
        else:
            for i, (col,outliers) in enumerate(outlier_map_group.items()):
                key_child = '{}-{}'.format(key, i)
                schema['children'].append({'title': {'en': col, 'fr': col}, 'key': key_child})

                tag = {k: '{} - {}'.format(v, col) for k, v in template[key]['tag'].items()}
                outlier_text = get_outlier_description_group_wise(df, outliers, chart['type'], col=col)
                add_description(response, key_child, tag, kw_en=outlier_text['en'], kw_fr=outlier_text['fr'])

                idx = df.columns[1:].tolist().index(col)
                data = deepcopy(response['visualize']['option']['series'][idx]['data'])
                indices = [x[1] for x in outliers]
                for j, x in enumerate(data):
                    if j in indices: x['itemStyle'] = {'decal': config.DECAL}
                response['visualCue'][key_child] = [{'data': data} if tmp_col == col else {} for tmp_col in df.columns[1:]]
                
        # element wise
        key = 'L2-3-2'
        schema = find_dict_item(response['schema'], key)
        if len(outlier_map_element) == 0: schema['show'] = False
        else:
            for i, (idx,outliers) in enumerate(outlier_map_element.items()):
                key_child = '{}-{}'.format(key, i)
                schema['children'].append({'title': {'en': df.iloc[idx,0], 'fr': df.iloc[idx,0]}, 'key': key_child})

                tag = {k: '{} - {}'.format(v, df.iloc[idx,0]) for k, v in template[key]['tag'].items()}
                outlier_text = get_outlier_description_element_wise(df, outliers, chart['type'], df.iloc[idx,0])
                add_description(response, key_child, tag, kw_en=outlier_text['en'], kw_fr=outlier_text['fr'])

                indices = [x[1] for x in outliers]
                response['visualCue'][key_child] = [{'data': deepcopy(x['data'])} for x in response['visualize']['option']['series']]
                for j, x in enumerate(response['visualCue'][key_child]):
                    if j in indices: x['data'][idx]['itemStyle'] = {'decal': config.DECAL}

    # correlation
    key = 'L2-4'
    schema = find_dict_item(response['schema'], key)
    if y_numerical == False:
        schema['show'] = False
    else:
        coefficient = pearsonr(np.arange(len(df)), df_totals.iloc[:,-1].tolist())
        if coefficient[1] >= 0.05:
            schema['show'] = False
        else:
            correlation_type = get_correlation_type(coefficient)
            add_description(response, key, template[key]['tag'], template[key]['description'][correlation_type])
            response['visualCue'][key] = [{'itemStyle': {'decal': config.DECAL}} for _ in df.columns[1:]]
    
    # trend
    key = 'L2-5'
    schema = find_dict_item(response['schema'], key)
    if y_numerical == False:
        schema['show'] = False
    else:
        data = df_totals.iloc[:,-1].tolist()
        trend_type = is_monotonic_function(data)
        if trend_type != 'non-monotonic':
            add_description(response, key, template[key]['tag'], template[key]['description'][trend_type])
            response['visualCue'][key] = [{'itemStyle': {'decal': config.DECAL}} for _ in df.columns[1:]]
        else:
            trend = get_trend(data)
            if len(trend) > config.THRESHOLD_TOTAL_INTERVALS:
                schema['show'] = False
            else:
                for x in trend:
                    x['names'] = (df.iloc[x['indices'][0],0], df.iloc[x['indices'][1],0])
                trend_text = get_trend_description(trend, chart['type'])
                add_description(response, key, template[key]['tag'], kw_en=[trend_text['en']], kw_fr=[trend_text['fr']])
                response['visualCue'][key] = [{'itemStyle': {'decal': config.DECAL}} for _ in df.columns[1:]]
