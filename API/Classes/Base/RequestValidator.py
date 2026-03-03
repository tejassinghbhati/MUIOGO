from flask import request, jsonify


def get_required_fields(fields: list):
    """
    Extract and validate required fields from the request JSON body.

    Returns:
        (data_dict, None)        — on success, data_dict contains all requested fields
        (None, error_response)   — if body is not JSON or any field is missing

    Usage:
        fields, err = get_required_fields(['casename', 'caserunname'])
        if err:
            return err
        casename    = fields['casename']
        caserunname = fields['caserunname']
    """
    if not request.is_json or request.json is None:
        return None, (jsonify({
            "message": "Request body must be valid JSON.",
            "status_code": "error"
        }), 400)

    data = {}
    for field in fields:
        if field not in request.json:
            return None, (jsonify({
                "message": f"Missing required field: '{field}'",
                "status_code": "error"
            }), 400)
        data[field] = request.json[field]

    return data, None
