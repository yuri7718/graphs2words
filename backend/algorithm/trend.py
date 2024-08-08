import numpy as np


def is_monotonic_function(data):
    diff = np.diff(data)
    if np.all(diff == 0):
        return 'constant'
    if np.all(diff >= 0):
        return 'increasing'
    if np.all(diff <= 0):
        return 'decreasing'
    else:
        return 'non-monotonic'


def get_trend(data):
    def get_intervals(data, order):
        if len(data) == 0:
            return []
        intervals = np.split(data, np.where(np.diff(data) != 1)[0] + 1)
        result = []
        for x in intervals:
            i, j = x[0], x[-1] + 1
            result.append({'indices': (i, j), 'order': order})
        return result

    indices_asc = np.where(np.diff(data) > 0)[0]
    indices_const = np.where(np.diff(data) == 0)[0]
    indices_desc = np.where(np.diff(data) < 0)[0]

    intervals = get_intervals(indices_asc, 'asc') + get_intervals(indices_const, 'const') + get_intervals(indices_desc, 'desc')
    intervals.sort(key=lambda x: x['indices'][0])
    return intervals


def get_trend_description(trend, chart_type, col=None):
    match chart_type:
        case 'd3-bars' | 'd3-bars-grouped' | 'column-chart' | 'grouped-column-chart' | 'd3-lines':
            kw_en = "The data for {} ".format(col) if col else "The data "
            kw_fr = "Les données pour {} ".format(col) if col else "Les données "
        case 'd3-bars-stacked' | 'stacked-column-chart' | 'd3-area':
            kw_en = "The aggregate values for {} ".format(col) if col else "The aggregate values "
            kw_fr = "Les valeurs agrégées pour {} ".format(col) if col else "Les valeurs agrégées "
        case _:
            kw_en = ""
            kw_fr = ""

    asc_en = "increase from {} to {}, "
    desc_en = "decrease from {} to {}, "
    const_en = "stay constant from {} to {}, "

    asc_fr = "augmentent de {} à {}, "
    desc_fr = "diminuent de {} à {}, "
    const_fr = "restent constantes de {} à {}, "

    for i, x in enumerate(trend):
        if i != 0 and i == len(trend) - 1:
            kw_en += 'and '
            kw_fr += 'et '
        match x['order']:
            case 'asc':
                kw_en += asc_en.format(x['names'][0], x['names'][1])
                kw_fr += asc_fr.format(x['names'][0], x['names'][1])
            case 'desc':
                kw_en += desc_en.format(x['names'][0], x['names'][1])
                kw_fr += desc_fr.format(x['names'][0], x['names'][1])
            case 'const':
                kw_en += const_en.format(x['names'][0], x['names'][1])
                kw_fr += const_fr.format(x['names'][0], x['names'][1])
  
    kw_en = kw_en[:-2] + '.'
    kw_fr = kw_fr[:-2] + '.'

    return {'en': kw_en, 'fr': kw_fr}


def get_trend_specific_description(trend, order, col=None):
    TREND_EN = {'asc': 'increase', 'desc': 'decrease'}
    TREND_FR = {'asc': 'augmentation', 'desc': 'diminution'}

    if col:
        kw_en = "The intervals where the data for {} have a sharp {} are: ".format(col, TREND_EN[order])
        kw_fr = "Les intervalles où les données pour {} connaissent une forte {} sont: ".format(col, TREND_FR[order])
    else:
        kw_en = "The intervals where the data have a sharp {} are: ".format(TREND_EN[order])
        kw_fr = "Les intervalles où les données connaissent une forte {} sont: ".format(TREND_FR[order])
    
    asc_en = "from {} to {}, "
    asc_fr = "de {} à {}, "

    for i, x in enumerate(trend):
        if i != 0 and i == len(trend) - 1:
            kw_en += 'and '
            kw_fr += 'et '
        kw_en += asc_en.format(x['names'][0], x['names'][1])
        kw_fr += asc_fr.format(x['names'][0], x['names'][1])
    
    kw_en = kw_en[:-2] + '.'
    kw_fr = kw_fr[:-2] + '.'

    return {'en': kw_en, 'fr': kw_fr}