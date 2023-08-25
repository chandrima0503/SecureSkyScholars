"""Django models file"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver
from django.db.models.signals import post_save


# Create your models here.
class ModelSessionYear(models.Model):
    """Model for Session Year"""
    id=models.AutoField(primary_key=True)
    start_session_year=models.DateField()
    end_session_year=models.DateField()
    models_object=models.Manager()

class CustomisedUser(AbstractUser):
    """Model for Customised User"""
    user_type_array=((1,"Admin"),(2,"Staff"),(3,"Student"))
    user_type=models.CharField(default=1,choices=user_type_array,max_length=10)

class ModelAdmin(models.Model):
    """Model for Admin"""
    id=models.AutoField(primary_key=True)
    admin=models.OneToOneField(CustomisedUser,on_delete=models.CASCADE)
    created_time=models.DateTimeField(auto_now_add=True)
    updated_time=models.DateTimeField(auto_now_add=True)
    models_object=models.Manager()

class ModelStaff(models.Model):
    """Model for Staff"""
    id=models.AutoField(primary_key=True)
    admin=models.OneToOneField(CustomisedUser,on_delete=models.CASCADE)
    address_text=models.TextField()
    created_time=models.DateTimeField(auto_now_add=True)
    updated_time=models.DateTimeField(auto_now_add=True)
    token_fcm=models.TextField(default="")
    models_object=models.Manager()

class ModelCourses(models.Model):
    """Model for Student"""
    id=models.AutoField(primary_key=True)
    course_name_char=models.CharField(max_length=255)
    created_time=models.DateTimeField(auto_now_add=True)
    updated_time=models.DateTimeField(auto_now_add=True)
    models_object=models.Manager()


class ModelSubjects(models.Model):
    """Model for Subjects"""
    id=models.AutoField(primary_key=True)
    subject_name_char=models.CharField(max_length=255)
    course_id=models.ForeignKey(ModelCourses,on_delete=models.CASCADE,default=1)
    staff_id=models.ForeignKey(CustomisedUser,on_delete=models.CASCADE,default=1)
    created_time=models.DateTimeField(auto_now_add=True)
    updated_time=models.DateTimeField(auto_now_add=True)
    models_object=models.Manager()

class ModelStudents(models.Model):
    """Model for Students"""
    id=models.AutoField(primary_key=True)
    admin=models.OneToOneField(CustomisedUser,on_delete=models.CASCADE)
    gender_val=models.CharField(max_length=255)
    profile_pic=models.FileField()
    address_text=models.TextField()
    course_id=models.ForeignKey(ModelCourses,on_delete=models.DO_NOTHING)
    session_year_id=models.ForeignKey(ModelSessionYear,on_delete=models.CASCADE)
    created_time=models.DateTimeField(auto_now_add=True)
    updated_time=models.DateTimeField(auto_now_add=True)
    token_fcm=models.TextField(default="")
    models_object = models.Manager()

class ModelAttendance(models.Model):
    """Model for Attendance"""
    id=models.AutoField(primary_key=True)
    subject_id=models.ForeignKey(ModelSubjects,on_delete=models.DO_NOTHING)
    attendance_timestamp=models.DateField()
    created_time=models.DateTimeField(auto_now_add=True)
    session_year_id=models.ForeignKey(ModelSessionYear,on_delete=models.CASCADE)
    updated_time=models.DateTimeField(auto_now_add=True)
    models_object = models.Manager()

class ModelAttendanceReport(models.Model):
    """Model for Attendance Report"""
    id=models.AutoField(primary_key=True)
    student_id=models.ForeignKey(ModelStudents,on_delete=models.DO_NOTHING)
    attendance_id=models.ForeignKey(ModelAttendance,on_delete=models.CASCADE)
    status_bool=models.BooleanField(default=False)
    created_time=models.DateTimeField(auto_now_add=True)
    updated_time=models.DateTimeField(auto_now_add=True)
    models_object=models.Manager()

class ModelLeaveReportStudent(models.Model):
    """Model for Student Leave Report"""
    id=models.AutoField(primary_key=True)
    student_id=models.ForeignKey(ModelStudents,on_delete=models.CASCADE)
    leave_date_char=models.CharField(max_length=255)
    leave_message_text=models.TextField()
    leave_status_int=models.IntegerField(default=0)
    created_time=models.DateTimeField(auto_now_add=True)
    updated_time=models.DateTimeField(auto_now_add=True)
    models_object=models.Manager()

class ModelLeaveReportStaff(models.Model):
    """Model for Staff Leave Report"""
    id = models.AutoField(primary_key=True)
    staff_id = models.ForeignKey(ModelStaff, on_delete=models.CASCADE)
    leave_date_char = models.CharField(max_length=255)
    leave_message_text = models.TextField()
    leave_status_int = models.IntegerField(default=0)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now_add=True)
    models_object = models.Manager()


class ModelFeedBackStudent(models.Model):
    """Model for Student Feedback"""
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(ModelStudents, on_delete=models.CASCADE)
    feedback_text = models.TextField()
    feedback_reply_text = models.TextField()
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now_add=True)
    models_object = models.Manager()


class ModelFeedBackStaff(models.Model):
    """Model for Staff Feedback"""
    id = models.AutoField(primary_key=True)
    staff_id = models.ForeignKey(ModelStaff, on_delete=models.CASCADE)
    feedback_text = models.TextField()
    feedback_reply_text=models.TextField()
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now_add=True)
    models_object = models.Manager()


class ModelNotificationStudent(models.Model):
    """Model for Student Notification"""
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(ModelStudents, on_delete=models.CASCADE)
    message_text = models.TextField()
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now_add=True)
    models_object = models.Manager()


class ModelNotificationStaff(models.Model):
    """Model for Staff Notification"""
    id = models.AutoField(primary_key=True)
    staff_id = models.ForeignKey(ModelStaff, on_delete=models.CASCADE)
    message_text = models.TextField()
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now_add=True)
    models_object = models.Manager()

class ModelStudentResult(models.Model):
    """Model for Student Result"""
    id=models.AutoField(primary_key=True)
    student_id=models.ForeignKey(ModelStudents,on_delete=models.CASCADE)
    subject_id=models.ForeignKey(ModelSubjects,on_delete=models.CASCADE)
    subject_exam_marks_float=models.FloatField(default=0)
    subject_assignment_marks_float=models.FloatField(default=0)
    created_time=models.DateField(auto_now_add=True)
    updated_time=models.DateField(auto_now_add=True)
    models_object=models.Manager()

class ModelOnlineClassRoom(models.Model):
    """Model for Online Class Room"""
    id=models.AutoField(primary_key=True)
    room_name_text=models.CharField(max_length=255)
    room_pwd_text=models.CharField(max_length=255)
    subject=models.ForeignKey(ModelSubjects,on_delete=models.CASCADE)
    session_years=models.ForeignKey(ModelSessionYear,on_delete=models.CASCADE)
    started_by=models.ForeignKey(ModelStaff,on_delete=models.CASCADE)
    is_active_bool=models.BooleanField(default=True)
    created_time=models.DateTimeField(auto_now_add=True)
    models_object=models.Manager()


@receiver(post_save,sender=CustomisedUser)
def user_profile_create(sender,instance,created,**kwargs):
    """Module for user profile create"""
    print(sender, kwargs)
    if created:
        if instance.user_type==1:
            ModelAdmin.models_object.create(admin=instance)
        if instance.user_type==2:
            ModelStaff.models_object.create(
                admin=instance,
                address_text="")
        if instance.user_type==3:          
            ModelStudents.models_object.create(
                admin=instance,
                course_id=ModelCourses.models_object.get(
                id=ModelCourses.models_object.order_by('id').first().id),
                session_year_id=ModelSessionYear.models_object.get(
                id=ModelSessionYear.models_object.order_by('id').first().id),
                address_text="",
                profile_pic="",
                gender_val=""
                )

@receiver(post_save,sender=CustomisedUser)
def user_profile_save(sender,instance,**kwargs):
    """Module for user profile save """
    print(sender, kwargs)
    if instance.user_type==1:
        instance.modeladmin.save()
    if instance.user_type==2:
        instance.modelstaff.save()
    if instance.user_type==3:
        instance.modelstudents.save()
