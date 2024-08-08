from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import requests
from datawrapper_api import *
from vis_helper import *
from preprocess import text2data, preprocess_df
from charts.bars.d3_bars import *
from charts.bars.d3_bars_split import *
from charts.bars.d3_bars_stacked import *
from charts.bars.d3_bars_grouped import *
from charts.column.column_chart import *
from charts.column.grouped_column_chart import *
from charts.column.stacked_column_chart import *
from charts.area.d3_area import *
from charts.lines.d3_lines import *
from charts.pies.d3_pies import *

from algorithm.color import *
from os import environ
from datetime import timedelta
from auth import auth_blueprint


app = Flask(__name__)
CORS(app, supports_credentials=True)

load_dotenv()

app.config["JWT_COOKIE_SECURE"] = False
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_SECRET_KEY"] = environ.get("JWT_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=30)

TOKEN_LE_DEVOIR = environ.get("TOKEN_LE_DEVOIR")
TOKEN_RADIO_CANADA = environ.get("TOKEN_RADIO_CANADA")

app.register_blueprint(auth_blueprint)


@app.route('/')
def hello():
    return 'Hello, World!'


@app.route('/chart', methods=['POST'])
def get_chart():
    chart_id = request.json['chartId']
    token = request.json['token']
    try:
        chart = fetch_chart(chart_id, token)
    except Exception as e:
        (error_args,) = e.args
        error = json.loads(error_args)
        return jsonify({'message': error['message']}), error['statusCode']

    return jsonify({
        'publicId': chart['publicId'],
        'type': chart['type'],
        'thumbnail': chart['thumbnails']['full']
    })



@app.route('/chart/v2', methods=['POST'])
def get_chart2():
    match request.json['datasetKey']:
        case 'le-devoir':
            token = TOKEN_LE_DEVOIR
        case 'radio-canada':
            token = TOKEN_RADIO_CANADA
    try:
        chart = fetch_chart(request.json['chartId'], token)
    except Exception as e:
        (error_args,) = e.args
        error = json.loads(error_args)
        print(error_args)
        return jsonify({'message': error['message']}), error['statusCode']

    return jsonify({
        'publicId': chart['publicId'],
        'type': chart['type'],
        'title': chart['title'],
        'thumbnail': chart['thumbnails']['full']
    })



@app.route('/visualization/v2', methods=['POST'])
def get_visualization():
    chart_id = request.json['chartId']
    dataset_key = request.json['datasetKey']
    
    match dataset_key:
        case 'le-devoir':
            with open('./assets/LeDevoirChart.json') as f:
                chart = json.load(f)[chart_id]
            with open('./assets/LeDevoirData.json') as f:
                text = json.load(f)[chart_id]
            with open('./assets/LeDevoirSVG.json') as f:
                svg = json.load(f)[chart_id]
        case 'radio-canada':
            with open('./assets/RadioCanadaChart.json') as f:
                chart = json.load(f)[chart_id]
            with open('./assets/RadioCanadaData.json') as f:
                text = json.load(f)[chart_id]
            with open('./assets/RadioCanadaSVG.json') as f:
                svg = json.load(f)[chart_id]
        case _:
            return jsonify({'message': 'Error in dataset key'}), 400

    try:
        df = text2data(text, chart['metadata']['data']['horizontal-header'])
        df, COLUMNS = preprocess_df(chart, df)
    except Exception as e:
        print('Exception',e.args[0])
        return jsonify({'message': e.args[0]}), 503
    
    #svg = export_chart(chart_id, token)
    color = get_svg_color(svg, chart, df, COLUMNS)
    
    schema = json.load(open('./assets/schema.json'))[chart['type']]
    template = json.load(open('./assets/template.json'))

    response = {
        'visualize': {
            'id': chart_id,
            'type': chart['type'],
            'title': chart['title'],
            'intro': chart['metadata']['describe']['intro'],
            'annotation': chart['metadata']['annotate']['notes']
        },
        'schema': schema,
        'visDescription': {},
        'visualCue': {}
    }

    #add_L1_description(response, chart, template['L1-info'])
    add_L3_description(response)

    match chart['type']:
        case 'd3-bars':
            add_d3_bars_option(response, chart, df, color)
            add_d3_bars_description(response, chart, df, color, template)
        case 'd3-bars-split':
            add_d3_bars_split_option(response, chart, df, color)
            add_d3_bars_split_description(response, chart, df, color, template)
        case 'd3-bars-stacked':
            add_d3_bars_stacked_option(response, chart, df, color)
            add_d3_bars_stacked_description(response, chart, df, color, template)
        case 'd3-bars-grouped':
            add_d3_bars_grouped_option(response, chart, df, color)
            add_d3_bars_grouped_description(response, chart, df, color, template)
        case 'column-chart':
            add_column_chart_option(response, chart, df, color)
            add_column_chart_description(response, chart, df, color, template)
        case 'grouped-column-chart':
            add_grouped_column_chart_option(response, chart, df, color)
            add_grouped_column_chart_description(response, chart, df, color, template)
        case 'stacked-column-chart':
            add_stacked_column_chart_option(response, chart, df, color)
            add_stacked_column_chart_description(response, chart, df, color, template)
        case 'd3-area':
            add_d3_area_option(response, chart, df, color)
            add_d3_area_description(response, chart, df, color, template)
        case 'd3-lines':
            add_d3_lines_option(response, chart, df, color)
            add_d3_lines_description(response, chart, df, color, template)
        case 'd3-pies':
            add_d3_pies_option(response, chart, df, color)
            add_d3_pies_description(response, chart, df, color, template)
        case _:
            pass
    return json.dumps(response, default=str)
    #return simplejson.dumps(response, ignore_nan=True)



@app.route('/visualization/v3', methods=['POST'])
def get_visualization3():
    chart_id = request.json['chartId']
    token = request.json['token']

    try:
        chart = fetch_chart(chart_id, token)
        text = fetch_chart_data(chart_id, token)
    except:
        return jsonify({'message': 'Error in Datawrapper API request'})

    try:
        df = text2data(text, chart['metadata']['data']['horizontal-header'])
        df, COLUMNS = preprocess_df(chart, df)
    except Exception as e:
        print('Exception',e.args[0])
        return jsonify({'message': e.args[0]}), 501
    
    svg = export_chart(chart_id, token)
    color = get_svg_color(svg, chart, df, COLUMNS)
    
    schema = json.load(open('./assets/schema.json'))[chart['type']]
    template = json.load(open('./assets/template.json'))

    response = {
        'visualize': {
            'id': chart_id,
            'type': chart['type'],
            'title': chart['title'],
            'intro': chart['metadata']['describe']['intro'],
            'annotation': chart['metadata']['annotate']['notes']
        },
        'schema': schema,
        'visDescription': {},
        'visualCue': {}
    }

    #add_L1_description(response, chart, template['L1-info'])
    add_L3_description(response)

    match chart['type']:
        case 'd3-bars':
            add_d3_bars_option(response, chart, df, color)
            add_d3_bars_description(response, chart, df, color, template)
        case 'd3-bars-split':
            add_d3_bars_split_option(response, chart, df, color)
            add_d3_bars_split_description(response, chart, df, color, template)
        case 'd3-bars-stacked':
            add_d3_bars_stacked_option(response, chart, df, color)
            add_d3_bars_stacked_description(response, chart, df, color, template)
        case 'd3-bars-grouped':
            add_d3_bars_grouped_option(response, chart, df, color)
            add_d3_bars_grouped_description(response, chart, df, color, template)
        case 'column-chart':
            add_column_chart_option(response, chart, df, color)
            add_column_chart_description(response, chart, df, color, template)
        case 'grouped-column-chart':
            add_grouped_column_chart_option(response, chart, df, color)
            add_grouped_column_chart_description(response, chart, df, color, template)
        case 'stacked-column-chart':
            add_stacked_column_chart_option(response, chart, df, color)
            add_stacked_column_chart_description(response, chart, df, color, template)
        case 'd3-area':
            add_d3_area_option(response, chart, df, color)
            add_d3_area_description(response, chart, df, color, template)
        case 'd3-lines':
            add_d3_lines_option(response, chart, df, color)
            add_d3_lines_description(response, chart, df, color, template)
        case 'd3-pies':
            add_d3_pies_option(response, chart, df, color)
            add_d3_pies_description(response, chart, df, color, template)
        case _:
            pass
    return json.dumps(response, default=str)
    #return simplejson.dumps(response, ignore_nan=True)



@app.route('/chartlist', methods=['POST'])
def get_charts_from_current_page():
    page = request.json['page']
    token = request.json['token']

    PAGE_SIZE = 9
    page = (page - 1) * PAGE_SIZE
    url = "https://api.datawrapper.de/v3/charts?order=DESC&orderBy=createdAt&limit=9&offset={}&expand=false".format(page)
    headers = {
        "accept": "*/*",
        'Authorization': 'Bearer {}'.format(token)
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return jsonify({'message': 'error in fetching chart list'}), response.status_code
    
    charts = json.loads(response.text)

    data = list(map(lambda x: {'publicId': x['publicId'], 'type': x['type'], 'thumbnail': x['thumbnails']['full']}, charts['list']))
    return jsonify({'chartList': data, 'total': charts['total']})


if __name__ == '__main__':
    app.run(debug=True)