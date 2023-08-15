from django.db import IntegrityError
from .models import Course
import pytest


@pytest.fixture
def course():
    course = Course.create(
        name='Test-course')
    return course


@pytest.mark.django_db
class TestCourseModel:
    def test_get_course(self, course):
        course_from_db = Course.objects.get(pk=course.pk)
        assert course_from_db == course

    def test_create_course_with_existing_name(self, course):
        with pytest.raises(IntegrityError):
            Course.create(course.name)

    def test_delete_course(self, course):
        course_copy = course
        course_copy.delete()
        with pytest.raises(Course.DoesNotExist):
            Course.objects.get(pk=course.pk)
