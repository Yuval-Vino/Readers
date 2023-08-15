from django.db import models


class Course(models.Model):
    name = models.CharField(max_length=100, unique=True, blank=False)

    @staticmethod
    def create(name):
        course = Course(name=name)
        course.save()
        return course
