import flask,json
from flask_cors import CORS
from gevent import pywsgi
import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import norm
from scipy.cluster.vq import kmeans,whiten
from sklearn.cluster import DBSCAN
from scipy.stats import pearsonr,ttest_rel,linregress
from typing import List, Tuple, Dict
import time
from insight_update import *

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, pd.RangeIndex):
            return obj.tolist()
        elif isinstance(obj, pd.Index):
            return obj.tolist()
        elif isinstance(obj, pd.Series):
            return obj.tolist()
        else:
            print(obj)
            return super(NpEncoder, self).default(obj)

app=flask.Flask(__name__)
CORS(app, supports_credentials=True)

@app.route('/insight',methods=['get','post'])
def insight():
    
    result = {'success':True,'data':{}}
    tic = time.time()

    try:
        input_data =  json.loads(flask.request.data)
        dataSource = pd.DataFrame(input_data['dataSource'])
        fields = pd.DataFrame(input_data['fields'])
        # with open('input_data.json','w') as f:
        #     json.dump(input_data,f)
        dataSource = dataSource.dropna()
        check_list = input_data['check_list'] if 'check_list' in input_data else None
        breakdown = input_data['breakdown'] if 'breakdown' in input_data else None
        aggrType = input_data['aggrType'] if 'aggrType' in input_data else 'mean'
        subspaces = input_data['subspaces'] if 'subspaces' in input_data else None
        rangeN = input_data['rangeN'] if 'rangeN' in input_data else 5
        if 'langType' in input_data and input_data['langType'] == 'en-US':
            langType = 'en'
        elif (
            'langType' in input_data
            and input_data['langType'] == 'zh-CN'
            or 'langType' not in input_data
        ):
            langType = 'cn'
    except:
        if result['success']==True:
            result['success']=False
            result['message']='error in read inputdata'
    # try:
    if 1>0:
        insight_dict,insight_input = insight_check(fields,dataSource,check_list,breakdown,aggrType,subspaces,rangeN,langType)
        result['data'] = (insight_dict,insight_input)
        print(insight_input)
        for d in insight_dict:
            if insight_dict[d]['score']>0:
                print(d,':',insight_dict[d]['score'])
    # except:
    #     if result['success']==True:
    #         result['success']=False
    #         result['message']='error in write result'
    #     else:
    #         pass

    print(result['success'])
    print('time:',time.time()-tic)
    return flask.Response(json.dumps(result, ensure_ascii=False, cls=NpEncoder), mimetype="application/json")

if __name__ == '__main__':
    # server = pywsgi.WSGIServer(('0.0.0.0', 8000), app, keyfile='./viexpl.key', certfile='./viexpl.pem')
    server = pywsgi.WSGIServer(('0.0.0.0', 8000), app)
    server.serve_forever()