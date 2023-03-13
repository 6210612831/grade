from django.shortcuts import render
import json
import pandas as pd
from .models import GradeTable
from django.http import HttpResponseRedirect
from django.urls import reverse
import requests
from rest_framework import status

# def handle_uploaded_file(f):
#     with open('path/to/save/file', 'wb+') as destination:
#         for chunk in f.chunks():
#             destination.write(chunk)
from django.conf import settings
from django.db import connection


HOST = "https://restapi.engr.tu.ac.th"

# Create your views here.


def if_session(request):
    try:
        request.session['user_id']
        return True
    except:
        return False


def if_instructor(request):
    if request.session['user_status'] == 1:
        return True
    else:
        return False


def index(request):
    try:
        if request.session['user_id']:
            return HttpResponseRedirect(reverse("web_grade:grade"))
    except:
        return render(request, "web_grade/login.html")


# Login page
def login_view(request):
    try:
        if request.session['user_id']:
            return HttpResponseRedirect(reverse("web_grade:grade"))
    except:
        if request.method == "POST":
            username = request.POST["username"]
            password = request.POST["password"]
            data = {
                'username': username,
                'password': password
            }
            response = requests.post(
                HOST+'/api/v1/authentication/', data=data)
            if response.status_code == status.HTTP_200_OK:
                try:
                    int(username)
                    # request.session['user_status'] = 0  # student
                    request.session['user_status'] = 1  # student Test
                except:
                    request.session['user_status'] = 1  # instructor
                request.session['user_id'] = username
                request.session['login_status'] = username
                request.session.modified = True
                # return render(request, "web/policy.html")
                return HttpResponseRedirect(reverse("web_grade:grade"))
            else:
                return render(request, "web_grade/login.html")
        return render(request, "web_grade/login.html")


# Manage_grade Page
def manage_grade_view(request):
    if not if_session(request):
        return HttpResponseRedirect(reverse("web_grade:login"))
    if not if_instructor(request):
        return HttpResponseRedirect(reverse("web_grade:index"))

    try:
        request.session['user_id']
        # Upload Excel file and create db to store data
        if request.method == 'POST':
            try:
                # Read exel file to json
                subject_id = request.POST["sid"]  # รหัสวิชา
                subject_name = request.POST["sname"]  # ชื่อวิชา
                section = request.POST["section"]  # SECTION
                year = request.POST["year"]  # ปีการศึกษา
                semestre = request.POST["semestre"]  # ภาคการศึกษา
                department = request.POST["department"]  # ภาควิชา
                course = request.POST["course"]  # โครงการ / หลักสูตร
                desc = request.POST["desc"]  # หมายเหตุ
                df = pd.read_excel(request.FILES['file'])
                data = df.to_json(orient='records')
                student_list = json.loads(data)

                # Set table name
                grade_table = subject_id.upper()+'_'+section+'_'+year+'_' + \
                    semestre+'_'+course+'_'+department + \
                    '_'+request.session['user_id']
                if len(GradeTable.objects.filter(grade_table=grade_table)) != 0:
                    return render(request, "web_grade/manage_grade.html", {'message': 'Table is already exist,Please delete old table'})
                # Create GradeTable Object that store table's data
                grade = GradeTable.objects.create(subject_id=subject_id.upper(), subject_name=subject_name, section=section, year=year, semestre=semestre,
                                                  department=department, course=course, desc=desc, grade_table=grade_table, user=request.session['user_id'])
                # Get header for create table field
                create_table_sql = f"CREATE TABLE {grade_table} ("
                header = []
                try:
                    student_list[0]['std_id']
                except:
                    grade.delete()
                    return render(request, "web_grade/manage_grade.html", {'message': "Table ต้องมีฟิลด์ std_id"})
                for key in student_list[0]:
                    if create_table_sql[-1] != "(":
                        create_table_sql += ","
                    create_table_sql += f"`{key.upper()}` varchar(255)"
                    header.append(key)
                # Create table
                create_table_sql += ');'
                try:
                    with connection.cursor() as cursor:
                        cursor.execute(create_table_sql)
                except Exception as e:
                    grade.delete()
                    return render(request, "web_grade/manage_grade.html", {'message': f'Exel File Error : {e} or (Maybe table is already exist)'})

                # Upload exel to table
                try:
                    for student in student_list:
                        created_grade = grade
                        # Get header for create table field
                        insert_data_sql = f"INSERT INTO {grade_table} VALUES ("
                        for key in header:
                            if insert_data_sql[-1] != "(":
                                insert_data_sql += ","
                            if (key == 'grade' or key == 'GRADE'):
                                insert_data_sql += "\'" + str(student[key]).upper()+"\'"
                            elif (key == 'std_id' or key == 'STD_ID'):
                                if len(str(student[key])) != 10:
                                    raise Exception("ฟิลด์ STD_ID ต้องมีเลขนักศึกษา 10 ตัว")
                                else:
                                    insert_data_sql += "\'" + str(student[key])+"\'"
                            else:
                                insert_data_sql += "\'" + str(student[key])+"\'"
                            
                        insert_data_sql += ');'
                        # Insert each row of student data
                        with connection.cursor() as cursor:
                            cursor.execute(insert_data_sql)
                except Exception as e:
                    with connection.cursor() as cursor:
                        cursor.execute(f"DROP TABLE {created_grade.grade_table}")
                        created_grade.delete()
                    return render(request, "web_grade/manage_grade.html", {'message': f'Exel File Error E : {e}'})
                return HttpResponseRedirect(reverse("web_grade:courese_list"))
            # If upload file error
            except Exception as e:
                with connection.cursor() as cursor:
                    cursor.execute(f"DROP TABLE {grade.grade_table}")
                grade.delete()
                return render(request, "web_grade/manage_grade.html", {'message': f'Exel File Error : {e}'})
        # Load data to manage_grade page
        else:
            return render(request, "web_grade/manage_grade.html")
    # If cause Exception
    except Exception as e:
        return render(request, "web_grade/manage_grade.html", {'message': f'Error : {e}'})


def delete_table_view(request, grade_table_id):
    if not if_session(request):
        return HttpResponseRedirect(reverse("web_grade:login"))
    if not if_instructor(request):
        return HttpResponseRedirect(reverse("web_grade:index"))

    try:
        grade_table = GradeTable.objects.get(
            id=grade_table_id, user=request.session['user_id'])
        with connection.cursor() as cursor:
            cursor.execute(f"DROP TABLE {grade_table.grade_table}")
        grade_table.delete()
        grade_table_list = GradeTable.objects.filter(
            user=request.session['user_id'])
        return render(request, "web_grade/courese_list.html", {'grade_table_list': grade_table_list, 'message': 'Delete Success'})

    except Exception as e:
        grade_table_list = GradeTable.objects.filter(
            user=request.session['user_id'])
        return render(request, "web_grade/courese_list.html", {'grade_table_list': grade_table_list, 'message': f'Delete Error : {e}'})


# Grade Page
def grade_view(request):
    if not if_session(request):
        return HttpResponseRedirect(reverse("web_grade:login"))
    try:
        request.session['user_id']
        # subject = 'cn203'
        grade_table_list = GradeTable.objects.filter(status=True)
        return render(request, "web_grade/grade.html", {'grade_table_list': grade_table_list})
    except Exception as e:
        return HttpResponseRedirect(reverse("web_grade:login"))


def courese_list(request):
    if not if_session(request):
        return HttpResponseRedirect(reverse("web_grade:login"))
    if not if_instructor(request):
        return HttpResponseRedirect(reverse("web_grade:index"))
    grade_table_list = GradeTable.objects.filter(
        user=request.session['user_id'])
    return render(request, "web_grade/courese_list.html", {'grade_table_list': grade_table_list})


def logout_view(request):
    del request.session['user_id']
    return HttpResponseRedirect(reverse("web_grade:login"))


def show_grade_view(request, grade_table_id):
    if not if_session(request):
        return HttpResponseRedirect(reverse("web_grade:login"))

    grade_table = ""
    try:
        grade_table_data = GradeTable.objects.get(id=grade_table_id)
        header_list = []
        # get cloumn name
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT `COLUMN_NAME` FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_NAME`=\'"+grade_table_data.grade_table+"\';")
            products = cursor.fetchall()
            # Column name to list
            for column_name in products:
                header_list.append(column_name[0])
            # print(header_list)
        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT * FROM {grade_table_data.grade_table} WHERE `std_id`=\'"+request.session['user_id']+"\';")
            grade_table = cursor.fetchall()

    except:
        pass
    if grade_table == ():
        grade_table = "None"
        output = {'grade_list': grade_table}
    else:
        output = {'grade_list': grade_table,
                  'header_list': header_list,
                  'table_name': grade_table_data.grade_table,
                  'grade_table_id': grade_table_data.id,
                  'subject_name': grade_table_data.subject_name,
                  'subject_id': grade_table_data.subject_id,
                  'desc': grade_table_data.desc,
                  'date': grade_table_data.created_at,
                  }
    return render(request, "web_grade/show_grade.html", {'grade_table': output})


def change_status_view(request, grade_table_id):
    if not if_session(request):
        return HttpResponseRedirect(reverse("web_grade:login"))
    if not if_instructor(request):
        return HttpResponseRedirect(reverse("web_grade:index"))
    try:
        grade_table = GradeTable.objects.get(
            id=grade_table_id, user=request.session['user_id'])
        grade_table.status = grade_table.status == False
        grade_table.save()
        return HttpResponseRedirect(reverse("web_grade:courese_list"))
    except Exception as e:
        return HttpResponseRedirect(reverse("web_grade:courese_list"))


def course_info(request, grade_table_id):
    if not if_session(request):
        return HttpResponseRedirect(reverse("web_grade:login"))
    if not if_instructor(request):
        return HttpResponseRedirect(reverse("web_grade:index"))

    grade_table = ""
    student_num = 0
    summary_grade = {
        'A': 0,
        'BB': 0,
        'B': 0,
        'CC': 0,
        'C': 0,
        'DD': 0,
        'D': 0,
        'F': 0,
        'W': 0,
        'I':0,
        'ขส':0,
        'S':0,
        'U':0,
    }
    sum_grade = 0
    student_gpa = 0
    try:
        grade_table_data = GradeTable.objects.get(id=grade_table_id)
        header_list = []
        # get cloumn name
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT `COLUMN_NAME` FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_NAME`=\'"+grade_table_data.grade_table+"\';")
            products = cursor.fetchall()
            # Column name to list
            for column_name in products:
                header_list.append(column_name[0])
            # print(header_list)
        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT * FROM {grade_table_data.grade_table} WHERE '1';")
            grade_table = cursor.fetchall()
        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT GRADE FROM {grade_table_data.grade_table} WHERE '1';")
            grade_field = cursor.fetchall()
            # print(grade_field)
        for grade in grade_field:
            if grade[0] == 'B+':
                summary_grade['BB'] += 1
            elif grade[0] == 'C+':
                summary_grade['CC'] += 1
            elif grade[0] == 'D+':
                summary_grade['DD'] += 1
            else:
                summary_grade[grade[0]] += 1
            student_num += 1
            if grade[0] == 'A':
                sum_grade += 4.0
            elif grade[0] == 'B+':
                sum_grade += 3.5
            elif grade[0] == 'B':
                sum_grade += 3.0
            elif grade[0] == 'C+':
                sum_grade += 2.5
            elif grade[0] == 'C':
                sum_grade += 2.0
            elif grade[0] == 'D+':
                sum_grade += 1.5
            elif grade[0] == 'D':
                sum_grade += 1.0
            elif grade[0] == 'F':
                sum_grade += 0.0
            student_gpa = sum_grade/student_num
            student_gpa = "{:.2f}".format(student_gpa)

    except:
        pass
    if grade_table == ():
        grade_table = "None"
        output = {'grade_list': grade_table}
    else:
        output = {'grade_list': grade_table,
                  'header_list': header_list,
                  'table_name': grade_table_data.grade_table,
                  'grade_table_id': grade_table_data.id,
                  'subject_name': grade_table_data.subject_name,
                  'subject_id': grade_table_data.subject_id,
                  'desc': grade_table_data.desc,
                  'date': grade_table_data.created_at,
                  }

    return render(request, "web_grade/course_info.html", {'grade_table': output, 'summary_grade': summary_grade, 'student_num': student_num, 'student_gpa': student_gpa})


def search_subject_view(request):
    if not if_session(request):
        return HttpResponseRedirect(reverse("grade:login"))
    search_subject_list = []
    if request.method == 'POST':
        search_subject_key = request.POST["search_subject_key"]
        search_subject_list = GradeTable.objects.filter(
            subject_id=search_subject_key, status=True)
    grade_table_list = GradeTable.objects.filter(status=True)
    return render(request, "web_grade/grade.html", {'grade_table_list': grade_table_list, 'search_subject_list': search_subject_list})
