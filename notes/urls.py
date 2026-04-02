# notes/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # 1. The Home Page (Root URL)
    path('', views.home, name='home'), 
    
    # 2. Subject List View
    path('semester/<int:semester_number>/', views.subject_list, name='subject_list'),
    
    # 3. Note List View
    path('subject/<int:subject_id>/', views.note_list, name='note_list'),
    
    # 4. Search View
    path('search/', views.search, name='search'),
    
    # 5. User Registration
    path('signup/', views.signup, name='signup'),

    # 6. Admin Dashboard
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # 7. Approve Note 
    # This combines your request with your existing admin structure
    path('approve-note/<int:note_id>/', views.approve_note, name='approve_note'),

    # 8. Delete Note
    path('admin/delete/<int:note_id>/', views.delete_note, name='delete_note'),

    # 9. Profile View
    path('profile/', views.profile, name='profile'),
    
    # 10. Ask AI Routes
    path('ask-ai/', views.ask_ai_view, name='ask_ai'),
    path('api/ask-ai/', views.ask_ai_api, name='ask_ai_api'),
]