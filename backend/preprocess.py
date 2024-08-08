import csv
import re
import numpy as np
import pandas as pd
from io import StringIO

import config


def text2data(text: str, horizontal_header: bool):
    data = text.strip()

    # raise exception if there is no number in the data
    if bool(re.search(r'\d', data)) == False:
        raise Exception(config.EXCEPTION_INVALID_RAW_DATA)

    header = 'infer' if horizontal_header else None

    # self.preferred = [',', '\t', ';', ' ', ':']
    # change the order of the heuristic as French use commas in numbers
    sniffer = csv.Sniffer()
    sniffer.preferred = ['\t', ',', ';', ' ', ':']

    dialect = sniffer.sniff(data.splitlines()[0])
    df = pd.read_csv(StringIO(data), sep=dialect.delimiter, header=header).dropna(how='all')
    
    if type(df.index) != pd.RangeIndex:
        raise Exception(config.EXCEPTION_INVALID_INDEX_IN_RAW_DATA)

    return df

    
def preprocess_df(chart, df):
    match chart['type']:
        case 'd3-bars':
            if chart['metadata']['data']['transpose']:
                df = transpose(df, chart['metadata']['data']['horizontal-header'])
            
            COLUMNS = df.columns.astype(str).tolist()

            if len(COLUMNS) != 2:
                raise Exception(config.EXCEPTION_UNSUPPORTED_NUMBER_OF_COLUMNS)
            
            df = restore_changes(df, chart['metadata']['data']['changes'], chart['metadata']['data']['transpose'])
            df = format_df(df)   
            validate_df(df)

            if chart['metadata']['visualize']['sort-bars']:
                df = df.sort_values(by=[df.columns[1]], ascending=False, ignore_index=True)
            if chart['metadata']['visualize']['reverse-order']:
                df = df[::-1].reset_index(drop=True)

            return df, COLUMNS
        
        case 'd3-bars-split':
            if chart['metadata']['data']['transpose']:
                df = transpose(df, chart['metadata']['data']['horizontal-header'])
            
            COLUMNS = df.columns.astype(str).tolist()

            df = restore_changes(df, chart['metadata']['data']['changes'], chart['metadata']['data']['transpose'])
            df = format_df(df)
            validate_df(df)
            
            if chart['metadata']['visualize']['sort-bars']:
                if chart['metadata']['visualize']['sort-by'] not in COLUMNS:
                    raise Exception(config.EXCEPTION_UNSUPPORTED_SORT_BY)
                idx = COLUMNS.index(chart['metadata']['visualize']['sort-by'])
                df.index.name = ''
                df = df.sort_values(by=[df.columns[idx], df.index.name], ascending=[False, True], ignore_index=True)
            
            if chart['metadata']['visualize']['reverse-order']:
                df = df [::-1].reset_index(drop=True)

            return df, COLUMNS

        case 'd3-bars-stacked':
            if chart['metadata']['data']['transpose']:
                df = transpose(df, chart['metadata']['data']['horizontal-header'])
            
            COLUMNS = df.columns.astype(str).tolist()
            
            df = restore_changes(df, chart['metadata']['data']['changes'], chart['metadata']['data']['transpose'])
            df = format_df(df)
            validate_df(df)

            if (df.iloc[:,1:].values < 0).any():
                raise Exception(config.EXCEPTION_UNSUPPORTED_STACKED_CHART)
            
            if chart['metadata']['visualize']['sort-bars']:
                if chart['metadata']['visualize']['sort-by'] not in COLUMNS:
                    raise Exception(config.EXCEPTION_UNSUPPORTED_SORT_BY)
                idx = COLUMNS.index(chart['metadata']['visualize']['sort-by'])
                df.index.name = ''
                df = df.sort_values(by=[df.columns[idx], df.index.name], ascending=[False, True], ignore_index=True)
            
            if chart['metadata']['visualize']['reverse-order']:
                df = df [::-1].reset_index(drop=True)
            
            return df, COLUMNS
        
        case 'd3-bars-grouped':
            if chart['metadata']['data']['transpose']:
                df = transpose(df, chart['metadata']['data']['horizontal-header'])
            
            COLUMNS = df.columns.astype(str).tolist()
            
            df = restore_changes(df, chart['metadata']['data']['changes'], chart['metadata']['data']['transpose'])
            df = format_df(df)
            validate_df(df)

            if chart['metadata']['visualize']['sort-bars']:
                if chart['metadata']['visualize']['sort-by'] not in COLUMNS:
                    raise Exception(config.EXCEPTION_UNSUPPORTED_SORT_BY)
                idx = COLUMNS.index(chart['metadata']['visualize']['sort-by'])
                df.index.name = ''
                df = df.sort_values(by=[df.columns[idx], df.index.name], ascending=[False, True], ignore_index=True)
            
            if chart['metadata']['visualize']['reverse-order']:
                df = df [::-1].reset_index(drop=True)
            
            return df, COLUMNS
        
        case 'column-chart':
            if chart['metadata']['data']['transpose']:
                df = transpose(df, chart['metadata']['data']['horizontal-header'])
            
            COLUMNS = df.columns.astype(str).tolist()

            if len(COLUMNS) != 2:
                raise Exception(config.EXCEPTION_UNSUPPORTED_NUMBER_OF_COLUMNS)
            
            df = restore_changes(df, chart['metadata']['data']['changes'], chart['metadata']['data']['transpose'])
            df = format_df(df)
            validate_df(df)

            if chart['metadata']['visualize']['sort-values']:
                df = df.sort_values(by=[df.columns[1]], ascending=False, ignore_index=True)
            if chart['metadata']['visualize']['reverse-order']:
                df = df[::-1].reset_index(drop=True)

            return df, COLUMNS
        
        case 'grouped-column-chart':
            TRANSPOSE = not chart['metadata']['data']['transpose']
            if TRANSPOSE:
                df = transpose(df, chart['metadata']['data']['horizontal-header'])
            
            COLUMNS = df.columns.astype(str).tolist()

            df = restore_changes(df, chart['metadata']['data']['changes'], TRANSPOSE)
            df = format_df(df)
            validate_df(df)

            if chart['metadata']['visualize']['sort-values']:
                if chart['metadata']['visualize']['sort-by'] not in COLUMNS:
                    raise Exception(config.EXCEPTION_UNSUPPORTED_SORT_BY)
                idx = COLUMNS.index(chart['metadata']['visualize']['sort-by'])
                df.index.name = ''
                df = df.sort_values(by=[df.columns[idx], df.index.name], ascending=[True, True], ignore_index=True)

            if chart['metadata']['visualize']['reverse-order']: 
                df = df[::-1].reset_index(drop=True)

            return df, COLUMNS
        
        case 'stacked-column-chart':
            TRANSPOSE = not chart['metadata']['data']['transpose']
            if TRANSPOSE:
                df = transpose(df, chart['metadata']['data']['horizontal-header'])
            
            COLUMNS = df.columns.astype(str).tolist()

            df = restore_changes(df, chart['metadata']['data']['changes'], TRANSPOSE)
            df = format_df(df)
            validate_df(df)

            if (df.iloc[:,1:].values < 0).any():
                raise Exception(config.EXCEPTION_UNSUPPORTED_STACKED_CHART)
            
            if chart['metadata']['visualize']['sort-values']:
                if chart['metadata']['visualize']['sort-by'] not in COLUMNS:
                    raise Exception(config.EXCEPTION_UNSUPPORTED_SORT_BY)
                idx = COLUMNS.index(chart['metadata']['visualize']['sort-by'])
                df.index.name = ''
                df = df.sort_values(by=[df.columns[idx], df.index.name], ascending=[True, True], ignore_index=True)

            if chart['metadata']['visualize']['reverse-order']: 
                df = df[::-1].reset_index(drop=True)

            return df, COLUMNS
        
        case 'd3-area':
            if chart['metadata']['data']['transpose']:
                df = transpose(df, chart['metadata']['data']['horizontal-header'])
            
            COLUMNS = df.columns.astype(str).tolist()
            
            df = restore_changes(df, chart['metadata']['data']['changes'], chart['metadata']['data']['transpose'])
            df = format_df(df)
            validate_df(df)

            if (df.iloc[:,1:].values < 0).any():
                raise Exception(config.EXCEPTION_UNSUPPORTED_STACKED_CHART)

            return df, COLUMNS

        case 'd3-lines':
            if chart['metadata']['data']['transpose']:
                df = transpose(df, chart['metadata']['data']['horizontal-header'])

            COLUMNS = df.columns.astype(str).tolist()

            df = restore_changes(df, chart['metadata']['data']['changes'], chart['metadata']['data']['transpose'])
            df = format_df(df)
            validate_df(df)

            return df, COLUMNS

        case 'd3-pies':
            if chart['metadata']['data']['transpose']:
                df = transpose(df, chart['metadata']['data']['horizontal-header'])
            
            COLUMNS = df.columns.astype(str).tolist()

            if len(COLUMNS) != 2:
                raise Exception(config.EXCEPTION_UNSUPPORTED_NUMBER_OF_COLUMNS)
            
            df = restore_changes(df, chart['metadata']['data']['changes'], chart['metadata']['data']['transpose'])
            df = format_df(df)
            validate_df(df)

            # sort based on chart configuration
            if chart['metadata']['visualize']['slice_order'] == 'ascending':
                df = df.sort_values(by=df.columns[1], ignore_index=True)
            elif chart['metadata']['visualize']['slice_order'] == 'descending':
                df = df.sort_values(by=df.columns[1], ascending=False, ignore_index=True)
            
            return df, COLUMNS
        
        case _:
            raise Exception(config.EXCEPTION_UNSUPPORTED_CHART_TYPE)
        

def transpose(df, horizontal_header: bool):
    if horizontal_header:
        df = df.T.reset_index()
        df.rename(columns=df.iloc[0], inplace=True)
        df.drop([0], inplace=True)
        df.reset_index(drop=True, inplace=True)
    else:
        df = df.T
    return df


def restore_changes(df, changes: list, transpose: bool):
    clean_html_tag = lambda x: re.sub(re.compile('<.*?>'), '', x)
    
    for change in changes:
        row, col = change['row'], change['column']
        
        if transpose:
            row, col = col, row
        
        if row == 0:
            # change in header
            if df.columns[col] == change['value']:
                continue
            df.rename(columns={df.columns[col]: clean_html_tag(change['value'])}, inplace=True)
        else:
            if df.iloc[row-1, col] == change['value']:
                continue
            if df.iloc[row-1, col] != change['previous']:
                raise Exception(config.EXCEPTION_CHANGES_CANNOT_BE_RESTORED)
            df.iloc[row-1, col] = change['value']
    
    return df


def format_df(df):
    remove_whitespace = lambda x: re.sub(r'\s', '', str(x))

    is_fr_number = lambda x: bool(re.match(r'^-?\d+(,\d+)?%?\$?$', x))
    is_en_number = lambda x: bool(re.match(r'^-?\d+(\.\d+)?%?\$?$', x))
    is_en_number_with_comma = lambda x: bool(re.match(r'^-?\d{1,3}(?:,\d{3})*(\.\d+)?%?\$?$', x))

    # remove whitespace, %, and $
    format_fr_number = lambda x: float(re.sub(r'[\s%$]', '', str(x)).replace(',', '.'))
    format_en_number = lambda x: float(re.sub(r'[\s%$]', '', str(x)))
    format_en_number_with_comma = lambda x: float(re.sub(r'[\s%$,]', '', str(x)))

    for col in df.columns:
        if pd.api.types.is_string_dtype(df[col]):
            # column type is string
            if df[col].apply(remove_whitespace).apply(is_fr_number).all():
                df[col] = df[col].apply(format_fr_number)
            elif df[col].apply(remove_whitespace).apply(is_en_number).all():
                df[col] = df[col].apply(format_en_number)
            elif df[col].apply(remove_whitespace).apply(is_en_number_with_comma).all():
                df[col] = df[col].apply(format_en_number_with_comma)
    return df


def validate_df(df):
    if df.iloc[:,1:].isnull().values.any():
        raise Exception(config.EXCEPTION_NULL_VALUES)
    if not np.issubdtype(df.iloc[:,1:].to_numpy().dtype, np.number):
        raise Exception(config.EXCEPTION_NON_NUMERIC_VALUES)