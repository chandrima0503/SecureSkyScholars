"""Module for Student Views"""
import datetime

from django.contrib import messages
from django.urls import reverse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect
from students_app.models import ModelStudents, ModelCourses, ModelSubjects, \
    CustomisedUser, ModelAttendance, ModelAttendanceReport, \
    ModelLeaveReportStudent, ModelFeedBackStudent, \
    ModelNotificationStudent, ModelStudentResult, \
    ModelOnlineClassRoom, ModelSessionYear


def student_index(request):
    """"Index page view for student"""
    obj_student=ModelStudents.models_object.get(admin=request.user.id)
    total_attendance=ModelAttendanceReport.models_object.filter(student_id=obj_student).count()
    present_attendance=ModelAttendanceReport.models_object.filter(
        student_id=obj_student,status_bool=True).count()
    absent_attendance=ModelAttendanceReport.models_object.filter(
        student_id=obj_student,status_bool=False).count()
    get_course=ModelCourses.models_object.get(id=obj_student.course_id.id)
    get_subjects=ModelSubjects.models_object.filter(course_id=get_course).count()
    get_subjects_data=ModelSubjects.models_object.filter(course_id=get_course)
    get_session_obj=ModelSessionYear.models_object.get(id=obj_student.session_year_id.id)
    get_class_room=ModelOnlineClassRoom.models_object.filter(
        subject__in=get_subjects_data,is_active_bool=True,session_years=get_session_obj)

    subject_name_list=[]
    data_present_list=[]
    data_absent_list=[]
    get_subject_data=ModelSubjects.models_object.filter(course_id=obj_student.course_id)
    for subject_item in get_subject_data:
        get_attendance=ModelAttendance.models_object.filter(subject_id=subject_item.id)
        present_count_attendance=ModelAttendanceReport.models_object.filter(
            attendance_id__in=get_attendance,status=True,student_id=obj_student.id).count()
        absent_count_attendance=ModelAttendanceReport.models_object.filter(
            attendance_id__in=get_attendance,status=False,student_id=obj_student.id).count()
        subject_name_list.append(subject_item.subject_name_list)
        data_present_list.append(present_count_attendance)
        data_absent_list.append(absent_count_attendance)

    return render(request,"student_pages/student_index.html",
                  {"total_attendance":total_attendance,
                   "absent_attendance":absent_attendance,
                   "present_attendance":present_attendance,
                   "get_ModelSubjects":get_subjects,
                   "data_name":subject_name_list,
                   "data1":data_present_list,
                   "data2":data_absent_list,
                   "get_class_room":get_class_room})

def class_room_join(request,subject_id,session_year_id):
    """View to join classroom"""
    session_year_obj=ModelSessionYear.models_object.get(id=session_year_id)
    get_subjects=ModelSubjects.models_object.filter(id=subject_id)
    if get_subjects.exists():
        session_filter=ModelSessionYear.models_object.filter(id=session_year_obj.id)
        if session_filter.exists():
            get_subject_obj=ModelSubjects.models_object.get(id=subject_id)
            get_course=ModelCourses.models_object.get(id=get_subject_obj.course_id.id)
            check_course_filter=ModelStudents.models_object.filter(
                admin=request.user.id,course_id=get_course.id)
            if check_course_filter.exists():
                session_check_filter=ModelStudents.models_object.filter(
                    admin=request.user.id,session_year_id=session_year_obj.id)
                if session_check_filter.exists():
                    onlineclass=ModelOnlineClassRoom.models_object.get(
                        session_years=session_year_id,subject_item=subject_id)
                    return render(request,"student_pages/class_room_join.html",
                                  {"username":request.user.username,
                                   "password":onlineclass.room_pwd,
                                   "roomid":onlineclass.room_name})

                return HttpResponse("This Online Session is Not For You.")
            return HttpResponse("This Subject is Not For You.")
        return HttpResponse("Session Year Not Found.")
    return HttpResponse("Subject Not Found.")


def view_attendance_student(request):
    """View for student attendance"""
    get_student=ModelStudents.models_object.get(admin=request.user.id)
    get_course=get_student.course_id
    get_subjects=ModelSubjects.models_object.filter(course_id=get_course)
    return render(request,"student_pages/view_attendance_student.html",
                  {"get_ModelSubjects":get_subjects})

def view_attendance_student_post(request):
    """view for posting student attendance"""
    get_subject_id=request.POST.get("subject_item")
    get_start_date=request.POST.get("start_date")
    get_end_date=request.POST.get("end_date")

    parse_start_data=datetime.datetime.strptime(get_start_date,"%Y-%m-%d").date()
    parse_end_data=datetime.datetime.strptime(get_end_date,"%Y-%m-%d").date()
    get_subject_obj=ModelSubjects.models_object.get(id=get_subject_id)
    get_user_object=CustomisedUser.objects.get(id=request.user.id)
    get_stud_obj=ModelStudents.models_object.get(admin=get_user_object)

    get_attendance=ModelAttendance.models_object.filter(
        attendance_date__range=(parse_start_data,parse_end_data),subject_id=get_subject_obj)
    attendance_reports=ModelAttendanceReport.models_object.filter(
        attendance_id__in=get_attendance,student_id=get_stud_obj)
    return render(request,"student_pages/attendance_data_student.html",
                  {"attendance_reports":attendance_reports})

def apply_leave_student(request):
    """view for student to apply leave"""
    staff_obj = ModelStudents.models_object.get(admin=request.user.id)
    leave_data_filter=ModelLeaveReportStudent.models_object.filter(student_id=staff_obj)
    return render(request,"student_pages/apply_leave_student.html",{"leave_data":leave_data_filter})

def apply_leave_student_save(request):
    """Save the data of applied leave by student."""
    if request.method!="POST":
        return HttpResponseRedirect(reverse("apply_leave_student"))
    get_leave_date=request.POST.get("leave_date")
    get_leave_msg=request.POST.get("leave_msg")
    obj_student=ModelStudents.models_object.get(admin=request.user.id)
    try:
        leave_report_student=ModelLeaveReportStudent(
            student_id=obj_student,
            leave_date=get_leave_date,
            leave_message=get_leave_msg,
            leave_status_int=0)
        leave_report_student.save()
        messages.success(request, "Successfully Applied for Leave.")
        return HttpResponseRedirect(reverse("apply_leave_student"))
    except KeyError:
        messages.error(request, "Failed To Apply for Leave.")
        return HttpResponseRedirect(reverse("apply_leave_student"))


def feedback_student(request):
    """View for Student Feedback Page."""
    staff_id=ModelStudents.models_object.get(admin=request.user.id)
    filter_feedback_data=ModelFeedBackStudent.models_object.filter(student_id=staff_id)
    return render(request,"student_pages/feedback_student.html",
                  {"feedback_data":filter_feedback_data})

def feedback_student_save(request):
    """Saves the feedback from students and saves it in database."""
    if request.method is not "POST":
        return HttpResponseRedirect(reverse("feedback_student"))
    get_feedback_msg=request.POST.get("feedback_msg")
    obj_student=ModelStudents.models_object.get(admin=request.user.id)
    try:
        feedback=ModelFeedBackStudent(
            student_id=obj_student,
            feedback=get_feedback_msg,
            feedback_reply="")
        feedback.save()
        messages.success(request, "Successfully Sent Feedback.")
        return HttpResponseRedirect(reverse("feedback_student"))
    except KeyError:
        messages.error(request, "Failed To Send Feedback.")
        return HttpResponseRedirect(reverse("feedback_student"))
def profile_student(request):
    """Profile page view function to show details about a particular user"""
    get_user=CustomisedUser.objects.get(id=request.user.id)
    get_student=ModelStudents.models_object.get(admin=get_user)
    return render(request,"student_pages/profile_student.html",
                  {"get_user":get_user,"get_student":get_student})

def profile_student_save(request):
    """Save changes made by admin on their own profile."""
    if request.method!="POST":
        return HttpResponseRedirect(reverse("profile_student"))
    get_first_name=request.POST.get("first_name")
    get_last_name=request.POST.get("last_name")
    get_password=request.POST.get("password")
    get_address=request.POST.get("address")
    try:
        get_user=CustomisedUser.objects.get(id=request.user.id)
        get_user.first_name=get_first_name
        get_user.last_name=get_last_name
        if get_password is not None and get_password!="":
            get_user.set_password(get_password)
        get_user.save()
        get_student=ModelStudents.models_object.get(admin=get_user)
        get_student.address=get_address
        get_student.save()
        messages.success(request, "Successfully Updated Profile.")
        return HttpResponseRedirect(reverse("profile_student"))
    except KeyError:
        messages.error(request, "Failed to Update Profile.")
        return HttpResponseRedirect(reverse("profile_student"))
@csrf_exempt
def student_save_fcmtoken(request):
    """This method will save fcm token of loggedin user for push notifications."""
    get_token=request.POST.get("token")
    try:
        get_student=ModelStudents.models_object.get(admin=request.user.id)
        get_student.token_fcm=get_token
        get_student.save()
        return HttpResponse("True.")
    except KeyError:
        return HttpResponse("False.")

def notifications(request):
    """Notifications page view function which shows all the notifications sent from teacher or students."""
    get_student=ModelStudents.models_object.get(admin=request.user.id)
    get_notifications=ModelNotificationStudent.models_object.filter(student_id=get_student.id)
    return render(request,"student_pages/notifications.html",{"notifications":get_notifications})

def result_student(request):
    """Result page view function that displays results of a particular subject."""
    get_student=ModelStudents.models_object.get(admin=request.user.id)
    get_student_result=ModelStudentResult.models_object.filter(student_id=get_student.id)
    return render(request,"student_pages/result_student.html",
                  {"ModelStudentResult":get_student_result})
