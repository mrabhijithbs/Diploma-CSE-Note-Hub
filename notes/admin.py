from django.contrib import admin
from .models import Year, Semester, Subject, Note

# --- INLINES ---
# This allows you to manage Semesters directly while editing a Year
class SemesterInline(admin.TabularInline):
    model = Semester
    extra = 2 

# --- MODEL ADMINS ---

# 1. Year Admin
@admin.register(Year)
class YearAdmin(admin.ModelAdmin):
    # list_display shows these columns in the main list
    list_display = ('name', 'number')
    # This includes the Semester form inside the Year page
    inlines = [SemesterInline]
    # Required if other models want to use autocomplete_fields for Year
    search_fields = ('name',) 

# 2. Semester Admin
@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('number', 'year')
    list_filter = ('year',)
    # Search fields are needed for autocomplete to work in SubjectAdmin
    search_fields = ('number',)

# 3. Subject Admin
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'semester')
    # Filter by Year (via Semester) then by Semester directly
    list_filter = ('semester__year', 'semester')
    search_fields = ('name',)

# 4. Note Admin
@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'uploaded_at')
    # Deep filtering: Year -> Semester -> Subject
    list_filter = ('subject__semester__year', 'subject__semester', 'subject')
    search_fields = ('title',)