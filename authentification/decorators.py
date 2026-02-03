from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from functools import wraps
from django.urls import reverse
from django.shortcuts import redirect


def user_is_in_group(*group_names):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                return redirect(reverse('forbidden', kwargs={'code': 401}))
            if user.groups.filter(name__in=group_names).exists():
                return view_func(request, *args, **kwargs)
            return redirect(reverse('forbidden', kwargs={'code': 403}))
        return _wrapped_view
    return decorator