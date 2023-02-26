# -*- coding: utf-8 -*-
from collections import OrderedDict
import os
import datetime
import math
import numpy as np
import pandas as pd
import re
import sys
import json
import itertools
from typing import List
from os.path import dirname, abspath, join, relpath
import copy
import io
from PIL import Image
from base64 import encodebytes
from glob import glob
from flask import jsonify
import zipfile
import json
import time
from github import Github
from decouple import config
import requests
from requests.sessions import Session
import boto3
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Thread, local


# get the /TableCharts
# Alter: abspath('') is called from back/run.py
# read data from github
# github = Github(config("API_TOKEN"))
github = Github("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")
rootDir = github.get_user().get_repo("attn-viz-data")
print(rootDir)

# s3 = boto3.resource('s3')

thread_local = local()


def get_session():
    if not hasattr(thread_local, 'session'):
        thread_local.session = requests.Session()
    return thread_local.session


def download_link(url):
    session = get_session()
    with session.get(url) as response:
        return response.text


def download_all(url_list):
    data = []
    with ThreadPoolExecutor(max_workers=None) as executor:
        processes = {executor.submit(download_link, url) for url in url_list}

        for res in as_completed(processes):
            data.append(json.loads(res.result()))

    return data


def read_matrix_data(model):
    # matrix_data = []
    time_start = time.time()

    # for layer in range(12):
    #     for head in range(12):
    #         # print("layer {} head {}".format(layer, head))
    #         object = s3.Object(
    #             'attn-data', '{}/byLayerHead/layer{}_head{}.json'.format(model, layer, head))
    #         data = object.get()['Body'].read().decode('utf-8')
    #         d = json.loads(data)
    #         matrix_data.append(d)

    all_urls = []
    for f in rootDir.get_contents(join(model, 'byLayerHead')):
        # print(f)
        url = join("https://raw.githubusercontent.com/",
                   rootDir.full_name, "main", f.path)
        all_urls.append(url)
        # resp = requests.get(url)
        # d = json.loads(resp.text)
        # matrix_data.append(d)

    matrix_data = download_all(all_urls)

    print('{} MatrixData Done! Time elapsed: {} seconds'.format(
        model, time.time()-time_start))
    return matrix_data


def read_attention_data(model):
    time_start = time.time()
    # attention_data = []

    # for f in rootDir.get_contents(join(model, 'attention')):
    #     url = 'https://raw.githubusercontent.com/' + \
    #         join(rootDir.full_name, 'main', f.path)
    #     resp = requests.get(url)
    #     d = json.loads(resp.text)
    #     attention_data.append(d)

    all_urls = []
    for f in rootDir.get_contents(join(model, 'attention')):
        # print(f)
        url = join("https://raw.githubusercontent.com/",
                   rootDir.full_name, "main", f.path)
        all_urls.append(url)

    attention_data = download_all(all_urls)

    print('{} AttentionData Done! Time elapsed: {} seconds'.format(model,
                                                                   time.time()-time_start))
    return attention_data


def read_token_data(model):
    time_start = time.time()
    url = 'https://raw.githubusercontent.com/' + \
        join(rootDir.full_name, 'main', model, 'tokens.json')
    resp = requests.get(url)
    d = json.loads(resp.text)
    # d = rootDir.get_contents(join(model, 'tokens.json')
    #  ).decoded_content.decode()
    print('{} TokenData Done! Time elapsed: {} seconds'.format(
        model, time.time()-time_start))
    return d


class DataService(object):
    def __init__(self):
        print('------inited------')
        # self.df = pd.read_csv(join(rootDir, 'prodata', 'pro_data_results.csv')) .h5 .npy
        # read data here

        # bert
        self.matrix_data_bert = read_matrix_data("bert")
        self.attention_data_bert = read_attention_data("bert")
        self.token_data_bert = read_token_data("bert")

        # gpt
        self.matrix_data_gpt = read_matrix_data("gpt")
        self.attention_data_gpt = read_attention_data("gpt")
        self.token_data_gpt = read_token_data("gpt")

        return None

    # def get_raw_data(self):
    #     # return data to the front end
    #     return self.data

    def get_matrix_data(self, model):
        if model == "bert":
            return self.matrix_data_bert
        return self.matrix_data_gpt

    # def get_attention_data(self, model):
    #     if model == "bert":
    #         return self.attention_data_bert
    #     return self.attention_data_gpt

    def get_token_data(self, model):
        if model == "bert":
            return self.token_data_bert
        return self.token_data_gpt

    def get_attention_by_token(self, token, model):
        layer = token['layer']
        head = token['head']
        index = token['index']

        if model == "bert":
            all_token_info = self.token_data_bert['tokens'][index]
        else:
            all_token_info = self.token_data_gpt['tokens'][index]
        start = index - all_token_info['pos_int']
        end = start + all_token_info['length']

        if model == "bert":
            attn_data = self.attention_data_bert
        else:
            attn_data = self.attention_data_gpt

        for plot in attn_data:
            if plot['layer'] == layer and plot['head'] == head:
                attns = plot['tokens'][start:end]
                break

        return {
            'layer': layer,
            'head': head,
            'attns': [t['attention'] for t in attns],
            'token': all_token_info
        }


if __name__ == '__main__':
    print('start dataservice')
    dataService = DataService()
