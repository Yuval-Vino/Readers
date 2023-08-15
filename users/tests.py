from .models import Student, user_directory_path
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db import IntegrityError
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
import os
from django.conf import settings


@pytest.fixture
def student():
    student = Student.create(
        username='Player',
        password='password',
        birth_date='1990-01-01', )
    return student


@pytest.mark.django_db
class TestStudentModel:

    def test_get_student(self, student):
        student_from_db = Student.objects.get(pk=student.pk)
        assert student_from_db == student

    def test_create_student_with_new_user(self):
        student = Student.create(username='test-user',
                                 password='password',
                                 birth_date='1990-01-01',
                                 )
        assert isinstance(student.user, User)
        assert student.user.username == 'test-user'
        assert student.user.check_password('password')

    def test_create_student_with_existing_username(self):
        user = User.objects.create_user(username='test-user', password='password')
        user.save()
        with pytest.raises(IntegrityError):
            Student.create(
                username=user.username,
                password=user.password,
                birth_date='1990-01-01')

    def test_delete_student(self, student):
        student_copy = student
        student_copy.delete()
        with pytest.raises(Student.DoesNotExist):
            Student.objects.get(pk=student.pk)

    def test_delete_user_deletes_student(self, student):
        user = student.user
        user.delete()
        with pytest.raises(student.DoesNotExist):
            Student.objects.get(pk=student.pk)

    def test_create_student_with_valid_fields(self):
        Student.create(
            username="test-user",
            password="password",
            birth_date='1990-01-01', ).full_clean()

    def test_create_student_with_invalid_birth_date(self):
        with pytest.raises(ValidationError):
            Student.create(
                username="test-user",
                password="password",
                birth_date='invalid date', ).full_clean()

    def test_create_student_with_blank_birth_date(self):
        with pytest.raises(ValidationError):
            Student.create(
                username="test-user",
                password="password",
                birth_date='').full_clean()

    def test_validate_and_save_valid_data(self, student):
        birth_date = '1999-02-01'

        assert student.birth_date != birth_date

        profile_pic = SimpleUploadedFile("sample.jpg", b"dummy_image_data", content_type="image/jpeg")
        student.validate_and_save(birth_date, profile_pic)

        assert student.birth_date == birth_date
        expected_file_path = os.path.join(settings.MEDIA_ROOT, student.profile_pic.name)
        assert os.path.exists(expected_file_path)

    @pytest.mark.parametrize(
        "birth_date, profile_pic, expected_errors",
        [
            ('invalid_date',
             SimpleUploadedFile("test_image.jpg", b"dummy_image_data", content_type="image/jpeg"),
             ["Invalid birth date format", ]),

            ('2000-01-01',
             SimpleUploadedFile("test_image.txt", b"dummy_file_data", content_type="image/jpeg"),
             ["Invalid picture format", ]),

            ("invalid_date",
             SimpleUploadedFile("test_image.txt", b"dummy_image_data", content_type="image/jpeg"),
             ["Invalid birth date format", "Invalid picture format", ]),
        ]
    )
    def test_validate_and_save_invalid_inputs(self, student, birth_date, profile_pic,
                                              expected_errors):
        with pytest.raises(ValidationError) as e:
            student.validate_and_save(birth_date, profile_pic)

            for error in expected_errors:
                assert error in str(e.value)


@pytest.mark.django_db
class testUserDirectoryPath:
    def test_user_directory_path(self, student):
        filename = 'example.jpg'
        result = user_directory_path(student, filename)
        expected_output = f'user_{student.user.id}/example.jpg'
        assert result == expected_output
