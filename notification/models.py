

class MessageAttachment(models.Model):
    name = models.CharField(max_length=255)  # The name of the uploaded file
    file = models.FileField()
    message = models.ForeignKey("Message")
