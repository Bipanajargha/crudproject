from django.db import models

# Create your models here.
class Registartion(models.Model):
    name = models.CharField(max_length=40)
    email = models.EmailField()
    course = models.CharField(max_length=40)
    message = models.TextField()
    isdelete = models.BooleanField(default=False)

    def __str__(self):
        return self.name