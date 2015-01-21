'''
Created on Oct 21, 2013

@author: antipro
'''


class GoogleAnalytics(object):
    def __init__(self):
        self.pageview = {}

    def process_request(self, request):
        request.google_analytic = GoogleAnalytics()
