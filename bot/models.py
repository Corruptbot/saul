from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Account(models.Model):
    fb_user = models.IntegerField(verbose_name='Facebook id',primary_key=True) 
    state = models.IntegerField(verbose_name='Estado',default=0)

    def __str__(self):
        return self.fb_user

    def setState(self,state):
    	self.state = state
    	self.save()
                        
class PoliciaTransito(models.Model):
	p_id = models.IntegerField(verbose_name='Matricula',primary_key=True) 
	name = models.CharField(max_length=40,verbose_name='Pais') 
