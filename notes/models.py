import os
from django.db import models
from django.contrib.auth.models import User

# 0. Programme Model
class Programme(models.Model):
    name = models.CharField(max_length=100) # e.g., "Computer Science"
    code = models.CharField(max_length=20, unique=True) # e.g., "DCSE"

    def __str__(self):
        return f"{self.code} - {self.name}"

# 1. User Profile Model
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')

    def __str__(self):
        return f'{self.user.username} Profile'

    @property
    def get_avatar_url(self):
        url = self.image.url
        if 'default.jpg' in url and 'raw/upload' in url:
            return url.replace('raw/upload', 'image/upload')
        return url

import re

# 2. Function to determine the folder structure for uploaded PDFs
def get_upload_path(instance, filename):
    # Sanitize subject name to prevent Cloudinary Invalid Signature errors with quotes/spaces
    safe_subject_name = re.sub(r'[^A-Za-z0-9_\-\.]', '_', instance.subject.name)
    # Organizes files like: Semester_4/OOP_S/chapter1.pdf
    return f'Semester_{instance.subject.semester.number}/{safe_subject_name}/{filename}'

# 3. Year Model
class Year(models.Model):
    name = models.CharField(max_length=50) # e.g., "First Year"
    number = models.PositiveIntegerField(unique=True) # e.g., 1, 2, 3

    def __str__(self):
        return self.name

# 4. Semester Model
class Semester(models.Model):
    year = models.ForeignKey(Year, on_delete=models.CASCADE, related_name='semesters', null=True, blank=True)
    number = models.IntegerField(unique=True) # e.g., 1, 2, 3...

    def __str__(self):
        return f"Semester {self.number}"

# 5. Subject Model
class Subject(models.Model):
    name = models.CharField(max_length=200)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='subjects')
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE, related_name='subjects', null=True, blank=True)

    def __str__(self):
        code = self.programme.code if self.programme else "Gen"
        return f"{self.name} ({code}-S{self.semester.number})"
        

# 6. Note Model
class Note(models.Model):
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to=get_upload_path) 
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE, related_name='direct_notes', null=True, blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='notes')
    
    # Admin/Dashboard Fields
    is_approved = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_size_bytes = models.PositiveIntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.file and not self.file_size_bytes:
            try:
                self.file_size_bytes = self.file.size
            except Exception:
                pass
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def get_file_size(self):
        if self.file_size_bytes:
            size_mb = self.file_size_bytes / (1024 * 1024)
            return f"{round(size_mb, 2)} MB"
        return "Unknown"

# 7. Complaint Model
class Complaint(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='complaints')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Complaint by {self.user.username}: {self.subject}"

# 8. Notification Model
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:50]}"