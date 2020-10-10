from django.urls import path

from .views import data, place, search, users
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name="landing-page.html"), name='home'),
    path('data', data.d3_data, name='data'),
    path('old-data', data.render_data, name='old-data'),
    path('search', search.results, name='search'),
    path('place/add/', place.PlaceCreate.as_view(), name='place-add'),
    path('place/<uuid:pk>/', place.PlaceUpdate.as_view(), name='place-update'),
    path('place/<uuid:pk>/delete/', place.PlaceDelete.as_view(), name="place-delete"),
    path('person/connect/<uuid:place_id>', data.connect_person, name='person-connect'),
    path('person/disconnect/<uuid:place_id>', data.disconnect_person, name='person-disconnect'),
    path('place/connect/<uuid:place_one_id>/<str:place_two_id>', data.connect, name="place-connect"),
    path('place/disconnect/<uuid:place_one_id>/<str:place_two_id>', data.disconnect, name="place-disconnect")
]
