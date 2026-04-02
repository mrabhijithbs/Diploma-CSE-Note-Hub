"""
URL configuration for core project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
# Import the notes views to access approve_note directly
from notes import views as notes_views

urlpatterns = [
    # 1. Custom Admin Actions
    # Placed ABOVE the default admin/ path to prevent pattern matching issues
    path('admin/approve/<int:note_id>/', notes_views.approve_note, name='approve_note'),

    # 2. Admin Interface
    path('admin/', admin.site.urls), 
    
    # 3. Authentication System (Login, Logout, Password Management)
    path('accounts/', include('django.contrib.auth.urls')), 
    
    # 4. Notes App Routes
    path('', include('notes.urls')), 
]

print(f"DEBUGGING MEDIA ROOT: {settings.MEDIA_ROOT}")
# 5. Media File Serving
# This block handles the serving of media files (PDFs, Profile Pictures)
# specifically when DEBUG is True in your settings.py
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)