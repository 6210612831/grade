from django.db import models




# Model for custom field
class CustomGradeField(models.Model):
    name = models.CharField(max_length=100 ,blank=False, null=False)
    value = models.CharField(max_length=255,blank=True, null=True)

    @property
    def context_data(self):
        return {
            'name': self.name,
            'value': self.value,

        }

    def __str__(self):
        return f"Name : {self.name} Value : {self.value}"


# Model for grade
class Grade(models.Model):
    std_id =  models.CharField( max_length=15,blank=False, null=False)
    name = models.CharField(max_length=100 ,blank=False, null=False)
    subject = models.CharField(max_length=100 ,blank=False, null=False)
    grade = models.CharField(max_length=100)
    midterm = models.CharField(max_length=100)
    final = models.CharField(max_length=100)
    customfield = models.ManyToManyField(CustomGradeField)

    # @property
    # def context_data(self):
    #     return {
    #         'name': self.name,
    #         'desc': self.desc,
    #         'status': self.status,
    #         'user': self.user,

    #     }

    def __str__(self):
        return f"Name : {self.name} Subject : {self.subject} Grade : {self.grade} Midterm : {self.midterm} Final : {self.final} Customfield : {self.customfield}"


# Model for grade table
class GradeTable(models.Model):
    subject_id =  models.CharField( max_length=15,blank=False, null=False)
    subject_name = models.CharField(max_length=100 ,blank=False, null=False)
    section = models.CharField(max_length=100 ,blank=False, null=False)
    year = models.CharField(max_length=4,blank=False, null=False)
    semestre = models.CharField(max_length=1,blank=False, null=False)
    department = models.CharField(max_length=100,blank=False, null=False)
    course = models.CharField(max_length=100,blank=False, null=False)
    desc = models.CharField(max_length=255,blank=False, null=False)
    user = models.CharField(max_length=255,blank=False, null=False)
    grade_table = models.CharField(max_length=255,blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False)

    def __str__(self):
        return f"Table Name : {self.grade_table} Status : {self.status} Created_at : {self.created_at} "



# Model for map subject and instructor who create
class SubjectInstructor(models.Model):
    subject = models.CharField(max_length=100 ,blank=False, null=False)
    instructor = models.CharField(max_length=255,blank=True, null=True)

    @property
    def context_data(self):
        return {
            'subject': self.subject,
            'instructor': self.instructor,

        }

    def __str__(self):
        return f"Subject : {self.subject}, Instructor : {self.instructor}"