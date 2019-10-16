from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import re

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_event_dict(email_dict):
    """
    To frame the event dictionary which is to passed to Google calendar API for
    send, update, cancel meeting invite
    :param email_dict:
    Sample for Create Event:
     {
       'notes': 'Meeting for discussion',
       'start_time': '2019-10-29T07:10:00Z',
       'end_time': '2019-10-29T07:20:00Z',
       'client': {
         'name': 'client1',
         'email': 'shyamsundar.tg@gmail.com'
       },
       'service': 'service_1'
     }
    Sample for Reschedule Event:
     {
      'start_time': '2019-11-29T07:10:00Z',
      'end_time': '2019-11-29T07:20:00Z',
      'notes': 'Meeting for discussion',
      'service': 'service_1',
      'client': {
        'name': 'client1',
        'email': 'shyamsundar.tg@gmail.com'
      }
    }
    Sample for Cancel Event:
     {
      'start_time': '2019-11-29T07:10:00Z',
      'end_time': '2019-11-29T07:20:00Z',
      'notes': 'Meeting for discussion',
      'service': 'service_1',
      'cancelled': True,
      'cancellation_reason': 'I cancelled',
      'client': {
        'name': 'client1',
        'email': 'shyamsundar.tg@gmail.com'
      }
    }
    :return: Event dictionary
    """
    summary = ''
    if len(email_dict['users']) == 1:
        """
        Summary for 1-1 invite
        """
        summary = summary + email_dict['users'][0]['name'] + " and " + email_dict['client']['name']
    else:
        """
        Summary for group invite
        """
        summary = summary + email_dict['service']
    attendees = [{'email': email_dict['client']['email']}]
    event = {
        'summary': summary,
        'location': email_dict['service'],
        'description': "<h1>"+ email_dict['notes'] + "</h1>",
        'start': {
            'dateTime': email_dict['start_time'],
            'timeZone': email_dict['start_time'],
        },
        'end': {
            'dateTime': email_dict['end_time'],
            'timeZone': email_dict['end_time'],
        },
        # 'recurrence': [
        #     'RRULE:FREQ=DAILY;COUNT=2'
        # ],
        'attendees': attendees,
        # 'reminders': {
        #     'useDefault': False,
        #     'overrides': [
        #         {'method': 'email', 'minutes': 24 * 60},
        #         {'method': 'popup', 'minutes': 10},
        #     ],
        # },
    }
    return event


def run_gcal_setup():
    """
    Takes care of handling authorization to trigger notification from google calendar API
    :return: Google Cal object
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'appointment_scheduler/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('calendar', 'v3', credentials=creds)
    return service

def send_invite_through_gcal(email_dict):
    """
    Send meeting invite using Google calendar API
    :param: email_dict
        Sample for Create Event:
     {
       'notes': 'Meeting for discussion',
       'start_time': '2019-10-29T07:10:00Z',
       'end_time': '2019-10-29T07:20:00Z',
       'client': {
         'name': 'client1',
         'email': 'shyamsundar.tg@gmail.com'
       },
       'service': 'service_1'
     }
    :return : event ID if event is created
    """
    service = run_gcal_setup()
    event = get_event_dict(email_dict)
    event_created = service.events().insert(calendarId='primary', body=event, sendUpdates="all").execute()
    return event_created.get('id')


def update_invite_through_gcal(email_dict, event_id):
    """
    Send reschedule invite using Google calendar API
    :param email_dict:
    Sample for Reschedule Event:
     {
      'start_time': '2019-11-29T07:10:00Z',
      'end_time': '2019-11-29T07:20:00Z',
      'notes': 'Meeting for discussion',
      'service': 'service_1',
      'client': {
      'name': 'client1',
        'email': 'shyamsundar.tg@gmail.com'
      }
    }
    :param event_id: Event ID to be rescheduled
    """
    service = run_gcal_setup()
    event = get_event_dict(email_dict)
    service.events().update(calendarId='primary', eventId=event_id, body=event, sendUpdates="all").execute()


def cancel_invite_through_gcal(email_dict, event_id):
    """
    Cancel invite using Google calendar API
    :param email_dict:
        Sample for Cancel Event:
         {
          'start_time': '2019-11-29T07:10:00Z',
          'end_time': '2019-11-29T07:20:00Z',
          'notes': 'Meeting for discussion',
          'service': 'service_1',
          'cancelled': True,
          'cancellation_reason': 'I cancelled',
          'client': {
          'name': 'client1',
            'email': 'shyamsundar.tg@gmail.com'
          }
        }
    :param event_id: Event ID to be cancelled
    """
    service = run_gcal_setup()
    event = get_event_dict(email_dict)
    event['status'] = "cancelled"
    event['description'] = email_dict['cancellation_reason']
    service.events().update(calendarId='primary', eventId=event_id, body=event, sendUpdates="all").execute()
