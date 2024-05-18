def error_message(message, data=0, code=0):
    response_dictionary = dict()
    response_dictionary["message"] = message
    response_dictionary["data"] = data
    response_dictionary["is_success"] = False
    response_dictionary['code'] = code
    return response_dictionary


def success_message(message, data=0, code=0):
    response_dictionary = dict()
    response_dictionary["message"] = message
    response_dictionary["data"] = data
    response_dictionary["is_success"] = True
    response_dictionary['code'] = code
    return response_dictionary
