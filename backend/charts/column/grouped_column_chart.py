from scipy.stats import pearsonr
from algorithm.color import *
from vis_helper import *
from algorithm.trend import *
from stats import *

import config

def add_grouped_column_chart_option(response, chart, df, color):
    option = {}

    option['tooltip'] = {}

    option['xAxis'] = {
        'type': 'category',
        'data': df.iloc[:,0].tolist(),
        'axisTick': {'show': False}
    }
    option['yAxis'] = {'type': 'value'}

    if color:
        option['color'] = color
    
    option['series'] = []
    for col in df.columns[1:]:
        option['series'].append({
            'type': 'bar',
            'data': df[col].map(lambda x: {'value': x}).tolist()
        })

    response['visualize']['option'] = option


def add_grouped_column_chart_description(response, chart, df, color, template):
    add_L1_description(response, chart, template['L1-info'])
    template = template['grouped-column-chart']

    x_numerical = is_numerical(df.iloc[:,0])
    # x-axis
    key = 'L1-4-0'
    if x_numerical:
        kw = [df.columns[0], df.iloc[0,0], df.iloc[-1,0]]
        add_description(response, key, template[key]['tag'], template[key]['description']['numerical'], kw, kw)
    else:
        kw_en = [df.columns[0], list2str(df.iloc[:,0].tolist(), 'en')]
        kw_fr = [df.columns[0], list2str(df.iloc[:,0].tolist(), 'fr')]
        add_description(response, key, template[key]['tag'], template[key]['description']['categorical'], kw_en, kw_fr)

    # y-axis
    key = 'L1-4-1'
    dataset = df.iloc[:,1:].to_numpy()
    min_, max_ = dataset.min().round(2), dataset.max().round(2)
    kw_en = [list2str(df.columns[1:].tolist(), 'en'), min(min_, 0), max(0, max_)]
    kw_fr = [list2str(df.columns[1:].tolist(), 'fr'), min(min_, 0), max(0, max_)]
    add_description(response, key, template[key]['tag'], template[key]['description'], kw_en, kw_fr)

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
                kw_en = [c_info['name']['en'], list2str(c_info['groups'], 'en')]
                kw_fr = [c_info['name']['fr'], list2str(c_info['groups'], 'fr')]
                add_description(response, key_child, tag, template[key]['description']['multi-color'], kw_en, kw_fr)
                
                response['visualCue'][key_child] = [
                    {'itemStyle': {'decal': config.DECAL}} if col in c_info['groups'] else {} for col in df.columns[1:]
                ]
    
    # data points
    key = 'L2-0'
    schema = find_dict_item(response['schema'], key)
    for i, col in enumerate(df.columns[1:]):
        key_child = '{}-{}'.format(key, i)
        schema['children'].append({'title': {'en': col, 'fr': col}, 'key': key_child})

        data_points = [' '.join(x) for x in df[[df.columns[0], col]].round(2).astype(str).values]

        tag = {k: '{} - {}'.format(v, col) for k, v in template[key]['tag'].items()}
        kw_en=[col, list2str(data_points, 'en')]
        kw_fr=[col, list2str(data_points, 'fr')]
        add_description(response, key_child, tag, template[key]['description'], kw_en, kw_fr)

        response['visualCue'][key_child] = [{
            'itemStyle': {'decal': config.DECAL}
        } if tmp_col == col else {} for tmp_col in df.columns[1:]]

    # maximum - group wise
    key = 'L2-1-0-0'
    schema = find_dict_item(response['schema'], key)
    for i, col in enumerate(df.columns[1:]):
        idx, max_ = df[col].idxmax(), df[col].max().round(2)
        kw = [col, df.iloc[idx,0], max_]
        add_comparison(schema, col, col, key, i, template[key]['description'], kw, kw)
    add_description(response, key, template[key]['tag'], schema=schema)
    
    # maximum - element wise
    key = 'L2-1-0-1'
    schema = find_dict_item(response['schema'], key)
    for i in range(len(df)):
        idx, max_ = df.iloc[i,1:].to_numpy().argmax(), df.iloc[i,1:].max().round(2)
        kw = [df.iloc[i,0], df.columns[idx+1], max_]
        add_comparison(schema, df.iloc[i,0], df.iloc[i,0], key, i, template[key]['description'], kw, kw)
    add_description(response, key, template[key]['tag'], schema=schema)
    response['visualCue'][key] = df.iloc[:,1:].to_numpy().argmax(axis=1).tolist()

    # minimum - group wise
    key = 'L2-1-1-0'
    schema = find_dict_item(response['schema'], key)
    for i, col in enumerate(df.columns[1:]):
        idx, min_ = df[col].idxmin(), df[col].min().round(2)
        kw = [col, df.iloc[idx,0], min_]
        add_comparison(schema, col, col, key, i, template[key]['description'], kw, kw)
    add_description(response, key, template[key]['tag'], schema=schema)

    # minimum - element wise
    key = 'L2-1-1-1'
    schema = find_dict_item(response['schema'], key)
    for i in range(len(df)):
        idx, min_ = df.iloc[i,1:].to_numpy().argmin(), df.iloc[i,1:].min().round(2)
        kw = [df.iloc[i,0], df.columns[idx+1], min_]
        add_comparison(schema, df.iloc[i,0], df.iloc[i,0], key, i, template[key]['description'], kw, kw)
    add_description(response, key, template[key]['tag'], schema=schema)
    response['visualCue'][key] = df.iloc[:,1:].to_numpy().argmin(axis=1).tolist()
    
    # mean - group wise
    key = 'L2-2-0-0'
    schema = find_dict_item(response['schema'], key)
    for i, col in enumerate(df.columns[1:]):
        kw = [col, df[col].mean().round(2)]
        add_comparison(schema, col, col, key, i, template[key]['description'], kw, kw)
    add_description(response, key, template[key]['tag'], schema=schema)
    
    # mean - element wise
    key = 'L2-2-0-1'
    schema = find_dict_item(response['schema'], key)
    for i in range(len(df)):
        kw = [df.iloc[i,0], df.iloc[i,1:].mean().round(2)]
        add_comparison(schema, df.iloc[i,0], df.iloc[i,0], key, i, template[key]['description'], kw, kw)
    add_description(response, key, template[key]['tag'], schema=schema)
    response['visualCue'][key] = df.iloc[:,1:].to_numpy().mean(axis=1).tolist()

    # std - group wise
    key = 'L2-2-1-0'
    schema = find_dict_item(response['schema'], key)
    for i, col in enumerate(df.columns[1:]):
        kw = [col, df[col].std().round(2)]
        add_comparison(schema, col, col, key, i, template[key]['description'], kw, kw)
    add_description(response, key, template[key]['tag'], schema=schema)

    # std - element wise
    key = 'L2-2-1-1'
    schema = find_dict_item(response['schema'], key)
    for i in range(len(df)):
        kw = [df.iloc[i,0], df.iloc[i,1:].std().round(2)]
        add_comparison(schema, df.iloc[i,0], df.iloc[i,0], key, i, template[key]['description'], kw, kw)
    add_description(response, key, template[key]['tag'], schema=schema)
    
    # median - group wise
    key = 'L2-2-2-0'
    schema = find_dict_item(response['schema'], key)
    for i, col in enumerate(df.columns[1:]):
        kw = [col, df[col].median().round(2)]
        add_comparison(schema, col, col, key, i, template[key]['description'], kw, kw)
    add_description(response, key, template[key]['tag'], schema=schema)

    # median - element wise
    key = 'L2-2-2-1'
    schema = find_dict_item(response['schema'], key)
    for i in range(len(df)):
        kw = [df.iloc[i,0], df.iloc[i,1:].median().round(2)]
        add_comparison(schema, df.iloc[i,0], df.iloc[i,0], key, i, template[key]['description'], kw, kw)
    add_description(response, key, template[key]['tag'], schema=schema)
    response['visualCue'][key] = np.median(df.iloc[:,1:].to_numpy(), axis=1).tolist()

    # outliers
    key = 'L2-3'
    schema = find_dict_item(response['schema'], key)
    
    outlier_map = {}
    for col in df.columns[1:]:
        outliers = get_outliers(df[col].tolist())
        if len(outliers) > 0:
            outlier_map[col] = outliers
    
    if len(outlier_map) == 0:
        schema['show'] = False
    else:
        for i, (col,outliers) in enumerate(outlier_map.items()):
            key_child = '{}-{}'.format(key, i)
            schema['children'].append({'title': {'en': col, 'fr': col}, 'key': key_child})

            tag = {k: '{} - {}'.format(v, col) for k, v in template[key]['tag'].items()}
            outlier_text = get_outlier_description_group_wise(df, outliers, chart['type'], col=col)
            add_description(response, key_child, tag, kw_en=outlier_text['en'], kw_fr=outlier_text['fr'])
            
            idx = df.columns[1:].tolist().index(col)
            response['visualCue'][key_child] = [{
                'markPoint': {'data': [{
                    'coord': [x[1], x[0]],
                    'value': x[0],
                    'symbolRotate': 0 if x[0] >= 0 else 180,
                    'label': {'offset': [0,0] if x[0] >= 0 else [0,9]},
                } for x in outliers]}
            } if tmp_col == col else {} for tmp_col in df.columns[1:]]

    # correlation
    key = 'L2-4'
    schema = find_dict_item(response['schema'], key)
    if x_numerical == False:
        schema['show'] = False
    else:
        correlation_map = {}
        for col in df.columns[1:]:
            coefficient = pearsonr(np.arange(len(df)), df[col].tolist())
            if coefficient[1] < 0.05:
                correlation_map[col] = get_correlation_type(coefficient)
        if len(correlation_map) == 0:
            schema['show'] = False
        else:
            for i, (col,correlation_type) in enumerate(correlation_map.items()):
                key_child = '{}-{}'.format(key, i)
                schema['children'].append({'title': {'en': col, 'fr': col}, 'key': key_child})
                
                tag = {k: '{} - {}'.format(v, col) for k, v in template[key]['tag'].items()}
                add_description(response, key_child, tag, template[key]['description'][correlation_type], [col], [col])

                response['visualCue'][key_child] = [{
                    'itemStyle': {'decal': config.DECAL}
                } if tmp_col == col else {} for tmp_col in df.columns[1:]]

    # trend
    key = 'L2-5'
    schema = find_dict_item(response['schema'], key)
    if x_numerical == False:
        schema['show'] = False
    else:
        for i, col in enumerate(df.columns[1:]):
            key_child = '{}-{}'.format(key, i)
            schema['children'].append({'title': {'en': col, 'fr': col}, 'key': key_child})

            tag = {k: '{} - {}'.format(v, col) for k, v in template[key]['tag'].items()}
            data = df[col].tolist()
            trend_type = is_monotonic_function(data)
            if trend_type != 'non-monotonic':
                add_description(response, key_child, tag, template[key]['description'][trend_type], [col], [col])
                response['visualCue'][key_child] = [{
                    'itemStyle': {'decal': config.DECAL}
                } if tmp_col == col else {} for tmp_col in df.columns[:]]
            else:
                trend = get_trend(data)
                add_multivariate_trend(trend, df, i, chart['type'], response, key_child, tag)