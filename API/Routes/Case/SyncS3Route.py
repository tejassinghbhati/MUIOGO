from flask import Blueprint, jsonify, request
import os
from pathlib import Path
import shutil
from Classes.Base import Config
from Classes.Base.SyncS3 import SyncS3
from Classes.Base.RequestValidator import get_required_fields

syncs3_api = Blueprint('SyncS3Route', __name__)

@syncs3_api.route("/deleteResultsPreSync", methods=['POST'])
def deleteResultsPreSync():
    try:        
        fields, err = get_required_fields(['casename'])
        if err:
            return err
        case = fields['casename']
        
        resPath = Path(Config.DATA_STORAGE, case, 'res')
        dataPath = Path(Config.DATA_STORAGE, case, 'data.txt')
        shutil.rmtree(resPath)
        os.remove(dataPath)

        response = {
            "message": 'Case <b>'+ case + '</b> deleted!',
            "status_code": "success"
        }
        return jsonify(response), 200
    except(IOError):
        return jsonify('No existing cases!'), 404
    except OSError:
        raise OSError

@syncs3_api.route("/uploadSync", methods=['POST'])
def uploadSync():
    try:        
        fields, err = get_required_fields(['casename'])
        if err:
            return err
        case = fields['casename']

        s3 = SyncS3()
        localDir = Path(Config.DATA_STORAGE, case)
        s3.uploadSync(localDir, case, Config.S3_BUCKET, '*')

        response = {
            "message": 'Case <b>'+ case + '</b> syncronized!',
            "status_code": "success"
        }
        return jsonify(response), 200
    except(IOError):
        return jsonify('No existing cases!'), 404
    except OSError:
        raise OSError

@syncs3_api.route("/deleteSync", methods=['POST'])
def deleteSync():
    try:        
        fields, err = get_required_fields(['casename'])
        if err:
            return err
        case = fields['casename']

        s3 = SyncS3()
        s3.deleteSync(case)

        response = {
            "message": 'Case <b>'+ case + '</b> deleted!',
            "status_code": "success"
        }
        return jsonify(response), 200
    except(IOError):
        return jsonify('No existing cases!'), 404
    except OSError:
        raise OSError

@syncs3_api.route("/updateSync", methods=['POST'])
def updateSync():
    try:        
        fields, err = get_required_fields(['casename', 'file'])
        if err:
            return err
        case = fields['casename']
        filename = fields['file']

        s3 = SyncS3()
        localDir = Path(Config.DATA_STORAGE, case, str(filename))
        s3.updateSync(localDir, case, Config.S3_BUCKET)

        response = {
            "message": 'Case <b>'+ case + '</b> deleted!',
            "status_code": "success"
        }
        return jsonify(response), 200
    except(IOError):
        return jsonify('No existing cases!'), 404
    except OSError:
        raise OSError

@syncs3_api.route("/updateSyncParamFile", methods=['GET'])
def updateSyncParamFile():
    try:        

        case = ''
        s3 = SyncS3()
        localDir = Path(Config.DATA_STORAGE, "Parameters.json")

        s3.updateSync(localDir, case, Config.S3_BUCKET)

        response = {
            "message": 'Case <b>'+ case + '</b> deleted!',
            "status_code": "success"
        }
        return jsonify(response), 200
    except(IOError):
        return jsonify('No existing cases!'), 404
    except OSError:
        raise OSError
