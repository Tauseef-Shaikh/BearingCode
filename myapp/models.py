from django.db import models

class Entry(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    pin = models.CharField(max_length=10)
    datetime = models.DateTimeField(auto_now_add=True)
    
    #optionType = 
    #bearingCode = models.CharField(max_length=100)
    #amount = models.IntegerField()
    #datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name