from rest_framework.views import exception_handler

def handler(exc, context):
    # Call REST framework's default exception handler first,
    print("request.data ", context["request"].data)

    print("\n\n\nExceptions",  exc)
    # to get the standard error response.
    response = exception_handler(exc, context)
    # Now add the HTTP status code to the response.
    if response is not None:
        response.data['status_code'] = response.status_code
    return response