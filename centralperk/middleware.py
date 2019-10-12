from django.conf import settings
from django.shortcuts import redirect, render, reverse
from django.contrib.auth import logout
from django.db import close_old_connections
from session_security.middleware import SessionSecurityMiddleware
from session_security.utils import set_last_activity, get_last_activity
from datetime import datetime, timedelta
from AUth.tasks import update_user_activity_on_logout

class login_required_middleware:
    """ This middleware takes care of anonymous users trying to visit links that requires an user to be logged-in.
        Also, non-admin users trying to access the admin panel 
    """

    admin_base_path = '/admin/'

    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """ process_view() is called just before Django calls the view """

        assert hasattr(request, 'user'), "assertion error in login_required_middleware()"
        path = request.path_info
        if request.user.is_authenticated:
            if not request.user.is_admin():
                if path == self.admin_base_path:
                    return render(request, 'trespass.html', {})
            if path == '/':    
                return redirect('/home/')
        else:    
            if path not in settings.LOGIN_EXEMPT_URL:
                return redirect(settings.LOGIN_URL)

class SessionActivityMiddleware(SessionSecurityMiddleware):
    def process_request(self, request):
        close_old_connections()
        """ Update last activity time or logout. """
        if not request.user.is_authenticated:
            return
        now = datetime.now()
        if '_session_security' not in request.session:
            set_last_activity(request.session, now)
            return

        delta = now - get_last_activity(request.session)
        expire_seconds = self.get_expire_seconds(request)
        if delta >= timedelta(seconds=expire_seconds):
            # Log the user out
            update_user_activity_on_logout.delay(request.user.username)
            logout(request)
        elif (request.path == reverse('session_security_ping') and
                'idleFor' in request.GET):
            self.update_last_activity(request, now)
        elif not self.is_passive_request(request):
            set_last_activity(request.session, now)
        close_old_connections()