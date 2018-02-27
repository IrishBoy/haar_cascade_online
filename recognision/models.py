from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from datetime import datetime

def image_example_upload_directory_path(instance, filename):
    return 'algo_{0}/{1}/{2}'.format(instance.algorithm.id, instance.image_type, filename)


def algorithm_xml_upload_directory_path(instance, filename):
    if instance.id:
        return 'algo_{0}/data'.format(instance.id)
    return 'base_algo/xml/{0}'.format(filename)


def user_history_directory_path(instance, filename):
    dt = datetime.now().strftime('%Y%m%d-%H%M%S')
    return 'user_{0}/algo_history_{1}/{2}/{3}'.format(instance.user.id, instance.algorithm.name, dt, filename)


class ImageExample(models.Model):
    IMAGE_TYPES = ((i, i) for i in ('positive', 'negative'))

    file = models.ImageField(upload_to=image_example_upload_directory_path, blank=True)
    algorithm = models.ForeignKey('Algorithm', on_delete=models.CASCADE)
    image_type = models.CharField(max_length=8, choices=IMAGE_TYPES)


class Algorithm(models.Model):
    ALGO_TYPES = ((i.upper(), i) for i in ('Custom', 'Base'))
    ALGO_STATUS = ((i.upper(), i) for i in ('In progress', 'Done'))

    name = models.CharField(max_length=256)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    xml_file = models.FileField(upload_to=algorithm_xml_upload_directory_path, blank=True)
    type = models.CharField(max_length=8, choices=ALGO_TYPES)
    status = models.CharField(max_length=16, choices=ALGO_STATUS)

    def __str__(self):
        return self.name



class History(models.Model):
    HISTORY_STATUS = ((i.upper(), i) for i in ('In progress', 'Done'))

    name = models.CharField(max_length=256)
    algorithm = models.ForeignKey(Algorithm, on_delete=models.CASCADE)
    input_image = models.ImageField(upload_to=user_history_directory_path)
    output_image = models.ImageField(upload_to=user_history_directory_path, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=16, choices=HISTORY_STATUS)

    def __str__(self):
        return self.name


@receiver(pre_delete, sender=ImageExample)
def image_example_file_delete(sender, instance, **kwargs):
    instance.file.delete(False)