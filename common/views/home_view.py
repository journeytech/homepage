'''
Created on Jul 28, 2013

@author: antipro
'''
from django.template.response import TemplateResponse


def main(request, template="homepage.html"):
    data = {}

    data['show_top_banner'] = True

    return TemplateResponse(request, template, data)
