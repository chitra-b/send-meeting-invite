from rest_framework import serializers, utils
from . import models, tasks

class AppointmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Appointments
        fields = ('id', 'start_time', 'end_time', 'notes', 'lead_status',
                  'client', 'cancelled', 'cancellation_reason')


    def create(self, validated_data):
        """
        To post appointment to DB
        :param validated_data: POST Data
        :return: Instance created
        """
        post_data = validated_data
        email_dict = {
            'notes': post_data['notes'],
            'start_time': validated_data['start_time'],
            'end_time': validated_data['end_time'],
            'client': {
                'name': post_data['client'],
                'email': post_data['client']},
        }
        pref_instance = models.Appointments.objects.create(**validated_data)
        tasks.send_email.delay(email_dict, pref_instance.id)
        return pref_instance

    def update(self, instance, validated_data):
        """
        To reschedule or cancel appointment
        :param instance: Appointment instance to be cancelled or rescheduled
        :param validated_data: Put /Patch Data
        :return: Instance updated in appointment model
        """
        post_data = validated_data
        email_dict = {

        }
        info = utils.model_meta.get_field_info(instance)
        # If reschedule
        if "start_time" in validated_data or "end_time" in validated_data:
            email_dict.update({
                'start_time': validated_data['start_time'],
                'end_time': validated_data['end_time'],
                'notes': instance.notes,
                'client': {
                    'name': instance.client,
                    'email': instance.client}
            })
        else:
            email_dict.update({
                'start_time': getattr(instance, 'start_time'),
                'end_time': getattr(instance, 'end_time'),
                'notes': instance.notes,
                'cancelled': validated_data['cancelled'],
                'cancellation_reason':  validated_data['cancellation_reason'],
                'client': {
                    'email': instance.client.client_email_id},

            })
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                field = getattr(instance, attr)
                field.set(value)
            else:
                setattr(instance, attr, value)
        instance.save()
        tasks.send_update_email.delay(email_dict, instance.event_identifier)
        return instance
