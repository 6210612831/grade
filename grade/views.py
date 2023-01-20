from django.shortcuts import render
import json
import pandas as pd
from .models import CustomGradeField,Grade
from django.http import HttpResponseRedirect
from django.urls import reverse
import requests
from rest_framework import status

# def handle_uploaded_file(f):
#     with open('path/to/save/file', 'wb+') as destination:
#         for chunk in f.chunks():
#             destination.write(chunk)


HOST = "http://127.0.0.1:8000"

# Create your views here.
def index(request):
    return render(request, "grade/index.html")


def delete_table_view(request,subject):
    try:
        grade_list = Grade.objects.filter(subject=subject)
        for grade in grade_list:
            for custom_field in grade.customfield.all():
                custom_field.delete()
            grade.delete()
        return HttpResponseRedirect(reverse("grade:index"))
    except:
        return HttpResponseRedirect(reverse("grade:index"))
    

def login_view(request):
    try:
        if request.session['user_id']:
            # print(request.session['user_id'])
            return render(request, "grade/grade.html")
    except:
        if request.method == "POST":
            username = request.POST["username"]
            password = request.POST["password"]
            # response = ldap3_authen(username,password)
            data = {
                'username': username,
                'password': password
            }
            response = requests.post(
                HOST+'/api/v1/authentication/', data=data)
            if response.status_code == status.HTTP_200_OK:
                request.session['user_id'] = username
                # print(request.session['user_id'])
                # print("render policy page")
                request.session['login_status'] = username
                request.session.modified = True
                # return render(request, "web/policy.html")
                return render(request, "grade/grade.html")
            else:
                return render(request, "grade/login.html")
        return render(request, "grade/login.html")


def manage_grade_view(request):
    try:
        request.session['user_id']
        # Upload Excel file and create db to store data
        if request.method == 'POST':
            try:
                df = pd.read_excel(request.FILES['file'])
                data = df.to_json(orient='records')
                student_list = json.loads(data)
                # print(json_str)
                # json_str = [{"aa":11,"bb":22,"cc":33,"dd":44},{"aa":"\u0e01\u0e01","bb":"\u0e02\u0e02","cc":"\u0e04\u0e04","dd":"\u0e07\u0e07"}]
                table_key = ['std_id','name','subject','grade','midterm','final']
                for student in student_list:
                    student_data = {}
                    custom_obj_list = []
                    for key in student:
                        if key in table_key:
                            student_data[key] = student[key]
                        else:
                            custom_obj = CustomGradeField.objects.create(name=key,value=student[key])
                            custom_obj_list.append(custom_obj)
                    grade_obj = Grade.objects.create(std_id=student['std_id'],name=student['name'],subject=student['subject'],grade=student['grade'],midterm=student['midterm'],final=student['final'])
                    for custom_field in custom_obj_list:
                        grade_obj.customfield.add(custom_field)
                        grade_obj.save()   
                ### save data to excel 
                # df = pd.DataFrame(student_list)
                # df.to_excel("output.xlsx", index=False)
                return HttpResponseRedirect(reverse("grade:manage_grade"))
            except Exception as e:
                print('File error',e)
            return HttpResponseRedirect(reverse("grade:manage_grade"))
        # Load data to manage_grade page
        else:
            # subject = 'cn203'
            subject_list = Grade.objects.values_list('subject', flat=True).distinct()
            output = []
            for subject in subject_list:
                grade_list = Grade.objects.filter(subject=subject)
                # grade_list = Grade.objects.filter(subject=subject,std_id = request.session['user_id'])
                header_list = ['std_id','name','subject','grade','midterm','final']
                for grade in grade_list:
                    for custom_field in grade.customfield.all():
                        header_list.append(custom_field.name)
                    break
                output.append({'grade_list':grade_list,'header_list':header_list})
            return render(request, "grade/manage_grade.html",{'output':output})
    except:
        return HttpResponseRedirect(reverse("grade:login"))


def grade_view(request):
    try:
        request.session['user_id']
        # Upload Excel file and create db to store data
        # subject = 'cn203'
        subject_list = Grade.objects.values_list('subject', flat=True).distinct()
        output = []
        for subject in subject_list:
            # grade_list = Grade.objects.filter(subject=subject)
            grade_list = Grade.objects.filter(subject=subject,std_id = request.session['user_id'])
            header_list = ['std_id','name','subject','grade','midterm','final']
            for grade in grade_list:
                for custom_field in grade.customfield.all():
                    header_list.append(custom_field.name)
                break
            output.append({'grade_list':grade_list,'header_list':header_list})
        return render(request, "grade/grade.html",{'output':output})
    except:
        return HttpResponseRedirect(reverse("grade:login"))