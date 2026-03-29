from django.db import models
from django.contrib.auth.models import User


class UploadedFile(models.Model):
    """Tracks every file uploaded by a user."""

    CATEGORY_CHOICES = [
        ('Images', 'Images'),
        ('Videos', 'Videos'),
        ('Documents', 'Documents'),
        ('Others', 'Others'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='files')
    original_name = models.CharField(max_length=255)   # name as uploaded
    saved_name = models.CharField(max_length=255)       # name on disk (may differ if duplicate)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    file_hash = models.CharField(max_length=64)         # SHA-256 hash for duplicate detection
    file_path = models.CharField(max_length=500)        # relative path inside MEDIA_ROOT
    size = models.PositiveIntegerField(default=0)       # bytes
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_duplicate = models.BooleanField(default=False)   # True if a hash match was found

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.original_name} ({self.category})"
