from django import forms
from .models import Message, Thread, MessageAttachment



class MessageReplyForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = {'content'}

