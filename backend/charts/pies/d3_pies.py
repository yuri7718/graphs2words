from algorithm.color import *
from vis_helper import *
from stats import *


def add_d3_pies_option(response, chart, df, color):
    
    option = {}
    option['dataset'] = {'source': df.to_numpy().tolist(), 'dimensions': df.columns.tolist()}
    option['tooltip'] = {'trigger': 'item'}

    if color:
        option['color'] = color
    
    option['series'] = [{
        'type': 'pie',
        'radius': '50%'
    }]

    response['visualize']['option'] = option



def add_d3_pies_description(response, chart, df, color: list[str], template):
    add_L1_description(response, chart, template['L1-info'])
    template = template['d3-pies']

    # order
    key = 'L1-4'
    SLICE_ORDER = chart['metadata']['visualize']['slice_order']
    if SLICE_ORDER == 'ascending' or SLICE_ORDER == 'descending':
        kw_en = ['ascending'] if SLICE_ORDER == 'ascending' else ['descending']
        kw_fr = ['croissant'] if SLICE_ORDER == 'ascending' else ['décroissant']
        add_description(response, key, template[key]['tag'], template[key]['description'], kw_en, kw_fr)
    else:
        schema = find_dict_item(response['schema'], key)
        schema['show'] = False

    # color
    key = 'L1-5'
    schema = find_dict_item(response['schema'], key)
    match len(set(color)):
        case 0:
            schema['show'] = False
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
            for i, (_,c_info) in enumerate(color_map.items()):
                key_child = '{}-{}'.format(key, i)
                schema['children'].append({'title': c_info['name'], 'key': key_child})

                elements = df.iloc[c_info['indices'],0].tolist()
                kw_en = [c_name['en'], list2str(elements, 'en')]
                kw_fr = [c_name['fr'], list2str(elements, 'fr')]
                add_description(response, key_child, template[key]['tag'], template[key]['description'], kw_en, kw_fr)

                response['visualCue'][key_child] = {
                    'enabled': True,
                    'decal': {
                        'show': True,
                        'decals': [{'symbol': 'circle'} if j in c_info['indices'] else {'symbol': 'none'} for j in range(len(df))]
                    }
                }

    # data points
    key = 'L2-0'
    data_points = [' '.join(map(str, x)) for x in df.values]
    kw_en = [list2str(data_points, 'en')]
    kw_fr = [list2str(data_points, 'fr')]
    add_description(response, key, template[key]['tag'], template[key]['description'], kw_en, kw_fr)

    # maximum
    key = 'L2-1-0'
    idx, max_ = df.iloc[:,1].idxmax(), df.iloc[:,1].max().round(2)
    kw = [df.iloc[idx,0], max_]
    add_description(response, key, template[key]['tag'], template[key]['description'], kw, kw)
    response['visualCue'][key] = {
        'enabled': True,
        'decal': {
            'show': True,
            'decals': [{'symbol': 'circle'} if i == idx else {'symbol': 'none'} for i in range(len(df))]
        }
    }

    # minimum
    key = 'L2-1-1'
    idx, min_ = df.iloc[:,1].idxmin(), df.iloc[:,1].min().round(2)
    kw = [df.iloc[idx,0], min_]
    add_description(response, key, template[key]['tag'], template[key]['description'], kw, kw)
    response['visualCue'][key] = {
        'enabled': True,
        'decal': {
            'show': True,
            'decals': [{'symbol': 'circle'} if i == idx else {'symbol': 'none'} for i in range(len(df))]
        }
    }

    # outliers
    key = 'L2-2'
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
            kw_en=outlier_text['en'],
            kw_fr=outlier_text['fr']
        )

        indices = [x[1] for x in outliers]
        response['visualCue'][key] = {
            'enabled': True,
            'decal': {
                'show': True,
                'decals': [{'symbol': 'circle'} if i in indices else {'symbol': 'none'} for i in range(len(df))]
            }
        }