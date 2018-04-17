import tensorflow as tf
import logging
import os
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

tf.logging.set_verbosity(tf.logging.ERROR)

SAVED_MODEL_DIR = 'model'

PROJECT = 'ksalama-gcp-playground'
CMLE_MODEL_NAME = 'babyweight_estimator'
CMLE_MODEL_VERSION = 'v3'


predictor_fn = None


def init_predictor():

    global predictor_fn

    if predictor_fn is None:

        print("Initialising predictor...")
        dir_path = os.path.dirname(os.path.realpath(__file__))
        export_dir = os.path.join(dir_path, SAVED_MODEL_DIR)

        if os.path.exists(export_dir):
            predictor_fn = tf.contrib.predictor.from_saved_model(
                export_dir=export_dir,
                signature_def_key="predict"
            )
        else:
            logging.ERROR("Model not found! - Invalid model path: {}".format(export_dir))

    return predictor_fn


def estimate_local(instance):

    predictor_fn = init_predictor()
    instance = dict((k, [v]) for k, v in instance.items())
    value = predictor_fn(instance)['predictions'][0][0]
    return value


def estimate_cmle(instance):

    credentials = GoogleCredentials.get_application_default()
    api = discovery.build('ml', 'v1', credentials=credentials,
                          discoveryServiceUrl='https://storage.googleapis.com/cloud-ml/discovery/ml_v1_discovery.json')

    request_data = {'instances': [instance]}

    model_url = 'projects/{}/models/{}/versions/{}'.format(PROJECT, CMLE_MODEL_NAME, CMLE_MODEL_VERSION)
    response = api.projects().predict(body=request_data, name=model_url).execute()
    value = response['predictions'][0]['predictions'][0]
    return value
