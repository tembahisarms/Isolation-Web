from django.http import JsonResponse

from webmanager.helpers.places_to_nodes import places_to_nodes
from webmanager.models import Place
from django.contrib.auth.models import User
from itertools import chain

# Search results can have a name and/or zip parameter. Name is used for a contains-text
# lookup. Zip matching is exact.
def results(request):
    searchTerm = request.GET.get('search')

    search_by_people = Place.objects.filter(person__user__email__icontains=searchTerm).distinct().values('name', 'member_count', 'zip_code')
    search_by_zip = Place.objects.filter(zip_code=searchTerm).values('name', 'member_count', 'zip_code')

    result_list = list(chain(search_by_people, search_by_zip))

    # name = request.GET.get('name')
    # zip = request.GET.get('zip')

    # if name and zip:
    #     places = Place.objects.filter(name__icontains=name, zip_code=zip)
    # elif name:
    #     places = Place.objects.filter(name__icontains=name)
    # elif zip:
    #     places = Place.objects.filter(zip_code=zip)
    # else:
    #     places = Place.objects.filter()

    # data = {
    #     'name': name,
    #     'zip': zip,
    #     'nodes': list(map(places_to_nodes, places)),
    # }

    return JsonResponse({'results': result_list})
