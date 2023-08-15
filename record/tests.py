import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from course.models import Course
from users.models import Student
from .models import Record


@pytest.fixture
def student():
    student = Student.create(
        username='test-user',
        password='password',
        birth_date='1990-01-01')
    return student


@pytest.fixture
def course():
    course = Course.create(
        name='Test-course')
    return course


@pytest.mark.django_db
class TestRecordModel:

    @pytest.mark.parametrize(
        "name,record, price, expected_errors",
        [
            ("Valid Record",
             SimpleUploadedFile("audio.mp3", b"file_content", content_type="audio/mp3"), 10.99,
             None),

            ("Invalid Price Record",
             SimpleUploadedFile("audio.mp3", b"file_content", content_type="audio/mp3"), "invalid_price",
             "Price must be a valid float or integer."),

            ("Invalid Format Record",
             SimpleUploadedFile("invalid.txt", b"file_content", content_type="text/plain"), 5.99,
             "Invalid audio file format. Supported formats: .mp3, .wav, .ogg"),

            (None,
             SimpleUploadedFile("audio.mp3", b"file_content", content_type="audio/mp3"), 12.99,
             "All fields (name, owner, course, record, price) must be provided."),

            ("Missing Record",
             None, 9.99,
             "All fields (name, owner, course, record, price) must be provided."),

            ("Negative Price",
             SimpleUploadedFile("audio.mp3", b"file_content", content_type="audio/mp3"), -5.99,
             "Price must be a valid float or integer."),
        ]
    )
    def test_record_creation(self, name, student, course, record, price, expected_errors):
        if expected_errors:
            with pytest.raises(ValidationError) as e:
                Record.create(name=name, owner=student, course=course, record=record, price=price)
                assert expected_errors in str(e.value)
        else:
            Record.create(name=name, owner=student, course=course, record=record, price=price).full_clean()

    def test_unique_constraint(self, student, course):
        record_file1 = SimpleUploadedFile("audio1.mp3", b"file_content", content_type="audio/mp3")
        Record.create(name='Unique Record', owner=student, course=course,
                      record=record_file1, price=10.99)

        record_file2 = SimpleUploadedFile("audio2.mp3", b"file_content", content_type="audio/mp3")
        with pytest.raises(ValidationError):
            Record.create(name='Unique Record', owner=student, course=course,
                          record=record_file2, price=15.99)
