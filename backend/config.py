import numpy as np

# exception
EXCEPTION_INVALID_RAW_DATA = 'Invalid raw data'
EXCEPTION_INVALID_INDEX_IN_RAW_DATA = 'Invalid index in raw data'

EXCEPTION_UNSUPPORTED_CHART_TYPE = 'Unsupported chart type'
EXCEPTION_CHANGES_CANNOT_BE_RESTORED = 'Changes cannot be restored'

EXCEPTION_NULL_VALUES = 'Presence of null values'
EXCEPTION_NON_NUMERIC_VALUES = 'Presence of non-numeric values'

EXCEPTION_UNSUPPORTED_NUMBER_OF_COLUMNS = 'Unsupported number of columns'               # d3-bars, column-chart, d3-pies
EXCEPTION_UNSUPPORTED_STACKED_CHART = 'Presence of negative numbers in stacked chart'   # d3-bars-stacked, stacked-column-chart, d3-area
EXCEPTION_UNSUPPORTED_SORT_BY = 'The value for sort-by is not in dataframe columns'

EXCEPTION_SVG = 'Failed to retrieve svg'
EXCEPTION_COLOR = 'Failed to retrieve color from svg'

# threshold
THRESHOLD_DATA_POINTS = 5
THRESHOLD_OUTLIERS = 5
THRESHOLD_TOTAL_INTERVALS = 5
THRESHOLD_SPECIFIC_INTERVALS = 3


DECAL = {
    'symbol': 'rect',
    'dashArrayX': [1, 0],
    'dashArrayY': [4, 3],
    'rotation': -np.pi / 4
}

TAG_ASC = {'en': 'sharp increase', 'fr': 'forte augmentation'}
TAG_DESC = {'en': 'sharp decrease', 'fr': 'forte diminution'}