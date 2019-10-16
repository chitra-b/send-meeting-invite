from datetime import datetime
from icalendar import Calendar, Event
from django.http import HttpResponse
from django.core.mail import EmailMessage
from send_meeting_invite import settings


def send_invite(site_name, domain):
    cal = Calendar()
    cal.add('prodid', '-//%s Events Calendar//%s//' % (site_name, domain))
    cal.add('version', '2.0')
    site_token = domain.split('.')
    site_token.reverse()
    site_token = '.'.join(site_token)
    ical_event = Event()
    ical_event.add('summary', "Test Mail")
    ical_event.add('dtstart', datetime(2019, 10, 4, 9, 00, 00, 000000))
    ical_event.add('dtend', datetime(2019, 10, 4, 9, 30, 00, 000000))
    ical_event.add('dtstamp', datetime(2019, 10, 4, 9, 30, 00, 000000))
    ical_event['uid'] = '92D01317-F86A-42FC-8E8B-B19C969B5C50'
    cal.add_component(ical_event)
    slug ="invite"
    response = HttpResponse(cal.to_ical(), content_type="text/calendar")
    response['Content-Disposition'] = 'attachment; filename=%s.ics' % slug
    # email_from = settings.EMAIL_HOST_USER
    # recipient_list = ['chitrabala274@gmail.com', ]
    # email = EmailMessage('Meeting invitation', 'Email body...', email_from, recipient_list)
    # email.attach('invite.ics', response)
    # email.send()
    return response
    # return HttpResponse("<h1> sent mail</h1>")