import uuid
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Q


# Places define physical entities. In the Isolation Web, they generally represent
# homes. Their residents are modeled as people, where people are abstractions of
# humans, in order to avoid privacy concerns.
#
# When people move between places, this creates connections. The connections are
# modeled between places.
#
# Covid statuses are set on people. They can be propagated up to places and spread
# visually throughout the isolation web to show risk and spread.
class Place(models.Model):
    id = models.UUIDField(null=False, default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=256)
    zip_code = models.CharField(max_length=10)
    lat = models.DecimalField(max_digits=11, decimal_places=8)
    lng = models.DecimalField(max_digits=11, decimal_places=8)
    created_by = models.OneToOneField(User, on_delete=models.CASCADE, related_name='owner')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    member_count = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.name}"

    def get_absolute_url(self):
        return reverse('place-update', kwargs={'pk': self.pk})

    def pending_connection(self, another_place):
        connections = self.connected_place.filter(
            Q(verified=False) | Q(verified=None)).values('place')
        they_started_it = [d['place'] for d in connections]

        if another_place.id in they_started_it:
            return True

    def waiting_connection(self, another_place):
        connections = self.connectedplace_set.filter(
            Q(verified=False) | Q(verified=None)).values('connected_place')
        i_started_it = [d['connected_place'] for d in connections]

        if another_place.id in i_started_it:
            return True

    def is_connected(self, another_place):
        i_started_it = [d['connected_place'] for d in self.connectedplace_set.filter(verified=True).values('connected_place')]
        they_started_it = [d['place'] for d in self.connected_place.filter(verified=True).values('place')]

        if another_place.id in i_started_it:
            return True
        if another_place.id in they_started_it:
            return True

        return False

    def waiting_deletion(self, another_place):
        connections = self.connectedplace_set.filter(
            verified=True).filter(delete_requested=True).values('connected_place')
        i_started_it = [d['connected_place'] for d in connections]

        if another_place.id in i_started_it:
            return True

    def pending_deletion(self, another_place):
        connections = self.connected_place.filter(
            verified=True).filter(delete_requested=True).values('place')
        they_started_it = [d['place'] for d in connections]

        if another_place.id in they_started_it:
            return True


class ConnectedPlace(models.Model):
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    connected_place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='connected_place')
    verified = models.BooleanField(null=False, default=False)
    delete_requested = models.BooleanField(null=False, default=False)

    objects = models.Manager()

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['place', 'connected_place'], 
            name='unique_connection')]

    def __str__(self):
        return f"{self.place} -> {self.connected_place}"


class Person(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, help_text="To delete this Person go to User admin")
    place = models.ForeignKey(Place, on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def owner(self):
        return self.user.owner

    def __str__(self):
        return f"{self.name}"
