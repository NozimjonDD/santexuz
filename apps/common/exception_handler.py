from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if response is not None:
        # Customize the response data
        key = None
        value = None
        token_not_valid = False
        for key, value in response.data.items():
            key = key
            value = value

            if value == 'token_not_valid':
                token_not_valid = True

        if token_not_valid:
            # not customize the response data
            return response

        if type(value) == list and len(value) == 1:
            code = value[0].code
            detail = value[0]
        else:
            code = value.code
            detail = value
        customized_response = {
            'error': True,
            'code': code,
            'status_code': response.status_code,
            'key': key,
            'detail': detail,
            'data': None
        }
        return Response(customized_response, status=response.status_code)

    # If the exception is not handled by DRF, return a generic error response
    # return Response({
    #     'error': True,
    #     'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR,
    #     'message': 'Internal server error.',
    #     'data': None
    # }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return response
