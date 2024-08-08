import json
import numpy as np
import re
from bs4 import BeautifulSoup
from scipy.spatial import distance
from skimage import color
import config

class ColorName:
    def __init__(self):
        with open('./assets/colorName.json') as f:
            COLOR_NAME = json.load(f)
        self.COLOR_NODES = np.array(COLOR_NAME['cielab'])
        self.CSS3_NAMES = COLOR_NAME['name']

    def __closest_node_index(self, node, l=1, a=1, b=1):
        weights = np.array([l, a, b])
        if node.ndim != 2:
            node = node.reshape((1,-1))
        closest_index = distance.cdist(node, self.COLOR_NODES, lambda u, v: np.sqrt((((u-v)*weights)**2).sum())).argmin()
        return closest_index

    # node: [r,g,b] or (r,g,b)
    def nearest_neighbor_search(self, node):
        if isinstance(node, str):
            # rgb(r,g,b)
            node = list(map(int, re.findall(r'\d+', node)))
        node_lab = color.rgb2lab(np.array(node)/255)
        closest_index = self.__closest_node_index(node_lab)
        return self.CSS3_NAMES[closest_index]
    

def get_svg_color(svg, chart, df, columns) -> list[str]:
    if not svg: raise Exception(config.EXCEPTION_SVG)
    is_rgb = lambda color_str: bool(re.compile(r'rgb\(\d+\s?,\d+\s?,\d+\s?\)').match(color_str))
    
    soup = BeautifulSoup(svg, 'lxml')
    match chart['type']:
        case 'd3-bars':
            color = [rect.get('fill') for rect in soup.find(id='chart-svg').findAll('rect') if is_rgb(rect.get('fill'))]
            if len(color) != len(df):
                raise Exception(config.EXCEPTION_COLOR)
            return color
        
        case 'd3-bars-split':
            color = [rect.get('fill') for rect in soup.find(id='chart-svg').findAll('rect') if is_rgb(rect.get('fill'))]
            n = len(df) * len(columns[1:])
            if chart['metadata']['visualize']['show-color-key']:
                if len(color) != n + len(columns[1:]):
                    raise Exception(config.EXCEPTION_COLOR)
            else:
                if len(color) != n:
                    raise Exception(config.EXCEPTION_COLOR)
            return color[:n]
        
        case 'd3-bars-stacked' | 'd3-bars-grouped':
            color = [rect.get('fill') for rect in soup.find(id='chart-svg').findAll('rect') if is_rgb(rect.get('fill'))]
            if len(color) < len(columns[1:]):
                raise Exception(config.EXCEPTION_COLOR)
            return color[:len(columns[1:])]
        
        case 'column-chart':
            color = [rect.get('fill') for rect in soup.find(id='columns-svg').findAll('rect')]
            if len(color) != len(df):
                raise Exception(config.EXCEPTION_COLOR)
            return color
        
        case 'grouped-column-chart' | 'stacked-column-chart':
            color = [rect.get('fill') for rect in soup.find(id='columns-svg').findAll('rect')]
            if len(color) < len(columns[1:]):
                raise Exception(config.EXCEPTION_COLOR)
            return color[:len(columns[1:])]

        case 'd3-area':
            color = []
            for path in soup.find(id='svg-main-svg').findAll('path'):
                rgb = re.search(r'fill:(.*?);', path.get('style')).group(1).strip()
                color.append(rgb)
            if len(color) != len(columns[1:]):
                raise Exception(config.EXCEPTION_COLOR)
            return color
        
        case 'd3-lines':
            color_map = {path.get('id'): path.get('stroke') for path in soup.find(id='lines-svg').findAll('path')}
            if len(color_map) == 1 and len(columns[1:]) == 1:
                return list(color_map.values())
            color = [color_map[x.strip()] for x in columns[1:]]
            if len(color) != len(df.columns[1:]):
                raise Exception(config.EXCEPTION_COLOR)
            return color
        
        case 'd3-pies':
            color = []
            for path in soup.find(id='pie-svg').find_all('path'):
                rgb = re.search(r'fill:(.*?);', path.get('style')).group(1).strip()
                color.append(rgb)
            if len(color) != len(df):
                raise Exception(config.EXCEPTION_COLOR)
            return color
        
        case _:
            raise Exception(config.EXCEPTION_UNSUPPORTED_CHART_TYPE)