
from django.contrib.sessions.models import Session

def session_delete(user_id):
    for session in Session.objects.all():
        if session.get_decoded():
            try:
                uid = session.get_decoded().get('_auth_user_id')
                if not(uid is None) and (user_id == uid):
                    print uid
                    session.delete()
                    return
            except:
                continue
    return 
