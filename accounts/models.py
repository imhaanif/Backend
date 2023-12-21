from django.db import models
from PIL import Image
import os
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
import random
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager
)

from django.utils import timezone


def get_filename_ext(filepath):

    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext


def upload_image_path(instance, filename):

    new_filename = random.randint(1, 3910209312)
    name, ext = get_filename_ext(filename)
    final_filename = '{new_filename}{ext}'.format(
        new_filename=new_filename, ext=ext)
    return "profile/{new_filename}/{final_filename}".format(
        new_filename=new_filename,
        final_filename=final_filename
    )


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email no')

        user = self.model(
            email=email,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email=email,
            password=password,
        )
        user.is_admin = True
        user.is_active = True
        user.is_superuser = True
        user.save(using=self._db)
        return user






class User(AbstractBaseUser):
    email = models.EmailField(unique=True, null=True, blank=True)
    fname = models.CharField(max_length=240, null=True, blank=True)
    lname = models.CharField(max_length=240, null=True, blank=True)
    slug = models.SlugField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=240, null=True, blank=True)
    email_ac_timestamp = models.DateTimeField(
        default=timezone.now, null=True, blank=True)
    timestamp = models.DateTimeField(
        default=timezone.now, null=True, blank=True)
    is_active = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    image = models.ImageField(
        upload_to=upload_image_path, null=True, blank=True)
    thumbnail = ImageSpecField(
        source='image',
        processors=[ResizeToFill(200, 200)],
        format='jpeg',
        options={'quality': 80}
    )

    is_google_user = models.BooleanField(default=False)
    google_profile_img = models.CharField(max_length=240, null=True, blank=True)
    google_id = models.CharField(max_length=240, null=True, blank=True)
    
    is_mfa = models.BooleanField(default=False)
    is_mfa_code_sent = models.BooleanField(default=False)
    mfa_code = models.CharField(max_length=6, blank=True, null=True)
    mfa_code_time = models.DateTimeField(null=True, blank=True)

 
    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return str(self.email)

    def get_full_name(self):
        return self.fname

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


