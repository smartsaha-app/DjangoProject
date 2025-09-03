from django.db import models
# -------------------------------
# Messages
# -------------------------------
class Message(models.Model):
    id = models.BigAutoField(primary_key=True)
    sender = models.ForeignKey('SmartSaha.User', on_delete=models.SET_NULL, null=True, related_name="sent_messages")
    receiver = models.ForeignKey('SmartSaha.User', on_delete=models.SET_NULL, null=True, related_name="received_messages")
    content = models.TextField()
    post = models.ForeignKey('SmartSaha.Post', on_delete=models.SET_NULL, null=True, blank=True)
    subject = models.CharField(max_length=255, default='No Subject')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} - {self.receiver.username} - {self.subject} "

