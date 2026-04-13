from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import Q, Count
# Added Profile, Complaint to imports
from .models import Year, Semester, Subject, Note, Profile, Complaint, Notification, Programme
from .forms import UserUpdateForm, ProfileUpdateForm, ComplaintForm
import os
import json
import time
import google.generativeai as genai
from huggingface_hub import InferenceClient
from django.http import JsonResponse

# 1. The Home View (Programme Selection)
def home(request):
    programmes = Programme.objects.all().order_by('code')
    
    context = {
        'programmes': programmes,
    }
    return render(request, 'notes/home.html', context)

# 1.5 Programme Detail View (Portal for a specific department)
def programme_detail(request, prog_code):
    programme = get_object_or_404(Programme, code=prog_code)
    
    query = request.GET.get('q')
    results = []
    
    if query:
        results = Note.objects.filter(
            Q(programme=programme) | Q(subject__programme=programme),
            Q(title__icontains=query) | Q(subject__name__icontains=query)
        ).distinct()

    years = Year.objects.all().prefetch_related('semesters').order_by('number')
    recent_notes = Note.objects.filter(
        Q(programme=programme) | Q(subject__programme=programme),
        is_approved=True
    ).order_by('-uploaded_at')[:10]

    context = {
        'programme': programme,
        'years': years,
        'recent_notes': recent_notes,
        'query': query,
        'results': results,
    }
    return render(request, 'notes/programme_detail.html', context)

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
def subject_list(request, prog_code, semester_number):
    programme = get_object_or_404(Programme, code=prog_code)
    semester = get_object_or_404(Semester, number=semester_number)
    subjects = Subject.objects.filter(semester=semester, programme=programme).annotate(
        note_count=Count('notes')
    )
    
    return render(request, 'notes/subjects.html', {
        'programme': programme,
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

# 4.5 The Note Detail View (PDF Viewer)
@login_required
def note_detail(request, note_id):
    note = get_object_or_404(Note, id=note_id, is_approved=True)
    return render(request, 'notes/note_detail.html', {
        'note': note
    })

# 5. Dedicated Search View
@login_required
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
    complaints = Complaint.objects.all().order_by('-created_at')
    
    context = {
        'total_notes': total_notes,
        'total_subjects': total_subjects,
        'recent_uploads': recent_uploads,
        'pending_notes': pending_notes,
        'complaints': complaints,
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
@require_POST
@user_passes_test(lambda u: u.is_superuser)
def delete_note(request, note_id):
    note = get_object_or_404(Note, id=note_id)
    title = note.title
    note.delete()
    messages.warning(request, f"Note '{title}' has been deleted.")
    return redirect('admin_dashboard')

# 10. Complaint Submit View
@login_required
def submit_complaint(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.user = request.user
            complaint.save()
            messages.success(request, "Your complaint has been submitted successfully.")
            return redirect('home')
    else:
        form = ComplaintForm()
    return render(request, 'notes/submit_complaint.html', {'form': form})

# 11. Admin Action: Resolve Complaint
@require_POST
@user_passes_test(lambda u: u.is_superuser)
def resolve_complaint(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)
    complaint.is_resolved = True
    complaint.save()
    # Create an in-app notification for the user who filed the complaint
    Notification.objects.create(
        user=complaint.user,
        message=f'Your complaint "{complaint.subject}" has been reviewed and resolved by the admin. Thank you for your feedback!'
    )
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
        
    messages.success(request, f"Complaint '{complaint.subject}' resolved. User notified.")
    return redirect('admin_dashboard')

# 12. Admin Action: Delete Complaint
@require_POST
@user_passes_test(lambda u: u.is_superuser)
def delete_complaint(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)
    subject = complaint.subject
    complaint.delete()
    messages.warning(request, f"Complaint '{subject}' has been deleted.")
    return redirect('admin_dashboard')

# 13. Mark Notifications as Read
@login_required
def mark_notifications_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return redirect(request.META.get('HTTP_REFERER', 'home'))

# 14. Get Unread Notifications (AJAX Polling Endpoint)
@login_required
def get_unread_notifications(request):
    """Returns unread notifications as JSON for frontend polling."""
    unread = request.user.notifications.filter(is_read=False).order_by('-created_at')
    notifications_data = [
        {
            'id': n.id,
            'message': n.message,
            'created_at': n.created_at.strftime('%d %b %Y, %I:%M %p'),
        }
        for n in unread
    ]
    return JsonResponse({
        'count': unread.count(),
        'notifications': notifications_data,
    })

# 12. Ask AI View
@login_required
def ask_ai_view(request):
    return render(request, 'notes/ask_ai.html')

# 13. Ask AI API Endpoint
@login_required
def ask_ai_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            prompt = data.get("prompt", "")
            if not prompt:
                return JsonResponse({"error": "Empty prompt"}, status=400)
            
            # Inject context for the AI
            sys_prompt = f"You are a helpful AI assistant for Diploma students at MGCE Polytechnic. Answer this question clearly and concisely: {prompt}"
            
            # Try Gemini first, failover to Hugging Face
            response_text = get_ai_response(sys_prompt)
            return JsonResponse({"response": response_text})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
            
    return JsonResponse({"error": "Invalid request"}, status=400)


# --- AI Helper Functions (Failover Logic) ---

def call_hf_model(prompt, model_id="google/gemma-2-9b-it", retries=2):
    """Calls Hugging Face Inference API with cold-start retry logic."""
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        return "Hugging Face API token is not configured."
    
    client = InferenceClient(token=hf_token)
    
    for attempt in range(retries + 1):
        try:
            response = client.chat_completion(
                model=model_id,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            if "503" in str(e) and attempt < retries:
                # Model is loading (cold start), wait and retry
                time.sleep(10)
                continue
            else:
                return f"Hugging Face error: {e}"
    
    return "Sorry, the AI model is currently unavailable. Please try again later."


def get_ai_response(prompt):
    """Tries Gemini first. If quota is exceeded (429), switches to Hugging Face."""
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            # No Gemini key, go straight to Hugging Face
            return call_hf_model(prompt)
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        if "429" in str(e) or "quota" in str(e).lower():
            # Gemini limit hit, switch to Hugging Face
            return call_hf_model(prompt)
        return f"An error occurred: {e}"