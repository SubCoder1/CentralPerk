from django.conf import settings
from django.shortcuts import redirect, render

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
