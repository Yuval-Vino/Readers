from django.contrib.auth.models import User
from django.db import models
import datetime
from django.core.exceptions import ValidationError


def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.user.id, filename)


class Student(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True)
    birth_date = models.DateField()
    profile_pic = models.ImageField(default='default-profile-pic.png', upload_to=user_directory_path)

    @staticmethod
    def create(username, password, birth_date):
        user = Student(user=User.objects.create_user(
            username=username,
            password=password), birth_date=birth_date)
        user.user.save()
        user.save()
        return user

    def validate_and_save(self, birth_date, profile_picture=None):
        errors = []
        try:
            datetime.datetime.strptime(birth_date, '%Y-%m-%d').date()
            self.birth_date = birth_date
        except ValueError:
            errors.append("Invalid birth date format, Please use the format YYYY-MM-DD.")

        if profile_picture:
            if not profile_picture.name.lower().endswith(('.png', '.jpeg', '.jpg')):
                errors.append("Invalid picture format, Please upload a JPEG or PNG image.")
            else:
                self.profile_pic.save(profile_picture.name, profile_picture, save=False)

        if errors:
            raise ValidationError("\n".join(errors))

        else:
            self.save()
