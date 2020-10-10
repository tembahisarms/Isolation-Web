def places_to_nodes(place):
    return {
        'id': place.id,
        'label': place.name,
        'zip': place.zip_code,
        'size': 1,
        'color': '#009',
        'x': place.lng,
        'y': place.lat * -1,
    }
