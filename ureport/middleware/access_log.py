import logging
log = logging.getLogger(__name__)



class UreportAccessLogMiddleware:
    # THis doesnt ever seem to get called!!
    def process_exception(self, request, exception):
        import traceback
        import sys
        exc_info = sys.exc_info()
        log.exception(exception)
        log.info('\n'.join(traceback.format_exception(*(exc_info or sys.exc_info()))))


    def process_request(self, request):
        log.info('{:6s} : {} ? {}'.format(request.method, request.path, str(request.GET.items())))



# Can't get this to work, it seems to mess with the response.
#    def process_response(self, request, response):
#        log.info(request.path + " : returned " + str(response.status_code))

