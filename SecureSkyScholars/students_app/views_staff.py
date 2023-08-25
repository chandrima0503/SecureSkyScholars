"""Module for Staff Views"""
from uuid import uuid4
import json
from datetime import datetime
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.contrib import messages
from django.urls import reverse


from students_app.models import ModelAttendance, \
        ModelAttendanceReport, ModelCourses, \
        ModelFeedBackStaff, ModelLeaveReportStaff, \
        ModelNotificationStaff, ModelOnlineClassRoom, \
        ModelSessionYear, ModelStaff, ModelStudentResult, \
        ModelStudents,ModelSubjects, CustomisedUser

def staff_index(request):
    """Index page view for Staff"""
    subjects_filter=ModelSubjects.models_object.filter(staff_id=request.user.id)
    course_id_array=[]
    for subject in subjects_filter:
        get_course=ModelCourses.models_object.get(id=subject.course_id.id)
        course_id_array.append(get_course.id)

    final_course_array=[]
    for course_id in course_id_array:
        if course_id not in final_course_array:
            final_course_array.append(course_id)

    students_count_filter=ModelStudents.models_object.filter(
        course_id__in=final_course_array).count()
    attendance_count_filter=ModelAttendance.models_object.filter(
        subject_id__in=subjects_filter).count()
    get_staff=ModelStaff.models_object.get(admin=request.user.id)
    leave_count_filter=ModelLeaveReportStaff.models_object.filter(
        staff_id=get_staff.id,leave_status_int=1).count()
    subjects_count=subjects_filter.count()
    subject_array=[]
    attendance_array=[]
    for subject in subjects_filter:
        attendance_count1_filter=ModelAttendance.models_object.filter(subject_id=subject.id).count()
        subject_array.append(subject.subject_name_char)
        attendance_array.append(attendance_count1_filter)

    students_attendance_filter=ModelStudents.models_object.filter(course_id__in=final_course_array)
    student_array=[]
    student_array_attendance_present=[]
    student_array_attendance_absent=[]
    for student in students_attendance_filter:
        attendance_present_count_filter=ModelAttendanceReport.models_object.filter(
            status=True,student_id=student.id).count()
        attendance_absent_count_filter=ModelAttendanceReport.models_object.filter(
            status=False,student_id=student.id).count()
        student_array.append(student.admin.username)
        student_array_attendance_present.append(attendance_present_count_filter)
        student_array_attendance_absent.append(attendance_absent_count_filter)

    return render(request,"staff_pages/staff_index.html",
                  {"students_count":students_count_filter,
                   "attendance_count":attendance_count_filter,
                   "leave_count":leave_count_filter,
                   "subject_count":subjects_count,
                   "subject_array":subject_array,
                   "attendance_list":attendance_array,
                   "student_list":student_array,
                   "present_list":student_array_attendance_present,
                   "absent_list":student_array_attendance_absent})

def take_attendance_staff(request):
    """view to take staff attendance"""
    subjects_filter=ModelSubjects.models_object.filter(staff_id=request.user.id)
    session_years_all=ModelSessionYear.models_object.all()
    return render(request,"staff_pages/take_attendance_staff.html",
                  {"subjects":subjects_filter,"session_years":session_years_all})

@csrf_exempt
def students_fetch(request):
    """View to fetch students"""
    get_subject_id=request.POST.get("subject")
    get_session_year=request.POST.get("session_year")

    get_subject=ModelSubjects.models_object.get(id=get_subject_id)
    get_session_model=ModelSessionYear.models_object.get(id=get_session_year)
    students_filter=ModelStudents.models_object.filter(
        course_id=get_subject.course_id,session_year_id=get_session_model)
    list_data=[]

    for student in students_filter:
        data_small={"id":student.admin.id,
                    "name":student.admin.first_name+" "+student.admin.last_name}
        list_data.append(data_small)
    return JsonResponse(json.dumps(list_data),content_type="application/json",safe=False)

@csrf_exempt
def attendance_save_data(request):
    """view to save attendance data"""
    get_student_ids=request.POST.get("student_ids")
    get_subject_id=request.POST.get("subject_id")
    get_attendance_date=request.POST.get("attendance_date")
    get_session_year_id=request.POST.get("session_year_id")

    get_subject_model=ModelSubjects.models_object.get(id=get_subject_id)
    get_session_model=ModelSessionYear.models_object.get(id=get_session_year_id)
    json_student=json.loads(get_student_ids)
    try:
        attendance=ModelAttendance(
            subject_id=get_subject_model,
            attendance_date=get_attendance_date,
            session_year_id=get_session_model)
        attendance.save()

        for stud in json_student:
            get_student=ModelStudents.models_object.get(admin=stud['id'])
            attendance_report=ModelAttendanceReport(
                student_id=get_student,attendance_id=attendance,status=stud['status'])
            attendance_report.save()
        return HttpResponse("OK")
    except KeyError:
        return HttpResponse("ERR")

def update_attendance_staff(request):
    """view to update staff attendance"""
    subjects_filter=ModelSubjects.models_object.filter(staff_id=request.user.id)
    session_year_id_all=ModelSessionYear.models_object.all()
    return render(request,"staff_pages/update_attendance_staff.html",
                  {"subjects":subjects_filter,"session_year_id":session_year_id_all})

@csrf_exempt
def attendance_get_dates(request):
    """view to get attendance dates"""
    get_subject=request.POST.get("subject")
    get_session_year_id=request.POST.get("session_year_id")
    get_subject_obj=ModelSubjects.models_object.get(id=get_subject)
    get_session_year_obj=ModelSessionYear.models_object.get(id=get_session_year_id)
    attendance_filter=ModelAttendance.models_object.filter(
        subject_id=get_subject_obj,session_year_id=get_session_year_obj)
    attendance_obj=[]
    for attendance_single in attendance_filter:
        data={"id":attendance_single.id,
              "attendance_date":str(attendance_single.attendance_date),
              "session_year_id":attendance_single.session_year_id.id}
        attendance_obj.append(data)

    return JsonResponse(json.dumps(attendance_obj),safe=False)

@csrf_exempt
def attendance_get_student(request):
    """view to get student attendance"""
    get_attendance_date=request.POST.get("attendance_date")
    get_attendance=ModelAttendance.models_object.get(id=get_attendance_date)

    attendance_data_filter=ModelAttendanceReport.models_object.filter(attendance_id=get_attendance)
    array_data=[]

    for student in attendance_data_filter:
        data_small_create={"id":student.student_id.admin.id,
                    "name":student.student_id.admin.first_name+
                    " "+student.student_id.admin.last_name,
                    "status":student.status}
        array_data.append(data_small_create)
    return JsonResponse(json.dumps(array_data),content_type="application/json",safe=False)

@csrf_exempt
def updateattendance_save_data(request):
    """view to save updated attendance"""
    get_student_ids=request.POST.get("student_ids")
    get_attendance_date=request.POST.get("attendance_date")
    get_attendance=ModelAttendance.models_object.get(id=get_attendance_date)

    json_sstudent=json.loads(get_student_ids)


    try:
        for stud in json_sstudent:
            get_student=ModelStudents.models_object.get(admin=stud['id'])
            get_attendance_report=ModelAttendanceReport.models_object.get(
                student_id=get_student,attendance_id=get_attendance)
            get_attendance_report.status=stud['status']
            get_attendance_report.save()
        return HttpResponse("OK")
    except KeyError:
        return HttpResponse("ERR")

def apply_leave_staff(request):
    """view to show staff leave application form and process it."""
    get_staff_obj = ModelStaff.models_object.get(admin=request.user.id)
    leave_data_filter= ModelLeaveReportStaff.models_object.filter(staff_id=get_staff_obj)
    return render(request,"staff_pages/apply_leave_staff.html",{"leave_data":leave_data_filter})

def apply_leave_staff_save(request):
    """view to save staff leave application details from the user side ."""
    if request.method!="POST":
        return HttpResponseRedirect(reverse("apply_leave_staff"))
    get_leave_date=request.POST.get("leave_date")
    get_leave_msg=request.POST.get("leave_msg")
    get_staff_obj= ModelStaff.models_object.get(admin=request.user.id)
    try:
        leave_report_create= ModelLeaveReportStaff(
            staff_id=get_staff_obj,
            leave_date=get_leave_date,
            leave_message=get_leave_msg,
            leave_status_int=0)
        leave_report_create.save()
        messages.success(request, "Successfully Applied for Leave.")
        return HttpResponseRedirect(reverse("apply_leave_staff"))
    except KeyError:
        messages.error(request, "Failed To Apply for Leave")
        return HttpResponseRedirect(reverse("apply_leave_staff"))


def feedback_staff(request):
    """view to show staff feedback page with all previous feedback data of that particular staff member."""
    get_staff_id=ModelStaff.models_object.get(admin=request.user.id)
    feedback_data_filter=ModelFeedBackStaff.models_object.filter(staff_id=get_staff_id)
    return render(request,"staff_pages/feedback_staff.html",
                  {"feedback_data":feedback_data_filter})

def feedback_staff_save(request):
    """view to save staff feedback details by the userside."""
    if request.method!="POST":
        return HttpResponseRedirect(reverse("feedback_staff_save"))
    else:
        get_feedback_msg=request.POST.get("feedback_msg")

        get_staff_obj=ModelStaff.models_object.get(admin=request.user.id)
        try:
            feedback=ModelFeedBackStaff(
                staff_id=get_staff_obj,
                feedback=get_feedback_msg,
                feedback_reply="")
            feedback.save()
            messages.success(request, "Successfully Sent Feedback")
            return HttpResponseRedirect(reverse("feedback_staff"))
        except KeyError:
            messages.error(request, "Failed To Send Feedback")
            return HttpResponseRedirect(reverse("feedback_staff"))

def profile_staff(request):
    """view to show staff profile page which contains his personal information and contact info."""
    get_user=CustomisedUser.objects.get(id=request.user.id)
    get_staff=ModelStaff.models_object.get(admin=get_user)
    return render(request,"staff_pages/profile_staff.html",{"user":get_user,"staff":get_staff})

def profile_staff_save(request):
    """view to update user's personal information"""
    if request.method!="POST":
        return HttpResponseRedirect(reverse("profile_staff"))
    else:
        get_first_name=request.POST.get("first_name")
        get_last_name=request.POST.get("last_name")
        get_address=request.POST.get("address")
        get_password=request.POST.get("password")
        try:
            get_customuser=CustomisedUser.objects.get(id=request.user.id)
            get_customuser.first_name=get_first_name
            get_customuser.last_name=get_last_name
            if get_password is not None and get_password!="":
                get_customuser.set_password(get_password)
            get_customuser.save()

            get_staff=ModelStaff.models_object.get(admin=get_customuser.id)
            get_staff.address=get_address
            get_staff.save()
            messages.success(request, "Successfully Updated Profile")
            return HttpResponseRedirect(reverse("profile_staff"))
        except KeyError:
            messages.error(request, "Failed to Update Profile")
            return HttpResponseRedirect(reverse("profile_staff"))

@csrf_exempt
def staff_fcmtoken_save(request):
    """This method will save fcm token of loggedin user for push notifications."""
    get_token=request.POST.get("token")
    try:
        get_staff=ModelStaff.models_object.get(admin=request.user.id)
        get_staff.token_fcm=get_token
        get_staff.save()
        return HttpResponse("True")
    except KeyError:
        return HttpResponse("False")

def staff_all_notification(request):
    """View that shows all the notification sent by admin or other users in a single view with pagination."""
    get_staff=ModelStaff.models_object.get(admin=request.user.id)
    notifications_filter=ModelNotificationStaff.models_object.filter(staff_id=get_staff.id)
    return render(request,"staff_pages/notifications.html",{"notifications":notifications_filter})

def add_result_staff(request):
    """Add result page for students."""
    subjects_filter=ModelSubjects.models_object.filter(staff_id=request.user.id)
    session_years_all=ModelSessionYear.models_object.all()
    return render(request,"staff_pages/add_result_staff.html",
                  {"subjects":subjects_filter,"session_years":session_years_all})

def save_student_result(request):
    """Save student results from Add Result Page"""
    if request.method!='POST':
        return HttpResponseRedirect('add_result_staff')
    get_student_admin_id=request.POST.get('student_list')
    get_assignment_marks=request.POST.get('assignment_marks')
    get_exam_marks=request.POST.get('exam_marks')
    get_subject_id=request.POST.get('subject')


    get_student_obj=ModelStudents.models_object.get(admin=get_student_admin_id)
    get_subject_obj=ModelSubjects.models_object.get(id=get_subject_id)

    try:
        check_exist_filter=ModelStudentResult.models_object.filter(
            subject_id=get_subject_obj,student_id=get_student_obj).exists()
        if check_exist_filter:
            result_create=ModelStudentResult.models_object.get(
                subject_id=get_subject_obj,student_id=get_student_obj)
            result_create.subject_assignment_marks=get_assignment_marks
            result_create.subject_exam_marks=get_exam_marks
            result_create.save()
            messages.success(request, "Successfully Updated Result")
            return HttpResponseRedirect(reverse("add_result_staff"))
        result_create=ModelStudentResult(student_id=get_student_obj,
                                  subject_id=get_subject_obj,
                                  subject_exam_marks=get_exam_marks,
                                  subject_assignment_marks=get_assignment_marks)
        result_create.save()
        messages.success(request, "Successfully Added Result")
        return HttpResponseRedirect(reverse("staff_edit_result"))
    except KeyError:
        messages.error(request, "Failed to Add Result")
        return HttpResponseRedirect(reverse("staff_edit_result"))

@csrf_exempt
def fetch_result_student(request):
    """Fetch Student Results and display on Edit Result Page"""
    get_subject_id=request.POST.get('subject_id')
    get_student_id=request.POST.get('student_id')
    get_student_obj=ModelStudents.models_object.get(admin=get_student_id)
    result_filter=ModelStudentResult.models_object.filter(
        student_id=get_student_obj.id,subject_id=get_subject_id).exists()
    if result_filter:
        result_filter=ModelStudentResult.models_object.get(
            student_id=get_student_obj.id,subject_id=get_subject_id)
        result_data={"exam_marks":result_filter.subject_exam_marks,
                     "assign_marks":result_filter.subject_assignment_marks}
        return HttpResponse(json.dumps(result_data))
    return HttpResponse("False")

def live_video_conference(request):
    """Live Video Conference View"""
    subjects_filter=ModelSubjects.models_object.filter(staff_id=request.user.id)
    session_years_all=ModelSessionYear.models_object.all()
    return render(request,"staff_pages/live_video_conference.html",
                  {"subjects":subjects_filter,"session_years":session_years_all})

def live_classroom_start_process(request):
    """Start Live Classroom Process"""
    get_session_year=request.POST.get("session_year")
    get_subject=request.POST.get("subject")

    get_subject_obj=ModelSubjects.models_object.get(id=get_subject)
    get_session_obj=ModelSessionYear.models_object.get(id=get_session_year)
    checks_filter=ModelOnlineClassRoom.models_object.filter(
        subject=get_subject_obj,session_years=get_session_obj,is_active=True).exists()
    if checks_filter:
        get_data=ModelOnlineClassRoom.models_object.get(
            subject=get_subject_obj,session_years=get_session_obj,is_active=True)
        room_pwd_generate=get_data.room_pwd
        roomname_generate=get_data.room_name
    else:
        room_pwd_generate=datetime.now().strftime('%Y%m-%d%H-%M%S-') + str(uuid4())
        roomname_generate=datetime.now().strftime('%Y%m-%d%H-%M%S-') + str(uuid4())
        get_staff_obj=ModelStaff.models_object.get(admin=request.user.id)
        online_class=ModelOnlineClassRoom(room_name=roomname_generate,
                                         room_pwd=room_pwd_generate,
                                         subject=get_subject_obj,
                                         session_years=get_session_obj,
                                         started_by=get_staff_obj,
                                         is_active=True)
        online_class.save()

    return render(request,"staff_pages/live_video_conference.html",
                  {"username":request.user.username,
                   "password":room_pwd_generate,
                   "roomid":roomname_generate,
                   "subject":get_subject_obj.subject_name_char,
                   "session_year":get_session_obj})


def return_html_widget(request):
    """Return HTML Widget for Staff Page"""
    return render(request,"widget.html")
