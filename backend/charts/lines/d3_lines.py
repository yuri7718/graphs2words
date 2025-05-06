from scipy.stats import pearsonr
from algorithm.color import *
from stats import *
from vis_helper import *
from algorithm.trend import *

import config

TAG_ASC = {'en': 'sharp increase', 'fr': 'forte augmentation'}
TAG_DESC = {'en': 'sharp decrease', 'fr': 'forte diminution'}

def add_d3_lines_option(response, chart, df, color):
    option = {}

    option['tooltip'] = {'trigger': 'axis'}

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
            'type': 'line',
            'data': df[col].tolist(),
            'showSymbol': chart['metadata']['visualize']['line-symbols'] if 'line-symbols' in chart['metadata']['visualize'] else None
        })

    response['visualize']['option'] = option



def add_d3_lines_description(response, chart, df, color, template):
    add_L1_description(response, chart, template['L1-info'])
    template = template['d3-lines']
    
    if len(df.columns) == 2:
        add_univariate_d3_lines_description(response, chart, df, color, template)
    else:
        add_multivariate_d3_lines_description(response, chart, df, color, template)

    

def add_univariate_d3_lines_description(response, chart, df, color, template):

    stats = df.iloc[:,1].describe()

    # x-axis
    key = 'L1-4-0'
    kw = [df.columns[0], df.iloc[0,0], df.iloc[-1,0]]
    add_description(response, key, template[key]['tag'], template[key]['description']['univariate'], kw, kw)

    # y-axis
    key = 'L1-4-1'
    kw = [df.columns[1], min(stats['min'].round(2), 0), max(0, stats['max'].round(2))]
    add_description(response, key, template[key]['tag'], template[key]['description']['univariate'], kw, kw)

    # color
    key = 'L1-5'
    if len(color) == 0:
        schema = find_dict_item(response['schema'], key)
        schema['show'] = False
    else:
        color_name = ColorName()
        c_name = color_name.nearest_neighbor_search(next(iter(color)))
        add_description(response, key, template[key]['tag'], template[key]['description']['single-color'], [c_name['en']], [c_name['fr']])

    # data points
    key = 'L2-0'
    data_points = [' '.join(x) for x in df.astype(str).values]
    kw_en, kw_fr = [list2str(data_points, 'en')], [list2str(data_points, 'fr')]
    add_description(response, key, template[key]['tag'], template[key]['description']['univariate'], kw_en, kw_fr)

    # maximum
    key = 'L2-1-0'
    idx = df.iloc[:,1].idxmax()
    kw = [df.iloc[idx,1].round(2), df.iloc[idx,0]]
    add_description(response, key, template[key]['tag'], template[key]['description']['univariate'], kw, kw)

    # minimum
    key = 'L2-1-1'
    idx = df.iloc[:,1].idxmin()
    kw = [df.iloc[idx,1].round(2), df.iloc[idx,0]]
    add_description(response, key, template[key]['tag'], template[key]['description']['univariate'], kw, kw)

    # mean
    key = 'L2-2-0'
    kw = [stats['mean'].round(2)]
    add_description(response, key, template[key]['tag'], template[key]['description']['univariate'], kw, kw)

    # std
    key = 'L2-2-1'
    kw = [stats['std'].round(2)]
    add_description(response, key, template[key]['tag'], template[key]['description']['univariate'], kw, kw)

    # median
    key = 'L2-2-2'
    kw = [stats['50%'].round(2)]
    add_description(response, key, template[key]['tag'], template[key]['description']['univariate'], kw, kw)

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
            'data': [{'coord': [int(x[1]), x[0]], 'value': x[0]} for x in outliers]
        }}

    # correlation
    key = 'L2-4'
    coefficient = pearsonr(np.arange(len(df)), df.iloc[:,1].tolist())
    if coefficient[1] >= 0.05:
        # correlation coefficient is not statistically significant
        schema = find_dict_item(response['schema'], key)
        schema['show'] = False
    else:
        correlation_type = get_correlation_type(coefficient)
        add_description(response, key, template[key]['tag'], template[key]['description']['univariate'][correlation_type])

    # trend
    key = 'L2-5'
    data = df.iloc[:,1].tolist()
    trend_type = is_monotonic_function(data)
    if trend_type != 'non-monotonic':
        add_description(response, key, template[key]['tag'], template[key]['description']['univariate'][trend_type])
    else:
        trend = get_trend(data)
        add_univariate_trend(trend, df, chart['type'], response, key, template[key]['tag'])


def add_multivariate_d3_lines_description(response, chart, df, color, template):
    
    # x-axis
    key = 'L1-4-0'
    kw = [df.columns[0], df.iloc[0,0], df.iloc[-1,0]]
    add_description(response, key, template[key]['tag'], template[key]['description']['multivariate'], kw, kw)


    # y-axis
    key = 'L1-4-1'
    dataset = df.iloc[:,1:].to_numpy()
    min_, max_ = round(dataset.min(), 2), round(dataset.max(), 2)
    kw_en = [list2str(df.columns[1:].tolist(), 'en'), min(min_, 0), max(0, max_)]
    kw_fr = [list2str(df.columns[1:].tolist(), 'fr'), min(min_, 0), max(0, max_)]
    add_description(response, key, template[key]['tag'], template[key]['description']['multivariate'], kw_en, kw_fr)


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
            color_name = ColorName()
            color_map = {}
            for i, c_node in enumerate(color):
                if c_node not in color_map:
                    c_name = color_name.nearest_neighbor_search(c_node)
                    color_map[c_node] = {'name': c_name, 'groups': [df.columns[i+1]]}
                else:
                    color_map[c_node]['groups'].append(df.columns[i+1])
            
            schema['children'] = []
            for i, (c_node,c_info) in enumerate(color_map.items()):
                key_child = '{}-{}'.format(key, i)
                schema['children'].append({'title': c_info['name'], 'key': key_child})
                
                tag = {k: '{} - {}'.format(v, c_info['name'][k]) for k, v in template[key]['tag'].items()}
                kw_en = [c_info['name']['en'], list2str(c_info['groups'], 'en')]
                kw_fr = [c_info['name']['fr'], list2str(c_info['groups'], 'fr')]
                add_description(response, key_child, tag, template[key]['description']['multi-color'], kw_en, kw_fr)
                
                response['visualCue'][key_child] = [
                    {'lineStyle': {'shadowColor': '#ffff00', 'shadowBlur': 10}} if col in c_info['groups'] else {} for col in df.columns[1:]
                ]

    # data points
    key = 'L2-0'
    schema = find_dict_item(response['schema'], key)
    schema['children'] = []
    for i, col in enumerate(df.columns[1:]):
        key_child = '{}-{}'.format(key, i)
        schema['children'].append({'title': {'en': col, 'fr': col}, 'key': key_child})
        
        data_points = [' '.join(x) for x in df[[df.columns[0], col]].astype(str).values]

        tag = {k: '{} - {}'.format(v, col) for k, v in template[key]['tag'].items()}
        kw_en = [col, list2str(data_points, 'en')]
        kw_fr = [col, list2str(data_points, 'fr')]
        add_description(response, key_child, tag, template[key]['description']['multivariate'], kw_en, kw_fr)
        
        response['visualCue'][key_child] = [
            {'lineStyle': {'shadowColor': '#ffff00', 'shadowBlur': 10}} if tmp_col == col else {} for tmp_col in df.columns[1:]
        ]

    # maximum
    key = 'L2-1-0'
    schema = find_dict_item(response['schema'], key)
    for i, col in enumerate(df.columns[1:]):
        idx = df[col].idxmax()
        kw = [col, df.iloc[idx,i+1].round(2), df.iloc[idx,0]]
        add_comparison(schema, col, col, key, i, template[key]['description']['multivariate'], kw, kw)
    add_description(response, key, template[key]['tag'], schema=schema)

    # minimum
    key = 'L2-1-1'
    schema = find_dict_item(response['schema'], key)
    for i, col in enumerate(df.columns[1:]):
        idx = df[col].idxmin()
        kw = [col, df.iloc[idx,i+1].round(2), df.iloc[idx,0]]
        add_comparison(schema, col, col, key, i, template[key]['description']['multivariate'], kw, kw)
    add_description(response, key, template[key]['tag'], schema=schema)

    # mean
    key = 'L2-2-0'
    schema = find_dict_item(response['schema'], key)
    for i, col in enumerate(df.columns[1:]):
        kw = [col, df[col].mean().round(2)]
        add_comparison(schema, col, col, key, i, template[key]['description']['multivariate'], kw, kw)
    add_description(response, key, template[key]['tag'], schema=schema)

    # std
    key = 'L2-2-1'
    schema = find_dict_item(response['schema'], key)
    for i, col in enumerate(df.columns[1:]):
        kw = [col, df[col].std().round(2)]
        add_comparison(schema, col, col, key, i, template[key]['description']['multivariate'], kw, kw)
    add_description(response, key, template[key]['tag'], schema=schema)

    # median
    key = 'L2-2-2'
    schema = find_dict_item(response['schema'], key)
    for i, col in enumerate(df.columns[1:]):
        kw = [col, df[col].median().round(2)]
        add_comparison(schema, col, col, key, i, template[key]['description']['multivariate'], kw, kw)
    add_description(response, key, template[key]['tag'], schema=schema)

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
        schema['children'] = []
        for i, (col,outliers) in enumerate(outlier_map.items()):
            key_child = '{}-{}'.format(key, i)
            schema['children'].append({'title': {'en': col, 'fr': col}, 'key': key_child})
            
            tag = {k: '{} - {}'.format(v, col) for k, v in template[key]['tag'].items()}
            outlier_text = get_outlier_description_group_wise(df, outliers, chart['type'], col=col)
            add_description(response, key_child, tag, kw_en=outlier_text['en'], kw_fr=outlier_text['fr'])
            
            response['visualCue'][key_child] = [{'markPoint': {
                'data': [{'coord': [int(x[1]), x[0]], 'value': x[0]} for x in outliers]
            }} if tmp_col == col else {} for tmp_col in df.columns[1:]]

    # correlation
    key = 'L2-4'
    schema = find_dict_item(response['schema'], key)

    correlation_map = {}
    for col in df.columns[1:]:
        coefficient = pearsonr(np.arange(len(df)), df[col].tolist())
        if coefficient[1] < 0.05:
            correlation_map[col] = get_correlation_type(coefficient)
    
    if len(correlation_map) == 0:
        schema['show'] = False
    else:
        schema['children'] = []
        for i, (col,correlation_type) in enumerate(correlation_map.items()):
            key_child = '{}-{}'.format(key, i)
            schema['children'].append({'title': {'en': col, 'fr': col}, 'key': key_child})
            
            tag = {k: '{} - {}'.format(v, col) for k, v in template[key]['tag'].items()}
            add_description(response, key_child, tag, template[key]['description']['multivariate'][correlation_type], [col], [col])

            response['visualCue'][key_child] = [{'lineStyle': {
                'shadowColor': '#ffff00', 'shadowBlur': 10
            }} if tmp_col == col else {} for tmp_col in df.columns[1:]]

    # trend
    key = 'L2-5'
    schema = find_dict_item(response['schema'], key)
    schema['children'] = []
    for i, col in enumerate(df.columns[1:]):
        key_child = '{}-{}'.format(key, i)
        schema['children'].append({'title': {'en': col, 'fr': col}, 'key': key_child})
        
        tag = {k: '{} - {}'.format(v, col) for k, v in template[key]['tag'].items()}
        data = df[col].tolist()
        trend_type = is_monotonic_function(data)
        if trend_type != 'non-monotonic':
            add_description(response, key_child, tag, template[key]['description']['multivariate'][trend_type], [col], [col])
            response['visualCue'][key_child] = [{'lineStyle': {
                'shadowColor': '#ffff00', 'shadowBlur': 10
            }} if tmp_col == col else {} for tmp_col in df.columns[1:]]
        else:
            trend = get_trend(data)
            add_multivariate_trend(trend, df, i, chart['type'], response, key_child, tag)