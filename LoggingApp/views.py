from django.http import HttpResponse
import datetime
# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger('main')

def login_view(request):
    logger.info('You accessed this page at '+str(datetime.datetime.now())+' hours!')
    return HttpResponse("<h1>Welcome to Appmigro, Enjoy your stay .</h1>")