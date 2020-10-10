import os

from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views import generic
from django.urls import reverse_lazy
from uszipcode import SearchEngine
from django.contrib.auth.mixins import LoginRequiredMixin
from django import forms
from django.forms.models import inlineformset_factory
from django.db import transaction

from webmanager.models import Place, Person, ConnectedPlace

zipcode_db_dir = os.path.join(os.path.dirname(__file__), ".uszipcode")
print(zipcode_db_dir)
search = SearchEngine(simple_zipcode=True, db_file_dir=zipcode_db_dir)

def update_or_detail(request, pk):
	the_place = Place.objects.get(id=pk)
	if request.user.is_authenticated and the_place.created_by == request.user:
		return PlaceUpdate.as_view()
	else:
		return PlaceView.as_view()



class PlaceView(generic.DetailView):
    model = Place
    template_name = 'place_detail.html'

# https://dev.to/zxenia/django-inline-formsets-with-class-based-views-and-crispy-forms-14o6
# https://docs.djangoproject.com/en/3.1/topics/forms/modelforms/#inline-formsets

PersonFormSet = inlineformset_factory(Place, Person,
	fields=('id', 'name'),
	widgets={
		'name': forms.TextInput(attrs={'readonly':'readonly'}),
	}, extra=0)

class PlaceUpdate(LoginRequiredMixin, generic.UpdateView):
	model = Place
	fields = ['name', 'zip_code', 'member_count']

	# def get(self, request, *args, **kwargs):
	# 	the_place = Place.objects.get(id=kwargs.get('pk'))
	# 	if request.user.is_authenticated and the_place.created_by == request.user:
	# 		return super().get(request, *args, **kwargs)
	# 	else: 
	# 		return PlaceView.as_view()

	def get_context_data(self, **kwargs):
		data = super(PlaceUpdate, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated and self.object.created_by == self.request.user:
			data['my_home'] = True
		else:
			data['my_home'] = False
		if self.request.POST:
			data['personFormSet'] = PersonFormSet(self.request.POST, instance=self.object)
		else:
			data['personFormSet'] = PersonFormSet(instance=self.object)
		return data

	def form_valid(self, form):
		context = self.get_context_data()
		members = context['personFormSet']

		# this just removes the person from the house
		self.object = form.save()
		for member in members.deleted_forms:
			member.instance.place=None
			member.instance.save()

		# this will actually delete the person from the system entirely
		# with transaction.atomic():
		# 	self.object = form.save()
		# 	if members.is_valid():
		# 		members.instance = self.object
		# 		members.save()
		return super(PlaceUpdate, self).form_valid(form)

class PlaceCreate(LoginRequiredMixin, generic.CreateView):
	model = Place
	fields = ['name', 'zip_code', 'member_count']
	success_url = "/d3web"

	def get_context_data(self, **kwargs):
		data = super(PlaceCreate, self).get_context_data(**kwargs)
		# if self.request.POST:
		# 	print(self.request.POST)
		# 	data['personFormSet'] = PersonFormSet(self.request.POST)
		# else:
		# 	data['personFormSet'] = PersonFormSet()
		return data

	def form_valid(self, form):
		form.instance.lat = search.by_zipcode(form.instance.zip_code).lat
		form.instance.lng = search.by_zipcode(form.instance.zip_code).lng
		context = self.get_context_data()
		form.instance.created_by = self.request.user
		
		# members = context['personFormSet']
		with transaction.atomic():
			self.object = form.save()
			# if members.is_valid():
			# 	members.instance = self.object
			# 	members.save()
		
		person = self.request.user.person
		person.place = self.object
		person.save()
		self.request.user.person.save()
		return super(PlaceCreate, self).form_valid(form)

class PlaceDelete(LoginRequiredMixin, generic.DeleteView):
	model = Place
	success_url = reverse_lazy('home')

