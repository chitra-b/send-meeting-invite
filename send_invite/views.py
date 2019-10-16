from . import models, serializers
from rest_framework import viewsets
from django.http import JsonResponse, HttpResponse


class AppointmentsViewSet(viewsets.ModelViewSet):
    """
    Handles managing user preferences
    """

    queryset = models.Appointments.objects.filter
    serializer_class = serializers.AppointmentSerializer