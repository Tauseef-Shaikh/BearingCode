# -*- coding: utf-8 -*-
"""
Created on Wed Sep  6 14:10:25 2023

@author: Administrator
"""

from django import forms
from .models import Entry

class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ['name', 'location', 'pin']      