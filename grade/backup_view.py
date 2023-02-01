
# # Manage_grade Page
# def manage_grade_view(request):
#     try:
#         request.session['user_id']
#         # Upload Excel file and create db to store data
#         if request.method == 'POST':
#             try:
#                 # Read exel file to json
#                 sid = request.POST["sid"] #รหัสวิชา
#                 sname = request.POST["sname"] #ชื่อวิชา
#                 section = request.POST["section"] #SECTION
#                 year = request.POST["year"] #ปีการศึกษา
#                 semestre = request.POST["semestre"] #ภาคการศึกษา
#                 department = request.POST["department"] #ภาควิชา
#                 course = request.POST["course"] #โครงการ / หลักสูตร
#                 desc = request.POST["desc"] #หมายเหตุ

#                 df = pd.read_excel(request.FILES['file'])
#                 data = df.to_json(orient='records')
#                 student_list = json.loads(data)
#                 # Check if subject is exist
#                 for student in student_list:
#                     temp = Grade.objects.filter(subject=student['subject'])
#                     if len(temp) > 0:
#                         output = get_grade_data(0, request)
#                         return render(request, "grade/manage_grade.html", {'output': output, 'message': 'subject has already exist'})
#                     break
#                 # Upload exel to db
#                 table_key = ['std_id', 'name', 'subject',
#                              'grade', 'midterm', 'final']
#                 for student in student_list:
#                     student_data = {}
#                     custom_obj_list = []
#                     for key in student:
#                         if key in table_key:
#                             student_data[key] = student[key]
#                         else:
#                             custom_obj = CustomGradeField.objects.create(
#                                 name=key, value=student[key])
#                             custom_obj_list.append(custom_obj)
#                     grade_obj = Grade.objects.create(std_id=student['std_id'], name=student['name'], subject=student['subject'],
#                                                      grade=student['grade'], midterm=student['midterm'], final=student['final'])
#                     for custom_field in custom_obj_list:
#                         grade_obj.customfield.add(custom_field)
#                         grade_obj.save()
#                 output = get_grade_data(0, request)
#                 return render(request, "grade/manage_grade.html", {'output': output, 'message': 'upload success'})
#             except:
#                 # If upload file error
#                 output = get_grade_data(0, request)
#                 return render(request, "grade/manage_grade.html", {'output': output, 'message': 'exel file error'})
#         # Load data to manage_grade page
#         else:
#             output = get_grade_data(0, request)
#             return render(request, "grade/manage_grade.html", {'output': output, 'message': 'loaded'})
#     except:
#         return HttpResponseRedirect(reverse("grade:login"))



# def get_grade_data(choice, request):
#     header_list = []
#     # get cloumn name
#     with connection.cursor() as cursor:
#                 cursor.execute("SELECT `COLUMN_NAME` \
#                 FROM `INFORMATION_SCHEMA`.`COLUMNS` \
#                 WHERE `TABLE_NAME`='cn101_230001_2565_1_1_6210612831';")
#                 products = cursor.fetchall()
#                 # Column name to list
#                 for column_name in products:
#                     header_list.append(column_name[0])
#                 print(header_list)
#     return True


# # Load grade data
# def get_grade_data(choice, request):
#     subject_list = Grade.objects.values_list('subject', flat=True).distinct()
#     output = []
#     for subject in subject_list:
#         if choice == 0:
#             grade_list = Grade.objects.filter(subject=subject)
#         else:
#             grade_list = Grade.objects.filter(
#                 subject=subject, std_id=request.session['user_id'])
#         header_list = ['std_id', 'name',
#                        'subject', 'grade', 'midterm', 'final']
#         for grade in grade_list:
#             for custom_field in grade.customfield.all():
#                 header_list.append(custom_field.name)
#             break
#         output.append({'grade_list': grade_list, 'header_list': header_list})
#     return output
