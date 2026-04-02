import os
from django.db import models
from django.contrib.auth.models import User

# 1. User Profile Model
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')

    def __str__(self):
        return f'{self.user.username} Profile'

# 2. Function to determine the folder structure for uploaded PDFs
def get_upload_path(instance, filename):
    # Organizes files like: media/Semester_4/DBMS/chapter1.pdf
    return f'Semester_{instance.subject.semester.number}/{instance.subject.name}/{filename}'

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

    def __str__(self):
        return f"{self.name} (S{self.semester.number})"
        

# 6. Note Model
class Note(models.Model):
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to=get_upload_path) 
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='notes')
    
    # Admin/Dashboard Fields
    is_approved = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    # Helper method to show file size in the template
    def get_file_size(self):
        try:
            if self.file and os.path.exists(self.file.path):
                size = self.file.size / (1024 * 1024)  # Convert bytes to MB
                return f"{round(size, 2)} MB"
        except Exception:
            pass
        return "Unknown"