from django import template
import json
from io import BytesIO
import base64
from grade.models import CustomGradeField,Grade


register = template.Library()


@register.filter
def load_grade(data,header):
    try:
        return getattr(data, header)
    except Exception as e:
        grade_list = Grade.objects.filter(id=data.id)
        for grade in grade_list:
            for custom_field in grade.customfield.all():
                if custom_field.name == header:
                    return custom_field.value
