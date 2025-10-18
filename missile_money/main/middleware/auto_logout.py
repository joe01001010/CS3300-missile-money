import datetime
from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import redirect

class AutoLogout:
    """
    This middleware will automatically logout a user if they are inactive for a certain amount of time
    The default timeout is 15 minutes, but can be changed in the settings.py file
    There is no return value for this class
    """
    def __init__(self, get_response):
        """
        This function will initialize the middleware
        There is no return value for this function
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        This function will check if the user is authenticated and if they are inactive for a certain amount of time
        If they are, it will logout the user and redirect to the login page
        There is no return value for this function
        """
        if not request.user.is_authenticated:
            return self.get_response(request)

        now = datetime.datetime.now()
        last_activity = request.session.get('last_activity')

        if last_activity:
            elapsed = (now - datetime.datetime.fromisoformat(last_activity)).total_seconds()
            if elapsed > getattr(settings, 'AUTO_LOGOUT_DELAY', 15 * 60):
                logout(request)
                request.session.flush()
                return redirect('login')

        request.session['last_activity'] = now.isoformat()
        return self.get_response(request)