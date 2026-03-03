from flask import Blueprint, jsonify, request, send_file, session
from pathlib import Path
import shutil, datetime, time, os
from Classes.Case.DataFileClass import DataFile
from Classes.Base import Config
from Classes.Base.RequestValidator import get_required_fields

datafile_api = Blueprint('DataFileRoute', __name__)

@datafile_api.route("/generateDataFile", methods=['POST'])
def generateDataFile():
    try:
        fields, err = get_required_fields(['casename', 'caserunname'])
        if err:
            return err
        casename = fields['casename']
        caserunname = fields['caserunname']

        if casename != None:
            txtFile = DataFile(casename)
            txtFile.generateDatafile(caserunname)
            response = {
                "message": "You have created data file!",
                "status_code": "success"
            }      
        return jsonify(response), 200
    except(IOError):
        return jsonify('No existing cases!'), 404

@datafile_api.route("/createCaseRun", methods=['POST'])
def createCaseRun():
    try:
        fields, err = get_required_fields(['casename', 'caserunname', 'data'])
        if err:
            return err
        casename = fields['casename']
        caserunname = fields['caserunname']
        data = fields['data']

        if casename != None:
            caserun = DataFile(casename)
            response = caserun.createCaseRun(caserunname, data)
     
        return jsonify(response), 200
    except(IOError):
        return jsonify('No existing cases!'), 404

@datafile_api.route("/updateCaseRun", methods=['POST'])
def updateCaseRun():
    try:
        fields, err = get_required_fields(['casename', 'caserunname', 'oldcaserunname', 'data'])
        if err:
            return err
        casename = fields['casename']
        caserunname = fields['caserunname']
        oldcaserunname = fields['oldcaserunname']
        data = fields['data']

        if casename != None:
            caserun = DataFile(casename)
            response = caserun.updateCaseRun(caserunname, oldcaserunname, data)
     
        return jsonify(response), 200
    except(IOError):
        return jsonify('No existing cases!'), 404

@datafile_api.route("/deleteCaseRun", methods=['POST'])
def deleteCaseRun():
    try:        
        fields, err = get_required_fields(['casename', 'caserunname', 'resultsOnly'])
        if err:
            return err
        casename    = fields['casename']
        caserunname = fields['caserunname']
        resultsOnly = fields['resultsOnly']

        casePath = Path(Config.DATA_STORAGE, casename, 'res', caserunname)
        if not resultsOnly:
            shutil.rmtree(casePath)
        else:
            for item in os.listdir(casePath):
                item_path = os.path.join(casePath, item)
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.remove(item_path)  # delete file
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)  # delete subfolder

        if casename != None:
            caserun = DataFile(casename)
            response = caserun.deleteCaseRun(caserunname, resultsOnly)    
        return jsonify(response), 200

        # if casename == session.get('osycase'):
        #     session['osycase'] = None
        #     response = {
        #         "message": 'Case <b>'+ casename + '</b> deleted!',
        #         "status_code": "success_session"
        #     }
        # else:
        #     response = {
        #         "message": 'Case <b>'+ casename + '</b> deleted!',
        #         "status_code": "success"
        #     }
        # return jsonify(response), 200
    except(IOError):
        return jsonify('No existing cases!'), 404
    except OSError:
        raise OSError

@datafile_api.route("/deleteScenarioCaseRuns", methods=['POST'])
def deleteScenarioCaseRuns():
    try:
        fields, err = get_required_fields(['scenarioId', 'casename'])
        if err:
            return err
        scenarioId = fields['scenarioId']
        casename = fields['casename']

        if casename != None:
            caserun = DataFile(casename)
            response = caserun.deleteScenarioCaseRuns(scenarioId)
     
        return jsonify(response), 200
    except(IOError):
        return jsonify('No existing cases!'), 404

@datafile_api.route("/saveView", methods=['POST'])
def saveView():
    try:
        fields, err = get_required_fields(['casename', 'param', 'data'])
        if err:
            return err
        casename = fields['casename']
        param = fields['param']
        data = fields['data']

        if casename != None:
            caserun = DataFile(casename)
            response = caserun.saveView(data, param)
     
        return jsonify(response), 200
    except(IOError):
        return jsonify('No existing cases!'), 404

@datafile_api.route("/updateViews", methods=['POST'])
def updateViews():
    try:
        fields, err = get_required_fields(['casename', 'param', 'data'])
        if err:
            return err
        casename = fields['casename']
        param = fields['param']
        data = fields['data']

        if casename != None:
            caserun = DataFile(casename)
            response = caserun.updateViews(data, param)
     
        return jsonify(response), 200
    except(IOError):
        return jsonify('No existing cases!'), 404

@datafile_api.route("/readDataFile", methods=['POST'])
def readDataFile():
    try:
        fields, err = get_required_fields(['casename', 'caserunname'])
        if err:
            return err
        casename = fields['casename']
        caserunname = fields['caserunname']
        if casename != None:
            txtFile = DataFile(casename)
            data = txtFile.readDataFile(caserunname)
            response = data    
        else:  
            response = None     
        return jsonify(response), 200
    except(IOError):
        return jsonify('No existing cases!'), 404
    
@datafile_api.route("/validateInputs", methods=['POST'])
def validateInputs():
    try:
        fields, err = get_required_fields(['casename', 'caserunname'])
        if err:
            return err
        casename = fields['casename']
        caserunname = fields['caserunname']
        if casename != None:
            df = DataFile(casename)
            validation = df.validateInputs(caserunname)
            response = validation    
        else:  
            response = None     
        return jsonify(response), 200
    except(IOError):
        return jsonify('No existing cases!'), 404

@datafile_api.route("/downloadDataFile", methods=['GET'])
def downloadDataFile():
    try:
        #casename = request.json['casename']
        #casename = 'DEMO CASE'
        # txtFile = DataFile(casename)
        # downloadPath = txtFile.downloadDataFile()
        # response = {
        #     "message": "You have downloaded data.txt to "+ str(downloadPath) +"!",
        #     "status_code": "success"
        # }         
        # return jsonify(response), 200
        #path = "/Examples.pdf"
        case = session.get('osycase', None)
        caserunname = request.args.get('caserunname')
        dataFile = Path(Config.DATA_STORAGE,case, 'res',caserunname, 'data.txt')
        return send_file(dataFile.resolve(), as_attachment=True, max_age=0)
    
    except(IOError):
        return jsonify('No existing cases!'), 404

@datafile_api.route("/downloadFile", methods=['GET'])
def downloadFile():
    try:
        case = session.get('osycase', None)
        file = request.args.get('file')
        dataFile = Path(Config.DATA_STORAGE,case,'res','csv',file)
        return send_file(dataFile.resolve(), as_attachment=True, max_age=0)
    
    except(IOError):
        return jsonify('No existing cases!'), 404

@datafile_api.route("/downloadCSVFile", methods=['GET'])
def downloadCSVFile():
    try:
        case = session.get('osycase', None)
        file = request.args.get('file')
        caserunname = request.args.get('caserunname')
        dataFile = Path(Config.DATA_STORAGE,case,'res',caserunname,'csv',file)
        return send_file(dataFile.resolve(), as_attachment=True, max_age=0)
    
    except(IOError):
        return jsonify('No existing cases!'), 404

@datafile_api.route("/downloadResultsFile", methods=['GET'])
def downloadResultsFile():
    try:
        case = session.get('osycase', None)
        caserunname = request.args.get('caserunname')
        dataFile = Path(Config.DATA_STORAGE,case, 'res', caserunname,'results.txt')
        return send_file(dataFile.resolve(), as_attachment=True, max_age=0)
    
    except(IOError):
        return jsonify('No existing cases!'), 404

@datafile_api.route("/run", methods=['POST'])
def run():
    try:
        fields, err = get_required_fields(['casename', 'caserunname', 'solver'])
        if err:
            return err
        casename = fields['casename']
        caserunname = fields['caserunname']
        solver = fields['solver']
        txtFile = DataFile(casename)
        response = txtFile.run(solver, caserunname)     
        return jsonify(response), 200
    # except Exception as ex:
    #     print(ex)
    #     return ex, 404
    
    except(IOError):
        return jsonify('No existing cases!'), 404
    
@datafile_api.route("/batchRun", methods=['POST'])
def batchRun():
    try:
        start = time.time()
        fields, err = get_required_fields(['modelname', 'cases'])
        if err:
            return err
        modelname = fields['modelname']
        cases = fields['cases']

        if modelname != None:
            txtFile = DataFile(modelname)
            for caserun in cases:
                txtFile.generateDatafile(caserun)

            response = txtFile.batchRun( 'CBC', cases) 
        end = time.time()  
        response['time'] = end-start 
        return jsonify(response), 200
    except(IOError):
        return jsonify('Error!'), 404
    
@datafile_api.route("/cleanUp", methods=['POST'])
def cleanUp():
    try:
        fields, err = get_required_fields(['modelname'])
        if err:
            return err
        modelname = fields['modelname']

        if modelname != None:
            model = DataFile(modelname)
            response = model.cleanUp()    

        return jsonify(response), 200
    except(IOError):
        return jsonify('Error!'), 404