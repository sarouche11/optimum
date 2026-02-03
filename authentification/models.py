from django.contrib.auth.models import User
from django.db import models
import random
from django.utils import timezone
from datetime import timedelta
from django.core.validators import RegexValidator

def generate_code():
    return ''.join(random.choices('AZERTYUIOPQSDFGHJKLMWXCVBN123456789', k=10))

class Profile(models.Model):
    phone_validator = RegexValidator(
        regex=r'^0\d{9}$',
        message="Le numéro doit commencer par 0 et contenir exactement 10 chiffres"
    )

    codeU = models.CharField(max_length=100, unique=True, default=generate_code)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    adresse = models.CharField(max_length=200, blank=False, null=False)
    phone = models.CharField(max_length=10, blank=False, null=False,validators=[phone_validator],)
    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username
    


def generate_otp():
    return str(random.randint(100000, 999999))

class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6, default=generate_otp)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return timezone.now() < self.created_at + timedelta(minutes=5)
