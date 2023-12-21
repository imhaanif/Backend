import random
import os
from statistics import mode
from django.db import models
from accounts.models import User
from django.core.exceptions import ValidationError






def get_filename_ext(filepath):

    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext


def upload_file_path(instance, filename):

    new_filename = random.randint(1, 3910209312)
    name, ext = get_filename_ext(filename)
    final_filename = '{new_filename}{ext}'.format(
        new_filename=new_filename, ext=ext)
    return "files/{final_filename}".format(
        new_filename=new_filename,
        final_filename=final_filename
    )



state = (
    ('found', 'found'),
    ('lost', 'lost'),
)
# Card & Official documents
# Wallet
# Electronics
# Personal stuff
# Bag & Luggage
# Animals
# Persons

main_cat = (
    ('Card & Official documents', 'Card & Official documents'),
    ('Wallet', 'Wallet'),
    ('Electronics', 'Electronics'),
    ('Personal stuff', 'Personal stuff'),
    ('Bag & Luggage', 'Bag & Luggage'),
    ('Animals', 'Animals'),
    ('Persons', 'Persons'),
)






class Image(models.Model):
    image = models.ImageField(upload_to=upload_file_path, null=True, blank=True)

    def __str__(self):
        return str(self.id)



class Item(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    # claimed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    state = models.CharField(max_length=100, choices=state, default='Lost')
    status  = models.CharField(max_length=100, default='search')
    main_cat = models.CharField(max_length=100, null=True, blank=True)
    sub_cat = models.CharField(max_length=100, null=True, blank=True)
    images = models.ManyToManyField(Image, blank=True)
    country = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=200, null=True, blank=True)
    c_state = models.CharField(max_length=200, null=True, blank=True)
    matched_with = models.ManyToManyField("self", blank=True)
    # person = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, blank=True)
    data = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return str(self.sub_cat + " " + self.state + " " + str(self.id))

class Match(models.Model):
    image_score = models.FloatField(default=0)
    matching_score = models.FloatField(default=0)
    lost_item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='lost_item', null=True, blank=True)
    found_item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='found_item', null=True, blank=True)
    founder_phone = models.CharField(max_length=100, null=True, blank=True)
    loster_phone = models.CharField(max_length=100, null=True, blank=True)
    is_accepted = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    face_matching_data = models.JSONField(default=dict, blank=True)
    def __str__(self):
        return str(self.lost_item.id) +"lost" + " found" + str(self.found_item.id)



class Notification(models.Model):
    user  = models.ForeignKey(User, on_delete=models.CASCADE)
    is_read  = models.BooleanField(default=False)
    msg = models.CharField(max_length=255, default="None")
    data = models.JSONField(default=dict, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)




model_name = (
    # ("VGG-Face", "VGG-Face"),
    ("Facenet", "Facenet"),
    ("Facenet512", "Facenet512"),
    ("OpenFace", "OpenFace"),
    # ("DeepFace", "DeepFace"),
    ("DeepID", "DeepID"),
    ("ArcFace", "ArcFace"),
    # ("Dlib", "Dlib"),
    ("SFace", "SFace"),
)

metrics = (
    ("cosine", "cosine"),
    ("euclidean", "euclidean"),
    # ("euclidean_l2", "euclidean_l2"),
)


backends = (
    ("opencv", "opencv"),
    ("ssd", "ssd"),
    ("dlib", "dlib"),
    ("mtcnn", "mtcnn"),
    ("retinaface", "retinaface"),
    ("mediapipe", "mediapipe"),
)


class Config(models.Model):
    face_match_threshold = models.FloatField(default=0.4)
    lev_score_threshold = models.IntegerField(default=80)
    model_name = models.CharField(max_length=100, default='VGG-Face', choices=model_name)
    metrics = models.CharField(max_length=100, default='cosine', choices=metrics)
    backend = models.CharField(max_length=100, default='opencv', choices=backends)


    def save(self, *args, **kwargs):
        if not self.pk and Config.objects.exists():
        # if you'll not check for self.pk 
        # then error will also raised in update of exists model
            raise ValidationError('There is can be only one Config instance')
        return super(Config, self).save(*args, **kwargs)


    def __str__(self):
        return str(self.id)



# class Country(models.Model):
#     name = models.CharField(max_length=100, null=True, blank=True)
