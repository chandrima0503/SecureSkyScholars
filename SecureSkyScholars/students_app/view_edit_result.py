"""Module to view and edit result"""
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from students_app.forms import EditResultForm

from students_app.models import ModelStudents, ModelSubjects, ModelStudentResult
class ViewEditResultClass(View):
    """Class for viewing and editing results of student"""
    def get(self,request,*args,**kwargs):
        """Method for getting data from database and displaying it in the form."""
        print(args, kwargs)
        staff_id=request.user.id
        edit_result_form=EditResultForm(staff_id=staff_id)
        return render(request,"staff_pages/student_edit_result.html",{"form":edit_result_form})

    def post(self,request,*args,**kwargs):
        """Method for updating student's results after submitting a new one through the form."""
        print(args,kwargs)
        form=EditResultForm(staff_id=request.user.id,data=request.POST)
        if form.is_valid():
            student_admin_id = form.cleaned_data['student_ids']
            assignment_marks = form.cleaned_data['assignment_marks']
            exam_marks = form.cleaned_data['exam_marks']
            subject_id = form.cleaned_data['subject_id']

            student_obj = ModelStudents.models_object.get(admin=student_admin_id)
            subject_obj = ModelSubjects.models_object.get(id=subject_id)
            result=ModelStudentResult.models_object.get(
                subject_id=subject_obj,student_id=student_obj)
            result.subject_assignment_marks=assignment_marks
            result.subject_exam_marks=exam_marks
            result.save()
            messages.success(request, "Successfully Updated Result")
            return HttpResponseRedirect(reverse("student_edit_result"))
        messages.error(request, "Failed to Update Result")
        form=EditResultForm(request.POST,staff_id=request.user.id)
        return render(request,"staff_pages/student_edit_result.html",{"form":form})
