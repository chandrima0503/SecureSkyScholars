"""ewkjfbnwejk,nfjwelm,sa"""
import json
import requests

from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth import login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.core.management import call_command
from django.conf import settings

from students_app.backend_email import BackendEmail
from students_app.models import CustomisedUser, ModelCourses, ModelSessionYear
# from student_management_system import settings


def run_migrations(request):
    call_command('runmigrations')
    return HttpResponse('Migrations have been run.')

def show_demo_page(request):
    """View to show demo page"""
    return render(request,"demo.html")

def show_login_page(request):
    """View to show login page"""
    return render(request,"login.html")

def do_login(request):
    """View to do login"""
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    token_captcha=request.POST.get("g-recaptcha-response")
    url_cap="https://www.google.com/recaptcha/api/siteverify"
    secret_cap=settings.RECAPTCHA_PUBLIC_KEY
    cap_data={"secret":secret_cap,"response":token_captcha}
    server_cap_response=requests.post(url=url_cap,data=cap_data, timeout= 20)
    json_cap=json.loads(server_cap_response.text)
    if json_cap['success'] is False:
        messages.error(request,"Invalid Captcha! Try Again")
        return HttpResponseRedirect("/")
    user_backend_email=BackendEmail.authenticate_email(
        request,
        username=request.POST.get("email"),password=request.POST.get("password"))
    if user_backend_email is not None:
        login(request,user_backend_email)
        if user_backend_email.user_type=="1":
            return HttpResponseRedirect('/index')
        if user_backend_email.user_type=="2":
            return HttpResponseRedirect(reverse("staff_index"))
        return HttpResponseRedirect(reverse("student_index"))
    messages.error(request,"Invalid Login Details. ")
    return HttpResponseRedirect("/")

def get_user_details(request):
    """view to get user details"""
    if request.user is not None:
        return HttpResponse( "usertype : "+str(request.user.user_type) +
                            "User : "+request.user.email)
    return HttpResponse("Please Login First! ")

def user_logout(request):
    """view for user logout"""
    logout(request)
    return HttpResponseRedirect("/")

def show_firebase_js(request):
    """View to do firebase notification send"""
    print(request)
    data = ''
    # data='importScripts("https://www.gstatic.com/firebasejs/7.14.6/firebase-app.js");' \
    #      'importScripts("https://www.gstatic.com/firebasejs/7.14.6/firebase-messaging.js"); ' \
    #      'var firebaseConfig = {' \
    #      '        apiKey: "YOUR_API_KEY",' \
    #      '        authDomain: "FIREBASE_AUTH_URL",' \
    #      '        databaseURL: "FIREBASE_DATABASE_URL",' \
    #      '        projectId: "FIREBASE_PROJECT_ID",' \
    #      '        storageBucket: "FIREBASE_STORAGE_BUCKET_URL",' \
    #      '        messagingSenderId: "FIREBASE_SENDER_ID",' \
    #      '        appId: "FIREBASE_APP_ID",' \
    #      '        measurementId: "FIREBASE_MEASUREMENT_ID"' \
    #      ' };' \
    #      'firebase.initializeApp(firebaseConfig);' \
    #      'const messaging=firebase.messaging();' \
    #      'messaging.setBackgroundMessageHandler(function (payload) {' \
    #      '    console.log(payload);' \
    #      '    const notification=JSON.parse(payload);' \
    #      '    const notificationOption={' \
    #      '        body:notification.body,' \
    #      '        icon:notification.icon' \
    #      '    };' \
    #      '    return self.registration.showNotification(payload.notification.title,' \
    #      ' notificationOption);' \
    #      '});'

    return HttpResponse(data,content_type="text/javascript")

def test_url(request):
    """view for testing url"""
    print(request)
    return HttpResponse("Ok.")

def admin_signup(request):
    """View for admin signup"""
    return render(request,"admin_signup.html")

def student_signup(request):
    """View for student signup"""
    get_courses=ModelCourses.models_object.all()
    get_session_years=ModelSessionYear.models_object.all()
    return render(request,"student_signup.html",
                  {"ModelCourses":get_courses,"session_years":get_session_years})

def staff_signup(request):
    """View for staff signup"""
    return render(request,"staff_signup.html")

def admin_signup_complete(request):
    """View for admin signup complete"""
    get_username=request.POST.get("username")
    get_email=request.POST.get("email")
    get_password=request.POST.get("password")

    try:
        get_user=CustomisedUser.objects.create_user(
            username=get_username,
            password=get_password,
            email=get_email,
            user_type=1)
        get_user.save()
        messages.success(request,"Successfully Created Admin.")
        return HttpResponseRedirect(reverse("show_login"))
    except KeyError:
        messages.error(request,"Failed to Create Admin.")
        return HttpResponseRedirect(reverse("show_login"))

def staff_signup_complete(request):
    """View for staff signup complete"""
    get_username=request.POST.get("username")
    get_email=request.POST.get("email")
    get_password=request.POST.get("password")
    get_address=request.POST.get("address_text")

    try:
        get_user=CustomisedUser.objects.create_user(
            username=get_username,
            password=get_password,
            email=get_email,user_type=2)
        get_user.modelstaff.address=get_address
        get_user.save()
        messages.success(request,"Successfully Created Staff.")
        return HttpResponseRedirect(reverse("show_login"))
    except KeyError:
        messages.error(request,"Failed to Create Staff.")
        return HttpResponseRedirect(reverse("show_login"))

def signup_student_complete(request):
    """View for student signup complete"""
    print(request)
    get_first_name = request.POST.get("first_name")
    get_last_name = request.POST.get("last_name")
    get_username = request.POST.get("username")
    get_email = request.POST.get("email")
    get_password = request.POST.get("password")
    get_address = request.POST.get("address_text")
    get_session_year_id = request.POST.get("session_year")
    get_course_id = request.POST.get("course")
    get_sex = request.POST.get("sex")

    get_profile_pic = request.FILES['profile_pic']
    get_file_system_storage = FileSystemStorage()
    get_filename = get_file_system_storage.save(get_profile_pic.name, get_profile_pic)
    get_profile_pic_url = get_file_system_storage.url(get_filename)

    #try:
    get_user = CustomisedUser.objects.create_user(
        username=get_username,
        password=get_password,
        email=get_email,
        last_name=get_last_name,
        first_name=get_first_name, user_type=3)
    get_user.modelstudents.address_text = get_address
    course_obj = ModelCourses.models_object.get(id=get_course_id)
    get_user.modelstudents.course = course_obj
    session_year = ModelSessionYear.models_object.get(id=get_session_year_id)
    get_user.modelstudents.session_year = session_year
    get_user.modelstudents.gender = get_sex
    get_user.modelstudents.profile_pic = get_profile_pic_url
    get_user.save()
    messages.success(request, "Successfully Added Student")
    return HttpResponseRedirect(reverse("show_login"))
    #except:
     #   messages.error(request, "Failed to Add Student")
      #  return HttpResponseRedirect(reverse("show_login"))
      