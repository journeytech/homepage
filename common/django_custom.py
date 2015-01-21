'''
Created on Aug 23, 2013

@author: antipro
'''
from django.http.response import HttpResponse, HttpResponseRedirect
from django.utils.http import is_safe_url
from django.shortcuts import resolve_url
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.urlresolvers import reverse

from . import json_serializer


def HttpJson(obj, status=200):
    content = json_serializer.JSONSerializer().serialize(obj, use_natural_keys=True)
    return HttpResponse(content, content_type="application/json", status=status)


def get_go_back_url(request, redirect_fieldname=REDIRECT_FIELD_NAME, default='/'):
    redirect_to = request.REQUEST.get(redirect_fieldname)
    if redirect_to == reverse('logout') or not is_safe_url(url=redirect_to, host=request.get_host()):
        redirect_to = request.META.get('HTTP_REFERER')
        if redirect_to == reverse('logout') or not is_safe_url(url=redirect_to, host=request.get_host()):
            redirect_to = resolve_url(default) if default else None
    return redirect_to


def HttpGoBack(request, redirect_fieldname=REDIRECT_FIELD_NAME, default='/'):
    redirect_to = get_go_back_url(request, redirect_fieldname)
    return HttpResponseRedirect(redirect_to)
