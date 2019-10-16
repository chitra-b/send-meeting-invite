from django.db import models
from timezone_field import TimeZoneField
import pytz


class Appointments(models.Model):
    date_created = models.DateTimeField(
        auto_now_add=True, blank=False, null=False)
    client = models.TextField(
        max_length=255, null=False, blank=False)
    start_time = models.DateTimeField(blank=False, null=False)
    end_time = models.DateTimeField(blank=False, null=False)
    cancelled = models.BooleanField(default=False)
    cancellation_reason = models.CharField(
        max_length=255, blank=True, null=True)
    timezone_field = TimeZoneField(default='UTC', choices=[(tz, tz) for tz in pytz.all_timezones])
    notes = models.TextField(
        max_length=255, blank=True, null=True)
    event_identifier = models.CharField(
        max_length=255, blank=True, null=True, unique=False)


    class Meta:
        db_table = 'appointments'
        permissions = [
            ("can_view_own_appointments", "Can view own appointments"),
            ("can_view_peers_appointments", "Can view peers appointments"),
        ]
        ordering = ['start_time']

    def __str__(self):
        return "{} - {}".format(self.start_time, self.end_time)