from django.db import models

# Create your models here.
from django.db import models

class Student(models.Model):
    stuId = models.CharField(max_length=10, primary_key=True)
    stuname = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)
    age = models.IntegerField()
    branch = models.CharField(max_length=100)
    collegeName = models.CharField(max_length=200)
    email = models.EmailField()

    def __str__(self):
        return self.stuname