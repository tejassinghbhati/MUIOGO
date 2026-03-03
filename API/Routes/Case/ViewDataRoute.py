from flask import Blueprint, jsonify, request
from Classes.Case.OsemosysClass import Osemosys
from Classes.Base.RequestValidator import get_required_fields

viewdata_api = Blueprint('ViewDataRoute', __name__)

@viewdata_api.route("/viewData", methods=['POST'])
def viewData():
    try:
        fields, err = get_required_fields(['casename'])
        if err:
            return err
        casename = fields['casename']
        if casename != None:
            osy = Osemosys(casename)
            data = {}
            data['Tech'] = osy.viewDataByTech()
            data['Comm'] = osy.viewDataByComm()
            data['Emi'] = osy.viewDataByEmi()
            response = data    
        else:  
            response = None     
        return jsonify(response), 200
    except(IOError):
        return jsonify('No existing cases!'), 404

@viewdata_api.route("/viewTEData", methods=['POST'])
def viewTEData():
    try:
        fields, err = get_required_fields(['casename'])
        if err:
            return err
        casename = fields['casename']
        if casename != None:
            osy = Osemosys(casename)
            data = {}
            data['Tech'] = osy.viewRTByTech()
            data['Emi'] = osy.viewREByEmi()
            response = data    
        else:  
            response = None     
        return jsonify(response), 200
    except(IOError):
        return jsonify('No existing cases!'), 404

@viewdata_api.route("/updateViewData", methods=['POST'])
def updateViewData():
    try:
        fields, err = get_required_fields(['casename', 'year', 'ScId', 'groupId', 'paramId', 'TechId', 'CommId', 'EmisId', 'Timeslice', 'value'])
        if err:
            return err
        casename   = fields['casename']
        year       = fields['year']
        ScId       = fields['ScId']
        groupId    = fields['groupId']
        paramId    = fields['paramId']
        TechId     = fields['TechId']
        CommId     = fields['CommId']
        EmisId     = fields['EmisId']
        Timeslice  = fields['Timeslice']
        value      = fields['value']

        if casename != None:
            osy = Osemosys(casename)
            osy.updateViewData(casename, year, ScId, groupId, paramId, TechId, CommId, EmisId, Timeslice, value)
            response = {
                "message": "You have updated view data!",
                "status_code": "success"
            }
        else:
            response = {
                "message": "No case data selected!",
                "status_code": "error"
            }
       
        return jsonify(response), 200
    except(IOError):
        return jsonify('No existing cases!'), 404

@viewdata_api.route("/updateTEViewData", methods=['POST'])
def updateTEViewData():
    try:
        fields, err = get_required_fields(['casename', 'scId', 'groupId', 'paramId', 'techId', 'emisId', 'value'])
        if err:
            return err
        casename = fields['casename']
        scId     = fields['scId']
        groupId  = fields['groupId']
        paramId  = fields['paramId']
        techId   = fields['techId']
        emisId   = fields['emisId']
        value    = fields['value']

        if casename != None:
            osy = Osemosys(casename)
            data = osy.updateTEViewData(casename, scId, groupId, paramId, techId, emisId, value)
            response = {
                "message": "You have updated view data!",
                "status_code": "success"
            }
        else:
            response = {
                "message": "No case data selected!",
                "status_code": "error"
            }
       
        return jsonify(response), 200
    except(IOError):
        return jsonify('No existing cases!'), 404
