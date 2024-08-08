import numpy as np
from scipy.stats import pearsonr

CORRELATION_TEMPLATE = {
    "univariate": {
        "correlated": {
            "en": "The data show a {} correlation.",
            "fr": "Les données montrent une {} corrélation {}."
        },
        "non-correlated": {
            "en": "There is no correlation observed in the data.",
            "fr": "Aucune corrélation n'est observée dans les données."
        }
    },
    "multivariate": {
        "correlated": {
            "en": "There is a {} correlation between the feature {} and the {}.",
            "fr": "Il exist une {} corrélation {} entre la variable {} et {}."
        },
        "non-correlated": {
            "en": "",
            "fr": ""
        }
    }
}

def add_correlation(response: dict, key: str, tag: dict, template, x: np.ndarray, y: np.ndarray) -> None:
    coefficient = pearsonr(x, y)
    if coefficient[1] >= 0.05:
        # correlation coefficient is not statistically significant
        # remove correlation
        response['schema']['L2'][4]['show'] = False
    else:
        if coefficient[0] > 0.6:
            response['visDescription'][key] = {
                'id': key,
                'tag': template[key]['tag'],
                'text': {k: v for k,v in template[key]['description']['strong-positive']['template'].items()}
            }
        elif coefficient[0] > 0.2:
            response['visDescription'][key] = {
                'id': key,
                'tag': template[key]['tag'],
                'text': {k: v for k,v in template[key]['description']['weak-positive']['template'].items()}
            }
        elif coefficient[0] > -0.2:
            response['visDescription'][key] = {
                'id': key,
                'tag': template[key]['tag'],
                'text': {k: v for k,v in template[key]['description']['no-correlation']['template'].items()}
            }
        elif coefficient[0] > -0.6:
            response['visDescription'][key] = {
                'id': key,
                'tag': template[key]['tag'],
                'text': {k: v for k,v in template[key]['description']['weak-negative']['template'].items()}
            }
        else:
            response['visDescription'][key] = {
                'id': key,
                'tag': template[key]['tag'],
                'text': {k: v for k,v in template[key]['description']['strong-negative']['template'].items()}
            }
pass