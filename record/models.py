from django.core.exceptions import ValidationError
from django.db import models

from course.models import Course
from users.models import Student


def validate(name, owner, course, record, price):
    if not name or not owner or not course or not record or price is None:
        raise ValidationError("All fields (name, owner, course, record, price) must be provided.")

    if Record.objects.filter(name=name, owner=owner).exists():
        raise ValidationError("A record with the same name and owner already exists.")

    if not isinstance(price, (float, int)) or price < 0:
        raise ValidationError("Price must be a valid float or integer.")

    if not record.name.lower().endswith(('.mp3', '.wav', '.ogg')):
        raise ValidationError("Invalid audio file format. Supported formats: .mp3, .wav, .ogg")


class Record(models.Model):
    name = models.CharField(max_length=100, blank=False)
    owner = models.ForeignKey(Student, on_delete=models.CASCADE, blank=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, blank=False)
    record = models.FileField(upload_to='uploads/', blank=False)
    price = models.FloatField(blank=False)
    downloads = models.IntegerField(default=0)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['name', 'owner'], name='unique_record')]
        unique_together = ('name', 'owner')

    @staticmethod
    def create(name, owner, course, record, price):
        try:
            validate(name, owner, course, record, price)
        except ValidationError as error:
            raise error

        record = Record(name=name, owner=owner, course=course,
                        record=record, price=price)
        record.save()
        return record
