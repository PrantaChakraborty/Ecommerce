from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)  # coupon code
    valid_from = models.DateTimeField()  # date for validity
    valid_to = models.DateTimeField()  # date for validity

    discount = models.IntegerField(validators=[MinValueValidator(0),
                                               MaxValueValidator(100)])
    active = models.BooleanField()  # to check active or not

    def __str__(self):
        return self.code
