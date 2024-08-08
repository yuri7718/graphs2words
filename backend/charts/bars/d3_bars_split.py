import numpy as np
from copy import deepcopy
from vis_helper import *
from algorithm.color import ColorName
from stats import *
import config

def add_d3_bars_split_option(response, chart, df, color):
    
    BAR_WIDTH = 30
    GAP = 10

    n = len(df.columns) - 1
    
    label_width = df.iloc[:,0].astype(str).str.len().max()
    
    label_width_percentage = (np.log2(label_width) + 1) * 5
    label_width_number = (np.log(label_width) + 1) * 30

    left = [(100 - label_width_percentage) / n * i + label_width_percentage for i in range(n)]
    width = (100 - label_width_percentage - 10) / n

    option = {}
    
    # option['dataset'] = {
    #     'source': df.to_numpy().tolist(),
    #     'dimensions': df.columns.tolist()
    # }

    option['title'] = []
    for i in range(n):
        option['title'].append({
            'text': df.columns[i+1],
            'textStyle': {'fontSize': 12, 'fontWeight': 'normal'},
            'left': '{}%'.format(left[i]),
            'top': '5%'
        })

    option['grid'] = []
    for i in range(n):
        option['grid'].append({
            'left': '{}%'.format(left[i]),
            'width': '{}%'.format(width),
            'height': (BAR_WIDTH + GAP) * len(df)
        })

    option['xAxis'] = []
    for i in range(n):
        option['xAxis'].append({
            'type': 'value',
            'max': df.to_numpy()[:,1:].max(),
            'axisLabel': {'show': False},
            'splitLine': {'show': False},
            'gridIndex': i
        })

    option['yAxis'] = []
    for i in range(n):
        if i == 0:
            option['yAxis'].append({
                'type': 'category',
                'inverse': True,
                'axisLabel': {
                    'align': 'left',
                    'overflow': 'break',
                    'margin': label_width_number,
                    'width': label_width_number
                },
                'axisLine': {'show': False},
                'axisTick': {'show': False},
                'gridIndex': i,
                'data': df.to_numpy()[:,0].tolist()
            })
        else:
            option['yAxis'].append({
                'type': 'category',
                'inverse': True,
                'axisLabel': {'show': False},
                'axisLine': {'show': False},
                'axisTick': {'show': False},
                'gridIndex': i
            })

    option['series'] = []
    for i in range(n):
        if len(color) == len(df.to_numpy()[:,1:].flatten()):
            data = [{'value': x, 'itemStyle': {'color': c}} for x,c in zip(df.to_numpy()[:,i+1], color[i::n])]
        else:
            data = [{'value': x, 'itemStyle': {}} for x in df.to_numpy()[:,i+1]]
        option['series'].append({
            'type': 'bar',
            'barWidth': BAR_WIDTH,
            'label': {'show': True, 'position': 'insideLeft'},
            'showBackground': True,
            'xAxisIndex': i,
            'yAxisIndex': i,
            'data': data
        })
    
    response['visualize']['color'] = []
    for i in range(n):
        response['visualize']['color'].append(color[i::n])

    response['visualize']['option'] = option
    return response



def add_d3_bars_split_description(response, chart, df, color, template):
    add_L1_description(response, chart, template['L1-info'])
    template = template['d3-bars-split']

    # x-axis
    key = 'L1-4-0'
    kw_en = [list2str(df.columns[1:], 'en')]
    kw_fr = [list2str(df.columns[1:], 'fr')]
    add_description(response, key, template[key]['tag'], template[key]['description'], kw_en, kw_fr)

    # y-axis
    key = 'L1-4-1'
    kw_en = [df.columns[0], list2str(df.iloc[:,0].tolist(), 'en')]
    kw_fr = [df.columns[0], list2str(df.iloc[:,0].tolist(), 'fr')]
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
        case _:
            if colored_by_group(color, len(df.columns)-1):
                color = color[:len(df.columns)-1]
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
                    add_description(response, key_child, tag, template[key]['description']['colored-by-group'], kw_en, kw_fr)
                    
                    response['visualCue'][key_child] = [{'itemStyle': 
                        {'decal': config.DECAL}} if col in c_info['groups'] else {} for col in df.columns[1:]
                    ]
                    
            elif colored_by_item(color, len(df.columns)-1):
                color = color[::len(df.columns)-1]
                color_name = ColorName()
                color_map = {}
                for i, c_node in enumerate(color):
                    if c_node not in color_map:
                        c_name = color_name.nearest_neighbor_search(c_node)
                        color_map[c_node] = {'name': c_name, 'indices': [i]}
                    else:
                        color_map[c_node]['indices'].append(i)

                schema['children'] = []
                for i, (_,c_info) in enumerate(color_map.items()):
                    key_child = '{}-{}'.format(key, i)
                    schema['children'].append({'title': c_info['name'], 'key': key_child})

                    tag = {k: '{} - {}'.format(v, c_info['name'][k]) for k, v in template[key]['tag'].items()}
                    elements = df.iloc[c_info['indices'],0].tolist()
                    kw_en = [c_info['name']['en'], list2str(elements, 'en')]
                    kw_fr = [c_info['name']['fr'], list2str(elements, 'fr')]
                    add_description(response, key_child, tag, template[key]['description']['colored-by-element'], kw_en, kw_fr)
                    
                    response['visualCue'][key_child] = [{'data': deepcopy(x['data'])} for x in response['visualize']['option']['series']]
                    for x in response['visualCue'][key_child]:
                        for j, y in enumerate(x['data']):
                            if j in c_info['indices']:
                                y['itemStyle']['decal'] = config.DECAL
            
            else:
                add_description(response, key, template[key]['tag'])

    # data points
    key = 'L2-0'
    schema = find_dict_item(response['schema'], key)
    if len(df.columns) - 1 <= len(df):
        for i, col in enumerate(df.columns[1:]):
            key_child = '{}-{}'.format(key, i)
            schema['children'].append({'title': {'en': col, 'fr': col}, 'key': key_child})
            
            data_points = [' '.join(x) for x in df[[df.columns[0], col]].astype(str).values]

            tag = {k: '{} - {}'.format(v, col) for k, v in template[key]['tag'].items()}
            kw_en = [col, list2str(data_points, 'en')]
            kw_fr = [col, list2str(data_points, 'fr')]
            add_description(response, key_child, tag, template[key]['description']['group-wise'], kw_en, kw_fr)

            response['visualCue'][key_child] = [{
                'itemStyle': {'decal': config.DECAL}
            } if tmp_col == col else {} for tmp_col in df.columns[1:]]
    else: 
        for i in range(len(df)):
            key_child = '{}-{}'.format(key, i)
            schema['children'].append({'title': {'en': df.iloc[i,0], 'fr': df.iloc[i,0]}, 'key': key_child})
            
            col1 = df.columns[1:].to_numpy().reshape((-1,1))
            col2 = df.iloc[[i]].iloc[:,1:].astype(str).to_numpy().reshape((-1,1))
            data_points = [' '.join(x) for x in np.hstack((col1, col2))]

            tag = {k: '{} - {}'.format(v, df.iloc[i,0]) for k, v in template[key]['tag'].items()}
            kw_en = [df.iloc[i,0], list2str(data_points, 'en')]
            kw_fr = [df.iloc[i,0], list2str(data_points, 'fr')]
            add_description(response, key_child, tag, template[key]['description']['element-wise'], kw_en, kw_fr)

            response['visualCue'][key_child] = [{'data': deepcopy(x['data'])} for x in response['visualize']['option']['series']]
            for x in response['visualCue'][key_child]:
                for j, y in enumerate(x['data']):
                    if j == i: y['itemStyle']['decal'] = config.DECAL
    
    # maximum - group wise
    key = 'L2-1-0-0'
    schema = find_dict_item(response['schema'], key)
    for i, col in enumerate(df.columns[1:]):
        idx, max_ = df[col].idxmax(), df[col].max().round(2)
        kw = [col, df.iloc[idx,0], max_]
        add_comparison(schema, col, col, key, i, template[key]['description'], kw, kw)
    add_description(response, key, template[key]['tag'], schema=schema)
    response['visualCue'][key] = df.iloc[:,1:].to_numpy().argmax(axis=0).tolist()

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
    response['visualCue'][key] = df.iloc[:,1:].to_numpy().argmin(axis=0).tolist()

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

    # outliers
    outlier_map_group = {}
    for col in df.columns[1:]:
        outliers = get_outliers(df[col].tolist())
        if len(outliers) > 0: outlier_map_group[col] = outliers
    
    outlier_map_element = {}
    for i in range(len(df)):
        outliers = get_outliers(df.iloc[i,1:].tolist())
        if len(outliers) > 0: outlier_map_element[i] = outliers
    
    if len(outlier_map_group) == 0 and len(outlier_map_element) == 0:
        key = 'L2-3'
        schema = find_dict_item(response['schema'], key)
        schema['show'] = False
    else:
        # group wise
        key = 'L2-3-0'
        schema = find_dict_item(response['schema'], key)
        if len(outlier_map_group) == 0:
            schema['show'] = False
        else:
            for i, (col,outliers) in enumerate(outlier_map_group.items()):
                key_child = '{}-{}'.format(key, i)
                schema['children'].append({'title': {'en': col, 'fr': col}, 'key': key_child})

                tag = {k: '{} - {}'.format(v, col) for k,v in template[key]['tag'].items()}
                outlier_text = get_outlier_description_group_wise(df, outliers, chart['type'], col=col)
                add_description(response, key_child, tag, kw_en=outlier_text['en'], kw_fr=outlier_text['fr'])
                
                idx = df.columns[1:].tolist().index(col)
                data = deepcopy(response['visualize']['option']['series'][idx]['data'])
                indices = [x[1] for x in outliers]
                for j, x in enumerate(data):
                    if j in indices: x['itemStyle']['decal'] = config.DECAL
                response['visualCue'][key_child] = [{'data': data} if tmp_col == col else {} for tmp_col in df.columns[1:]]

        # element wise
        key = 'L2-3-1'
        schema = find_dict_item(response['schema'], key)
        if len(outlier_map_element) == 0:
            schema['show'] = False
        else:
            for i, (idx,outliers) in enumerate(outlier_map_element.items()):
                key_child = '{}-{}'.format(key, i)
                schema['children'].append({'title': {'en': df.iloc[idx,0], 'fr': df.iloc[idx,0]}, 'key': key_child})

                tag = {k: '{} - {}'.format(v, df.iloc[idx,0]) for k, v in template[key]['tag'].items()}
                outlier_text = get_outlier_description_element_wise(df, outliers, chart['type'], element=df.iloc[idx,0])
                add_description(response, key_child, tag, kw_en=outlier_text['en'], kw_fr=outlier_text['fr'])

                indices = [x[1] for x in outliers]
                response['visualCue'][key_child] = [{'data': deepcopy(x['data'])} for x in response['visualize']['option']['series']]
                for j, x in enumerate(response['visualCue'][key_child]):
                    if j in indices: x['data'][idx]['itemStyle']['decal'] = config.DECAL

def colored_by_group(color, n):
    for i in range(n):
        if len(set(color[i::n])) != 1:
            return False
    return True

def colored_by_item(color, n):
    for i in range(0, len(color), n):
        if len(set(color[i:i+n])) != 1:
            return False
    return True