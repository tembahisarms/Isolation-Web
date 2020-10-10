from django.http import JsonResponse
from django.db.models import Count
import uuid
from django.urls import reverse
from django.shortcuts import redirect


from webmanager.helpers.places_to_nodes import places_to_nodes
from webmanager.models import Place, Person, ConnectedPlace

# {
#   "nodes": [
#     {
#       "id": "f531b79b-02aa-48a6-8b08-e8b4fb8ee24d",
#       "label": "Bohemia",
#       "x": -73.9828,
#       "y": -40.6669,
#       "size": 1,
#       "color": "#009"
#     },
#   ],
#   "edges": [
#     {
#       "id": "bc2bec12-31de-4a22-90f3-e21185aa3a26",
#       "source": "f531b79b-02aa-48a6-8b08-e8b4fb8ee24d",
#       "target": "60e5be64-021b-4197-b35d-9e555bfa02c5"
#     },
#   ]
# }
def _user_connections_to_edges(connected_place):
  return {
    'id': uuid.uuid4(),
    'source': connected_place.place.id,
    'target': connected_place.connected_place.id,
  }


def render_data(request):
    places = Place.objects.filter()
    connected_places = ConnectedPlace.objects.filter()
    data = {
        'nodes': list(map(places_to_nodes, places)),
        'edges': list(map(_user_connections_to_edges, connected_places))
    }

    return JsonResponse(data)


def make_tooltip(a_place, request):
    if request.user.is_authenticated and request.user.person is not None and request.user.person.place is not None: 
        home = request.user.person.place
        # if this place is home and this place was created by me, show 'update my household'
        if (a_place == home and a_place.created_by == request.user):
            url = reverse('place-update', kwargs={'pk': a_place.pk})
            text = "Update my household"
            link = f'<a href="{url}" class="button">{text}</button>'
        elif (a_place == home):
            url = reverse('place-update', kwargs={'pk': a_place.pk})
            text = "View my household"
            link = f'<a href="{url}" class="button">{text}</button>'
        # if this place is connected to my home, show 'Disconnect households'
        elif (ConnectedPlace.objects.filter(place=home, connected_place=a_place)):
            url = reverse('place-disconnect', kwargs={
                'place_one_id': home.id,
                'place_two_id': a_place.id
            })
            text = "Disconnect households"
            link = f'<a href="{url}" class="button js-disconnect">{text}</button>'
        # if this place is connected to my home, but they made the connection, show 'Disconnect households'
        elif (ConnectedPlace.objects.filter(place=a_place, connected_place=home)):
            url = reverse('place-disconnect', kwargs={
                'place_one_id': a_place.id,
                'place_two_id': home.id
            })
            text = "Disconnect households"
            link = f'<a href="{url}" class="button js-disconnect">{text}</button>'
        # if this place is not connected to my home, show 'Add interaction'
        else:
            url = reverse('place-connect', kwargs={
                'place_one_id': request.user.person.place.id, 
                'place_two_id': a_place.pk
            })
            text = "Connect households"
            link = f'<a href="{url}" class="button js-connect">{text}</button>'
    # if the user is authenticated but doesn't have a home, show 'Add me to this home'
    elif request.user.is_authenticated:
        url = reverse('person-connect', kwargs={'place_id': a_place.id})
        text = 'Add me to this home'
        link = f'<a href="{url}" class="button js-person-add">{text}</button>'
    # if the user is not authenticated, just show place information
    else:
        link = ''
    
    if a_place.member_count > 1:
        plural = 's'
    else:
        plural = ''

    source_connections = ConnectedPlace.objects.filter(place = a_place).count()
    target_connections = ConnectedPlace.objects.filter(connected_place = a_place).count()
    total_connections = source_connections + target_connections

    return (
        f'<div id="{a_place.id}">'
        f'<h4><strong>{a_place.name}</strong></h4>'
        f'<p>{a_place.member_count} household member{plural}</p>'
        f'<p>Direct Connections: {total_connections}</p>'
        f'{link}'
        f'</div>'
    )

def d3_nodes(places, request):
    nodes = []
    for place in places:
        node = {
            'id': place.id,
            'label': place.name,
            'zip': place.zip_code,
            'size': 1,
            'color': '#009',
            'x': place.lng,
            'y': place.lat * -1,
        }
        node['tooltip'] = make_tooltip(place, request)
        nodes.append(node)
    return nodes    

def d3_data(request):
    places = Place.objects.filter()
    connected_places = ConnectedPlace.objects.filter()

    data = {
        'nodes': d3_nodes(places, request),
        'edges': list(map(_user_connections_to_edges, connected_places))
    }

    return JsonResponse(data)


def connect_person(request, place_id):
    if request.user.is_authenticated:
        my_home = Place.objects.get(id=place_id)
        request.user.person.place = my_home
        request.user.person.save()

        data = {
            'nodes': d3_nodes([my_home], request)
        }
        return JsonResponse(data)
    else:
        return JSONResponse({
                'success': False
            })

def disconnect_person(request, place_id):
    if request.user.is_authenticated:
        if request.user.person.place.id == place_id:
            request.user.person.place = None
            request.user.person.save()

    return redirect(reverse('d3web'))


def connect(request, place_one_id, place_two_id):
    my_home = Place.objects.get(id=place_one_id)
    connected_home = Place.objects.get(id=place_two_id)

    connected_place = ConnectedPlace(place=my_home, connected_place=connected_home)
    connected_place.save()

    data = {
        'nodes': d3_nodes([my_home, connected_home], request), 
        'edges': [_user_connections_to_edges(connected_place)]
    }

    return JsonResponse(data)


def disconnect(request, place_one_id, place_two_id):
    place_one = Place.objects.get(id = place_one_id)
    place_two = Place.objects.get(id = place_two_id)

    connected_places = ConnectedPlace.objects.filter(place=place_one_id, connected_place=place_two_id)
    connected_places[0].delete()

    data = {
        'nodes': d3_nodes([place_one, place_two], request)
    }

    return JsonResponse(data)
