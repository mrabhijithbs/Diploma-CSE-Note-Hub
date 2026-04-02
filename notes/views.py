from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import Q, Count
# Added Profile to imports
from .models import Year, Semester, Subject, Note, Profile
from .forms import UserUpdateForm, ProfileUpdateForm
import os
import json
import google.generativeai as genai
from django.http import JsonResponse

# 1. The Home View
def home(request):
    query = request.GET.get('q')
    results = []
    
    if query:
        results = Note.objects.filter(
            Q(title__icontains=query) | Q(subject__name__icontains=query)
        ).distinct()

    years = Year.objects.all().prefetch_related('semesters').order_by('number')
    recent_notes = Note.objects.filter(is_approved=True).order_by('-uploaded_at')[:10]

    context = {
        'years': years,
        'recent_notes': recent_notes,
        'query': query,
        'results': results,
    }
    return render(request, 'notes/home.html', context)

# 2. User Profile View (Safely handles missing profiles)
@login_required
def profile(request):
    # This line ensures a profile exists before we try to use it
    user_profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # request.FILES is the most important part for pictures!
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=user_profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile') 
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=user_profile)

    return render(request, 'notes/profile.html', {
        'u_form': u_form,
        'p_form': p_form
    })

# 3. The Subject List View
@login_required
def subject_list(request, semester_number):
    semester = get_object_or_404(Semester, number=semester_number)
    subjects = Subject.objects.filter(semester=semester).annotate(
        note_count=Count('notes')
    )
    
    return render(request, 'notes/subjects.html', {
        'semester': semester,
        'subjects': subjects
    })

# 4. The Note List View
@login_required
def note_list(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    notes = Note.objects.filter(subject=subject, is_approved=True).order_by('-uploaded_at')
    
    return render(request, 'notes/notes.html', {
        'subject': subject,
        'notes': notes
    })

# 5. Dedicated Search View
def search(request):
    query = request.GET.get('q')
    results = Note.objects.filter(title__icontains=query, is_approved=True) if query else []
    return render(request, 'notes/search_results.html', {'results': results, 'query': query})

# 6. User Registration View
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

# 7. Admin Dashboard (Superuser Only)
@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    total_notes = Note.objects.count()
    total_subjects = Subject.objects.count()
    recent_uploads = Note.objects.all().order_by('-uploaded_at')[:5]
    pending_notes = Note.objects.filter(is_approved=False).order_by('-uploaded_at')
    
    context = {
        'total_notes': total_notes,
        'total_subjects': total_subjects,
        'recent_uploads': recent_uploads,
        'pending_notes': pending_notes,
    }
    return render(request, 'notes/admin_dashboard.html', context)

# 8. Admin Action: Approve Note
@user_passes_test(lambda u: u.is_superuser)
def approve_note(request, note_id):
    note = get_object_or_404(Note, id=note_id)
    note.is_approved = True
    note.save()
    messages.success(request, f"Note '{note.title}' has been approved.")
    return redirect('admin_dashboard')

# 9. Admin Action: Delete Note
@user_passes_test(lambda u: u.is_superuser)
def delete_note(request, note_id):
    note = get_object_or_404(Note, id=note_id)
    title = note.title
    note.delete()
    messages.warning(request, f"Note '{title}' has been deleted.")
    return redirect('admin_dashboard')

# 10. Ask AI View
@login_required
def ask_ai_view(request):
    return render(request, 'notes/ask_ai.html')

# 11. Ask AI API Endpoint
@login_required
def ask_ai_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            prompt = data.get("prompt", "")
            if not prompt:
                return JsonResponse({"error": "Empty prompt"}, status=400)
            
            # Use environment variable for the API key
            # Since the API key needs to be configured once, we configure it here
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                return JsonResponse({"error": "Gemini API key is not configured in .env"}, status=500)
                
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # Inject context
            sys_prompt = f"You are a helpful AI assistant for Diploma students at MGCE Polytechnic. Answer this question clearly and concisely: {prompt}"
            response = model.generate_content(sys_prompt)
            return JsonResponse({"response": response.text})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
            
    return JsonResponse({"error": "Invalid request"}, status=400)