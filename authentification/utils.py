from django.contrib.sessions.models import Session
from django.utils import timezone

def logout_other_sessions(request, user):
    current_session_key = request.session.session_key

    sessions = Session.objects.filter(expire_date__gte=timezone.now())

    for session in sessions:
        data = session.get_decoded()

        if str(data.get("_auth_user_id")) == str(user.id):
            if session.session_key != current_session_key:
                session.delete()