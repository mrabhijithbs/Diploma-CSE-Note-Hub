from django.contrib import admin
from .models import Year, Semester, Subject, Note, Programme

# --- INLINES ---
# This allows you to manage Semesters directly while editing a Year
class SemesterInline(admin.TabularInline):
    model = Semester
    extra = 2 

# --- MODEL ADMINS ---

@admin.register(Programme)
class ProgrammeAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('code', 'name')
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
    list_display = ('name', 'programme', 'semester', 'get_year')
    # Filter by Programme, then by Year (via Semester) then by Semester directly
    list_filter = ('programme', 'semester__year', 'semester')
    search_fields = ('name', 'programme__name', 'programme__code')
    autocomplete_fields = ['programme', 'semester']

    def get_year(self, obj):
        return obj.semester.year.name if obj.semester and obj.semester.year else "N/A"
    get_year.short_description = 'Year'

# 4. Note Admin
@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_programme', 'subject', 'get_semester', 'get_year', 'is_approved', 'uploaded_at')
    # Deep filtering: Programme -> Year -> Semester -> Subject
    list_filter = ('subject__programme', 'subject__semester__year', 'subject__semester', 'is_approved')
    search_fields = ('title', 'subject__name', 'subject__programme__name', 'subject__programme__code')
    autocomplete_fields = ['subject']
    readonly_fields = ('uploaded_at', 'file_size_bytes')

    def get_programme(self, obj):
        return obj.subject.programme.name if obj.subject and obj.subject.programme else "N/A"
    get_programme.short_description = 'Programme'

    def get_semester(self, obj):
        return obj.subject.semester.number if obj.subject and obj.subject.semester else "N/A"
    get_semester.short_description = 'Semester'

    def get_year(self, obj):
        if obj.subject and obj.subject.semester and obj.subject.semester.year:
            return obj.subject.semester.year.name
        return "N/A"
    get_year.short_description = 'Year'