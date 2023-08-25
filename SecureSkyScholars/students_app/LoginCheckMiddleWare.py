"""Module to check middleware"""
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin


class LoginCheckMiddleWare(MiddlewareMixin):
    """Login Check Middle Ware."""
    def process_view(self,request,view_func,view_args,view_kwargs):
        """module to process view"""
        print(view_args,view_kwargs)
        modulename=view_func.__module__
        print(modulename)
        user=request.user
        if user.is_authenticated:
            if user.user_type == "1":
                if modulename == "student_management_app.HodViews":
                    pass
                elif modulename in {'student_management_app.views', 'django.views.static'}:
                    pass
                elif modulename in {'django.contrib.auth.views', 'django.contrib.admin.sites'}:
                    pass
                else:
                    return HttpResponseRedirect(reverse("index"))
            elif user.user_type == "2":
                if modulename in { "student_management_app.StaffViews",
                                  "student_management_app.EditResultVIewClass"} :
                    pass
                elif modulename in { "student_management_app.views", "django.views.static"}:
                    pass
                else:
                    return HttpResponseRedirect(reverse("staff_index"))
            elif user.user_type == "3":
                if modulename in { "student_management_app.StudentViews","django.views.static"}:
                    pass
                elif modulename == "student_management_app.views":
                    pass
                else:
                    return HttpResponseRedirect(reverse("student_home"))
            else:
                return HttpResponseRedirect(reverse("show_login"))

        else:
            if request.path == reverse("show_login") or \
                request.path == reverse("do_login") or \
                    modulename == "django.contrib.auth.views" or \
                        modulename =="django.contrib.admin.sites" or \
                            modulename=="student_management_app.views":
                pass
            else:
                return HttpResponseRedirect(reverse("show_login"))
            