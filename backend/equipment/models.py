from django.db import models


class UploadRecord(models.Model):
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    total_count = models.IntegerField()
    avg_flowrate = models.FloatField(null=True, blank=True)
    avg_pressure = models.FloatField(null=True, blank=True)
    avg_temperature = models.FloatField(null=True, blank=True)

    type_distribution = models.JSONField()

    def __str__(self):
        return f"{self.filename} ({self.uploaded_at})"
