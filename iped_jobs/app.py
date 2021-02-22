#!/usr/bin/env python3

import os
import http
import logging
from flask import Flask, make_response, request
from flask_restplus import Resource, Api, fields
from werkzeug.exceptions import BadRequest

from .k8s import K8s

DEBUG = ('DEBUG' in os.environ)


def env2dict(env: str):
    result = {}
    for line in env.split('\n'):
        line = line.strip()
        if not line:
            continue
        parts = line.split('=', 1)
        if len(parts) == 2:
            result[parts[0].strip()] = parts[1].strip()
    return result


def create_app():
    app = Flask(__name__)  # Create a Flask WSGI appliction
    api = Api(app)  # Create a Flask-RESTPlus API
    log = logging.getLogger(__name__)

    @api.route('/iped/')
    class Iped(Resource):
        @api.representation('text/plain')
        @api.expect(api.model('ipedParameters', {
            "image": fields.String(required=True, description='docker image'),
            "IPEDJAR": fields.String(required=True, description='path to the IPED.jar file'),
            "EVIDENCE_PATH": fields.String(required=True, description='path to a datasource, to create a single job'),
            "OUTPUT_PATH": fields.String(required=True, description='IPED output folder'),
            "IPED_PROFILE": fields.String(required=True, description='IPED profile'),
            "ADD_ARGS": fields.String(required=True, description='extra arguments to IPED'),
            "ADD_PATHS": fields.String(required=True, description='extra source paths to IPED'),
            "env": fields.String(required=True, description='extra envirnoment variables, one by line'),
        }))
        def post(self):
            """Create a new kubernetes job to run IPED"""
            try:
                image = api.payload['image']
                IPEDJAR = api.payload['IPEDJAR']
                EVIDENCE_PATH = api.payload['EVIDENCE_PATH']
                OUTPUT_PATH = api.payload['OUTPUT_PATH']
                IPED_PROFILE = api.payload['IPED_PROFILE']
                ADD_ARGS = api.payload['ADD_ARGS']
                ADD_PATHS = api.payload['ADD_PATHS']
                env = api.payload['env']
            except:
                raise BadRequest('missing parameters')
            try:
                env = env2dict(env)
                return K8s().addJob(image, IPEDJAR, EVIDENCE_PATH, OUTPUT_PATH, IPED_PROFILE, ADD_ARGS, ADD_PATHS, **env)
            except Exception as e:
                if DEBUG:
                    log.exception(e)
                raise BadRequest(dict(error=str(e)))
    return app
