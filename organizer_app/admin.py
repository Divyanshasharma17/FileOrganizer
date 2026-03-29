from django.contrib import admin
from .models import UploadedFile


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display  = ('original_name', 'category', 'user', 'size', 'is_duplicate', 'uploaded_at')
    list_filter   = ('category', 'is_duplicate')
    search_fields = ('original_name', 'user__username')
    readonly_fields = ('file_hash', 'uploaded_at')
