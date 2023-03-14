from django.db import models

# Model for grade table
class GradeTable(models.Model):
    subject_id =  models.CharField( max_length=15,blank=False, null=False)
    subject_name = models.CharField(max_length=100 ,blank=False, null=False)
    section = models.CharField(max_length=100 ,blank=False, null=False)
    year = models.CharField(max_length=4,blank=False, null=False)
    semestre = models.CharField(max_length=1,blank=False, null=False)
    department = models.CharField(max_length=100,blank=False, null=False)
    desc = models.CharField(max_length=255,blank=False, null=False)
    user = models.CharField(max_length=255,blank=False, null=False)
    grade_table = models.CharField(max_length=255,blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False)

    def __str__(self):
        return f"Table Name : {self.grade_table} Status : {self.status} Created_at : {self.created_at} "
