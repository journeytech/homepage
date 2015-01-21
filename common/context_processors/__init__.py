from django.contrib.sites.models import Site


def site_name(request):
    return {'SITE_NAME': Site.objects.get_current().name}
