import numpy as np

def get_outliers(series):
    Q1 = np.quantile(series, 0.25)
    Q3 = np.quantile(series, 0.75)
    IQR = Q3 - Q1
    lower_range = Q1 - 1.5 * IQR
    upper_range = Q3 + 1.5 * IQR
    outliers = []
    for i, x in enumerate(series):
        if x < lower_range or x > upper_range:
            outliers.append((round(x,2), i))
    return outliers
