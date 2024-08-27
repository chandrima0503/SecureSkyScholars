"""Admin views module"""
import json

# import requests
# import boto3
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseForbidden
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from students_app.forms import AddStudentForm, EditStudentForm
from students_app.models import ModelAttendance, \
        ModelAttendanceReport, ModelCourses, \
        ModelFeedBackStaff, ModelLeaveReportStaff, \
        ModelSessionYear, ModelStaff, \
        ModelStudents,ModelSubjects, CustomisedUser, \
        ModelLeaveReportStudent, ModelFeedBackStudent

def index(request):
    """Index page view for admin"""
    student_count1 = ModelStudents.models_object.all().count()
    staff_count = ModelStaff.models_object.all().count()
    subject_count=ModelStudents.models_object.all().count()
    course_count = ModelCourses.models_object.all().count()

    course_all=ModelCourses.models_object.all()
    course_name_list=[]
    subject_count_list=[]
    student_count_list_in_course=[]
    for course in course_all:
        subjects_filter=ModelSubjects.models_object.filter(course_id=course.id).count()
        students_filter=ModelStudents.models_object.filter(course_id=course.id).count()
        course_name_list.append(course.course_name_char)
        subject_count_list.append(subjects_filter)
        student_count_list_in_course.append(students_filter)

    subjects_all=ModelSubjects.models_object.all()
    subject_list=[]
    student_count_list_in_subject=[]
    for subject in subjects_all:
        course=ModelCourses.models_object.get(id=subject.course_id.id)
        student_count=ModelStudents.models_object.filter(course_id=course.id).count()
        subject_list.append(subject.subject_name_char)
        student_count_list_in_subject.append(student_count)

    staffs=ModelStaff.models_object.all()
    attendance_present_list_staff=[]
    attendance_absent_list_staff=[]
    staff_name_list=[]
    for staff in staffs:
        subject_ids_filter=ModelSubjects.models_object.filter(staff_id=staff.admin.id)
        attendance_filter=ModelAttendance.models_object.filter(
            subject_id__in=subject_ids_filter).count()
        leaves_filter=ModelLeaveReportStaff.models_object.filter(
            staff_id=staff.id,leave_status_int=1).count()
        attendance_present_list_staff.append(attendance_filter)
        attendance_absent_list_staff.append(leaves_filter)
        staff_name_list.append(staff.admin.username)

    students_all=ModelStudents.models_object.all()
    attendance_present_list_student=[]
    attendance_absent_list_student=[]
    student_name_list=[]
    for student in students_all:
        attendance_filter=ModelAttendanceReport.models_object.filter(
            student_id=student.id,status_bool=True).count()
        absent_filter=ModelAttendanceReport.models_object.filter(
            student_id=student.id,status_bool=False).count()
        leaves_filter=ModelLeaveReportStudent.models_object.filter(
            student_id=student.id,leave_status_int=1).count()
        attendance_present_list_student.append(attendance_filter)
        attendance_absent_list_student.append(leaves_filter+absent_filter)
        student_name_list.append(student.admin.username)


    return render(request,"admin_pages/index.html",
                  {"student_count":student_count1,
                   "staff_count":staff_count,
                   "subject_count":subject_count,
                   "course_count":course_count,
                   "course_name_list":course_name_list,
                   "subject_count_list":subject_count_list,
                   "student_count_list_in_course":student_count_list_in_course,
                   "student_count_list_in_subject":student_count_list_in_subject,
                   "subject_list":subject_list,
                   "staff_name_list":staff_name_list,
                   "attendance_present_list_staff":attendance_present_list_staff,
                   "attendance_absent_list_staff":attendance_absent_list_staff,
                   "student_name_list":student_name_list,
                   "attendance_present_list_student":attendance_present_list_student,
                   "attendance_absent_list_student":attendance_absent_list_student})

def staff_entry(request):
    """View for staff entry page"""
    return render(request,"admin_pages/staff_entry.html")

def staff_entry_save(request):
    """View for staff entry save"""
    if request.method!="POST":
        return HttpResponse("Method Not Allowed")
    else:
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        username=request.POST.get("username")
        email=request.POST.get("email")
        password=request.POST.get("password")
        address_text=request.POST.get("address_text")
        try:
            user=CustomisedUser.objects.create_user(
                username=username,
                password=password,
                email=email,
                last_name=last_name,
                first_name=first_name,
                user_type=2)
            user.modelstaff.address_text=address_text
            user.save()
            messages.success(request,"Successfully Added Staff")
            return HttpResponseRedirect(reverse("staff_entry"))
        except KeyError:
            messages.error(request,"Failed to Add Staff")
            return HttpResponseRedirect(reverse("staff_entry"))

def course_entry(request):
    """View for course entry"""
    return render(request,"admin_pages/course_entry.html")

def course_entry_save(request):
    """View for course entry save"""
    if request.method!="POST":
        return HttpResponse("Method Not Allowed")
    else:
        course=request.POST.get("course")
        try:
            course_model=ModelCourses(course_name_char=course)
            course_model.save()
            messages.success(request,"Successfully Added Course")
            return HttpResponseRedirect(reverse("course_entry"))
        except KeyError:
            messages.error(request,"Failed To Add Course")
            return HttpResponseRedirect(reverse("course_entry"))

def student_entry(request):
    """View for student entry"""
    form=AddStudentForm()
    return render(request,"admin_pages/student_entry.html",{"form":form})

def student_entry_save(request):
    """View for student entry save"""
    if request.method!="POST":
        return HttpResponse("Method Not Allowed")
    else:
        form=AddStudentForm(request.POST,request.FILES)
        if form.is_valid():
            first_name=form.cleaned_data["first_name"]
            last_name=form.cleaned_data["last_name"]
            username=form.cleaned_data["username"]
            email=form.cleaned_data["email"]
            password=form.cleaned_data["password"]
            address_text=form.cleaned_data["address"]
            session_year_id=form.cleaned_data["session_year_id"]
            course_id=form.cleaned_data["course"]
            gender_val=form.cleaned_data["sex"]

            profile_pic=request.FILES['profile_pic']
            file_system_storage=FileSystemStorage()
            filename=file_system_storage.save(profile_pic.name,profile_pic)
            profile_pic_url=file_system_storage.url(filename)

            try:
                user=CustomisedUser.objects.create_user(
                    username=username,
                    password=password,
                    email=email,
                    last_name=last_name,
                    first_name=first_name,
                    user_type=3)
                user.modelstudents.address_text=address_text
                course_obj=ModelCourses.models_object.get(id=course_id)
                user.modelstudents.course_id=course_obj
                session_year_id=ModelSessionYear.models_object.get(id=session_year_id)
                user.modelstudents.session_year_id=session_year_id
                user.modelstudents.gender_val=gender_val
                user.modelstudents.profile_pic=profile_pic_url
                user.save()
                messages.success(request,"Successfully Added Student")
                return HttpResponseRedirect(reverse("student_entry"))
            except KeyError:
                messages.error(request,"Failed to Add Student")
                return HttpResponseRedirect(reverse("student_entry"))
        else:
            form=AddStudentForm(request.POST)
            return render(request, "admin_pages/student_entry.html", {"form": form})


def subject_entry(request):
    """View for subject entry"""
    courses_all=ModelCourses.models_object.all()
    staffs_filter=CustomisedUser.objects.filter(user_type=2)
    return render(request,"admin_pages/subject_entry.html",
                  {"ModelStaff":staffs_filter,"ModelCourses":courses_all})

def subject_entry_save(request):
    """View for subject entry save"""
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        subject_name_char=request.POST.get("subject_name_char")
        course_id=request.POST.get("course")
        course=ModelCourses.models_object.get(id=course_id)
        staff_id=request.POST.get("staff")
        staff=CustomisedUser.objects.get(id=staff_id)
        # p \
        #       "\ncourse:", course, "\nstaff:", staff )
        try:
            subject=ModelSubjects(
                subject_name_char=subject_name_char,
                course_id=course,
                staff_id=staff)
            subject.save()
            messages.success(request,"Successfully Added Subject")
            return HttpResponseRedirect(reverse("subject_entry"))
        except KeyError:
            messages.error(request,"Failed to Add Subject")
            return HttpResponseRedirect(reverse("subject_entry"))


def staff_manage(request):
    """View for staff manage"""
    staffs_all=ModelStaff.models_object.all()
    return render(request,"admin_pages/staff_manage.html",{"ModelStaff":staffs_all})

def student_manage(request):
    """View for student manage"""
    students_all=ModelStudents.models_object.all()
    return render(request,"admin_pages/student_manage.html",{"ModelStudents":students_all})

def course_manage(request):
    """View for course manage"""
    courses_all=ModelCourses.models_object.all()
    return render(request,"admin_pages/course_manage.html",{"ModelCourses":courses_all})

def subject_manage(request):
    """View for subject manage"""
    subjects_all=ModelSubjects.models_object.all()
    return render(request,"admin_pages/subject_manage.html",{"ModelSubjects":subjects_all})

def session_entry(request):
    """View for session entry"""
    return render(request,"admin_pages/session_entry.html")

def session_manage(request):
    """View for session manage"""
    session_all=ModelSessionYear.models_object.all().order_by('start_session_year')
    return render(request,"admin_pages/session_manage.html",{"ModelSession":session_all})

def session_add_save(request):
    """View for session add save"""
    if request.method!="POST":
        return HttpResponseRedirect(reverse("session_manage"))
    else:
        session_start_year=request.POST.get("session_start")
        session_end_year=request.POST.get("session_end")

        try:
            sessionyear=ModelSessionYear(
                start_session_year=session_start_year,
                end_session_year=session_end_year
            )
            sessionyear.save()
            messages.success(request, "Successfully Added Session")
            return HttpResponseRedirect(reverse("session_entry"))
        except KeyError:
            messages.error(request, "Failed to Add Session")
            return HttpResponseRedirect(reverse("session_entry"))


def session_delete(request, session_id):
    """View for session delete"""
    if request.method == 'POST':
        try:
            session = ModelSessionYear.models_object.get(id=session_id)
            session.delete()
        except ObjectDoesNotExist:
            pass
        return HttpResponseRedirect(reverse("session_manage"))
    # If the request method is not POST, return a 403 Forbidden response
    return HttpResponseForbidden("Forbidden")

def staff_edit(request,staff_id):
    """ module fetches the staff details and fills the edit form """
    get_staff=ModelStaff.models_object.get(admin=staff_id)
    return render(request,"admin_pages/staff_edit.html",{"staff":get_staff,"id":staff_id})

def staff_edit_save(request):
    """View for staff edit save"""
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    button_name = request.POST['button']
    staff_id=request.POST.get("staff_id")
    if button_name == 'submit':
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        email=request.POST.get("email")
        username=request.POST.get("username")
        address_text=request.POST.get("address_text")
        try:
            user=CustomisedUser.objects.get(id=staff_id)
            user.first_name=first_name
            user.last_name=last_name
            user.email = email
            user.username=username
            user.save()
            staff_model=ModelStaff.models_object.get(admin=staff_id)
            staff_model.address_text=address_text
            staff_model.save()
            messages.success(request,"Successfully Edited Staff")
            return HttpResponseRedirect(reverse("staff_edit",kwargs={"staff_id":staff_id}))
        except KeyError:
            messages.error(request,"Failed to Edit Staff")
            return HttpResponseRedirect(reverse("staff_edit",kwargs={"staff_id":staff_id}))
    else:
        try:
            get_staff = ModelStaff.models_object.get(admin=staff_id)
            get_staff.delete()
            CustomisedUser.objects.filter(id=staff_id).delete()
            messages.success(request, "Successfully Deleted Staff")
            return HttpResponseRedirect(reverse("staff_manage"))
        except IntegrityError:
            messages.error(request, "Staff cannot be deleted")
            return HttpResponseRedirect(reverse("staff_manage"))


def student_edit(request,student_id):
    """ module fetches the student details and fills the edit form"""
    request.session['student_id']=student_id
    get_student=ModelStudents.models_object.get(admin=student_id)
    student_form=EditStudentForm()
    student_form.fields['email'].initial=get_student.admin.email
    student_form.fields['first_name'].initial=get_student.admin.first_name
    student_form.fields['last_name'].initial=get_student.admin.last_name
    student_form.fields['username'].initial=get_student.admin.username
    student_form.fields['address'].initial=get_student.address_text
    student_form.fields['course'].initial=get_student.course_id.id
    student_form.fields['sex'].initial=get_student.gender_val
    student_form.fields['session_year'].initial=get_student.session_year_id.id
    return render(request,"admin_pages/student_edit.html",
                  {"form":student_form,"id":student_id,"username":get_student.admin.username})

def student_edit_save(request):
    """ module saves or deletes the edit student form responses to db """
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    button_name = request.POST['button']
    student_id=request.session.get("student_id")
    if student_id is None:
        return HttpResponseRedirect(reverse("student_manage"))
    if button_name == 'submit':
        form=EditStudentForm(request.POST,request.FILES)
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            address_text = form.cleaned_data["address"]
            session_year_id=form.cleaned_data["session_year"]
            course_id = form.cleaned_data["course"]
            sex = form.cleaned_data["sex"]
            if request.FILES.get('profile_pic',False):
                profile_pic=request.FILES['profile_pic']
                file_system_storage=FileSystemStorage()
                filename=file_system_storage.save(profile_pic.name,profile_pic)
                profile_pic_url=file_system_storage.url(filename)
            else:
                profile_pic_url=None
            try:
                user=CustomisedUser.objects.get(id=student_id)
                user.first_name=first_name
                user.last_name=last_name
                user.username=username
                user.email=email
                user.save()
                student=ModelStudents.models_object.get(admin=student_id)
                student.address_text=address_text
                session_year = ModelSessionYear.models_object.get(id=session_year_id)
                student.session_year_id = session_year
                student.gender_val=sex
                course=ModelCourses.models_object.get(id=course_id)
                student.course_id=course
                if profile_pic_url is not None:
                    student.profile_pic=profile_pic_url
                student.save()
                del request.session['student_id']
                messages.success(request,"Successfully Edited Student")
                return HttpResponseRedirect(
                    reverse("student_edit",kwargs={"student_id":student_id}))
            except KeyError:
                messages.error(
                    request,"Failed to Edit Student")
                return HttpResponseRedirect(
                    reverse("student_edit",kwargs={"student_id":student_id}))
        else:
            form=EditStudentForm(request.POST)
            student=ModelStudents.models_object.get(admin=student_id)
            return render(request,"admin_pages/student_edit.html",
                          {"id":student_id,"username":student.admin.username})
    else:
        try:
            student = ModelStudents.models_object.get(admin=student_id)
            student.delete()
            CustomisedUser.objects.filter(id=student_id).delete()
            messages.success(request, "Successfully Deleted Subject")
            return HttpResponseRedirect(reverse("student_manage"))
        except IntegrityError:
            messages.error(request, "Subject cannot be deleted")
            return HttpResponseRedirect(reverse("student_manage"))

def subject_edit(request,subject_id):
    """ module fetches the subject details and fills the edit form"""
    subject=ModelSubjects.models_object.get(id=subject_id)
    courses_all=ModelCourses.models_object.all()
    staffs_filter=CustomisedUser.objects.filter(user_type=2)
    return render(request,
                  "admin_pages/subject_edit.html",
                  {"subject":subject,"ModelStaff":staffs_filter,
                   "ModelCourses":courses_all,"id":subject_id})

def subject_edit_save(request):
    """ module makes changes to the subject details or deletes them completely """
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    button_name = request.POST['button']
    if button_name == 'submit':
        subject_id=request.POST.get("subject_id")
        subject_name_char=request.POST.get("subject_name_char")
        staff_id=request.POST.get("staff_id")
        course_id=request.POST.get("course_id")
        try:
            subject=ModelSubjects.models_object.get(id=subject_id)
            subject.subject_name_char=subject_name_char
            staff_id=CustomisedUser.objects.get(id=staff_id)
            subject.staff_id=staff_id
            course=ModelCourses.models_object.get(id=course_id)
            subject.course_id=course
            subject.save()
            messages.success(request,"Successfully Edited Subject")
            return HttpResponseRedirect(reverse("subject_edit",kwargs={"subject_id":subject_id}))
        except KeyError :
            messages.error(request,"Subject ID not found")
            return HttpResponseRedirect(reverse("subject_manage"))
    else:
        subject_id = request.POST.get("subject_id")
        try:
            subject = ModelSubjects.models_object.get(id=subject_id)
            subject.delete()
            messages.success(request, "Successfully Deleted Subject")
            return HttpResponseRedirect(reverse("subject_manage"))
        except IntegrityError:
            messages.error(request, "Subject cannot be deleted")
            return HttpResponseRedirect(reverse("subject_manage"))

def course_edit(request,course_id):
    """ module fetches the course details and fills the edit form"""
    course=ModelCourses.models_object.get(id=course_id)
    return render(request,"admin_pages/course_edit.html",{"course":course,"id":course_id})

def course_edit_save(request):
    """ module makes changes to the course details or deletes them completely """
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    course_id=request.POST.get("course_id")
    course_name=request.POST.get("course")
    button_name = request.POST['button']
    course=ModelCourses.models_object.get(id=course_id)
    course.course_name_char=course_name
    if button_name=="submit":
        try:
            course.save()
            messages.success(request,"Successfully Edited Course")
            return HttpResponseRedirect(reverse("course_manage",kwargs={"course_id":course_id}))
        except KeyError:
            messages.error(request,"Failed to Edit Course")
            return HttpResponseRedirect(reverse("course_edit",kwargs={"course_id":course_id}))
    else:
        try:
            course.delete()
            messages.success(request,'Course Successfully Deleted')
            return HttpResponseRedirect(reverse('course_manage'))
        except IntegrityError:
            messages.error(request, "Course cannot be deleted")
            return HttpResponseRedirect(reverse("course_edit"))



@csrf_exempt
def email_is_exist(request):
    """View for checking if email exist"""
    email=request.POST.get("email")
    user_obj=CustomisedUser.objects.filter(email=email).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)

@csrf_exempt
def username_is_exist(request):
    """View for checking if username exist"""
    username=request.POST.get("username")
    user_obj=CustomisedUser.objects.filter(username=username).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)

def feedback_staff_admin(request):
    """View for checking staff feedback"""
    feedbacks=ModelFeedBackStaff.models_object.all()
    return render(request,"admin_pages/feedback_staff.html",{"feedbacks":feedbacks})

def feedback_student_admin(request):
    """View for checking student feedback"""
    feedbacks=ModelFeedBackStudent.models_object.all()
    return render(request,"admin_pages/feedback_student.html",{"feedbacks":feedbacks})

@csrf_exempt
def feedback_student_reply(request):
    """View for replying student feedback"""
    feedback_id=request.POST.get("id")
    feedback_message=request.POST.get("message")

    try:
        feedback=ModelFeedBackStudent.models_object.get(id=feedback_id)
        feedback.feedback_reply=feedback_message
        feedback.save()
        return HttpResponse("True")
    except KeyError:
        return HttpResponse("False")

@csrf_exempt
def feedback_staff_reply(request):
    """View for replying staff feedback"""
    feedback_id=request.POST.get("id")
    feedback_message=request.POST.get("message")

    try:
        feedback=ModelFeedBackStaff.models_object.get(id=feedback_id)
        feedback.feedback_reply=feedback_message
        feedback.save()
        return HttpResponse("True")
    except KeyError:
        return HttpResponse("False")

def view_leave_staff(request):
    """View for checking staff leave"""
    leaves=ModelLeaveReportStaff.models_object.all()
    return render(request,"admin_pages/view_leave_staff.html",{"leaves":leaves})

def view_leave_student(request):
    """View for checking student leave"""
    leaves=ModelLeaveReportStudent.models_object.all()
    return render(request,"admin_pages/view_leave_student.html",{"leaves":leaves})

def student_leave_approve(request,leave_id):
    """View for doing student leave approval"""
    print(request)
    leave=ModelLeaveReportStudent.models_object.get(id=leave_id)
    leave.leave_status_int=1
    leave.save()
    return HttpResponseRedirect(reverse("view_leave_student"))

def student_leave_disapprove(request,leave_id):
    """View for doing student leave disapproval"""
    print(request)
    leave=ModelLeaveReportStudent.models_object.get(id=leave_id)
    leave.leave_status_int=2
    leave.save()
    return HttpResponseRedirect(reverse("view_leave_student"))


def staff_leave_approve(request,leave_id):
    """View for doing staff leave approval"""
    print(request)
    leave=ModelLeaveReportStaff.models_object.get(id=leave_id)
    leave.leave_status_int=1
    leave.save()
    return HttpResponseRedirect(reverse("view_leave_staff"))

def staff_leave_disapprove(request,leave_id):
    """View for doing staff leave disapproval"""
    print(request)
    leave=ModelLeaveReportStaff.models_object.get(id=leave_id)
    leave.leave_status_int=2
    leave.save()
    return HttpResponseRedirect(reverse("view_leave_staff"))

def attendance_display_admin(request):
    """"View for attendance display"""
    subjects_all=ModelSubjects.models_object.all()
    session_year_id=ModelSessionYear.models_object.all()
    return render(request,"admin_pages/attendance_display_admin.html",
                  {"ModelSubjects":subjects_all,"session_year_id":session_year_id})

@csrf_exempt
def get_dates_attendance(request):
    """View for getting attendance dates"""
    subject=request.POST.get("subject")
    session_year_id=request.POST.get("session_year_id")
    subject_obj=ModelSubjects.models_object.get(id=subject)
    session_year_obj=ModelSessionYear.models_object.get(id=session_year_id)
    attendance_filter=ModelAttendance.models_object.filter(
        subject_id=subject_obj,session_year_id=session_year_obj)
    attendance_obj=[]
    for attendance_single in attendance_filter:
        data={"id":attendance_single.id,"attendance_date":str(attendance_single.attendance_date),
              "session_year_id":attendance_single.session_year_id.id}
        attendance_obj.append(data)

    return JsonResponse(json.dumps(attendance_obj),safe=False)


@csrf_exempt
def get_student_attendance(request):
    """View for getting student attendance"""
    get_attendance_date=request.POST.get("attendance_date")
    attendance=ModelAttendance.models_object.get(id=get_attendance_date)

    attendance_data=ModelAttendanceReport.models_object.filter(attendance_id=attendance)
    list_data=[]

    for student in attendance_data:
        data_small={"id":student.student_id.admin.id,
                    "name":student.student_id.admin.first_name+
                    " "+student.student_id.admin.last_name,
                    "status":student.status}
        list_data.append(data_small)
    return JsonResponse(json.dumps(list_data),content_type="application/json",safe=False)

def profile_admin(request):
    """view for profile admin"""
    user=CustomisedUser.objects.get(id=request.user.id)
    return render(request,"admin_pages/profile_admin.html",{"user":user})

def profile_admin_save(request):
    """view for save profile admin"""
    if request.method!="POST":
        return HttpResponseRedirect(reverse("profile_admin"))
    get_first_name=request.POST.get("first_name")
    get_last_name=request.POST.get("last_name")
    # password=request.POST.get("password")
    try:
        get_user=CustomisedUser.objects.get(id=request.user.id)
        get_user.first_name=get_first_name
        get_user.last_name=get_last_name
        get_user.save()
        messages.success(request, "Successfully Updated Profile.")
        return HttpResponseRedirect(reverse("profile_admin"))
    except KeyError:
        messages.error(request, "Failed to Update Profile.")
        return HttpResponseRedirect(reverse("profile_admin"))

def notification_send_student_admin(request):
    """Sends a push notification to a student member from admin"""
    students_all=ModelStudents.models_object.all()
    return render(request,"admin_pages/notification_send_student_admin.html",
                  {"ModelStudents":students_all})

def notification_send_staff_admin(request):
    """Sends a push notification to a staff member from admin"""
    staffs_all=ModelStaff.models_object.all()
    return render(request,"admin_pages/notification_send_staff_admin.html",
                  {"ModelStaff":staffs_all})

@csrf_exempt
def send_notification_student(request):
    """Sends a push notification to a student member."""
    # _id_=request.POST.get("id")
    # message=request.POST.get("message")
    # student=ModelStudents.models_object.get(admin=_id_)
    # token=student.token_fcm
    # url="https://fcm.googleapis.com/fcm/send"
    # body={
    #     "notification":{
    #     "title":"Student Management System",
    #     "body":message,
    #     "click_action": "https://studentmanagementsystem22.herokuapp.com/notifications",
    #     "icon": "http://studentmanagementsystem22.herokuapp.com/static/dist/img/user2-160x160.jpg"
    #     },
    #     "to":token
    # }
    # headers={"Content-Type":"application/json","Authorization":"key=SERVER_KEY_HERE"}
    # data=requests.post(url,data=json.dumps(body),headers=headers, timeout= 20)
    # notification=ModelNotificationStudent(student_id=student,message=message)
    # notification.save()
    # print(data.text)
    # return HttpResponse("True")
    pass

@csrf_exempt
def send_notification_staff(request):
    """Sends a push notification to a staff member."""

    # _id_ = request.POST.get("id")
    # message = request.POST.get("message")

    # staff = ModelStaff.models_object.get(admin=_id_)
    # token = staff.token_fcm

    # sns = boto3.client("sns")

    # topic_arn = "arn:aws:sns:us-east-1:762473049171:SecureSkyScholars:0f553184-cc43-49ae-a0e3-4064d29e93f4"
    # message = {
    #     "default": {
    #         "body": message,
    #         "title": "Student Management System"
    #     }
    # }

    # message_attributes = {
    #     "Token": {
    #         "DataType": "String"
    #     }
    # }

    # response = sns.publish(
    #     TopicArn=topic_arn,
    #     Message=json.dumps(message),
    #     MessageAttributes=message_attributes
    # )

    # if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
    #     return HttpResponse("Push notification sent successfully")
    # else:
    #     return HttpResponse(f"Error sending push notification: {response['ResponseMetadata']['HTTPStatusCode']}")
    pass
