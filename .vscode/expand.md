# Multiple Programmes Support Implementation Plan

This plan details how we will upgrade the DiplomaNote Hub from supporting a single programme (DCSE) to a multi-programme architecture, accommodating students from DAI, DEEE, DME, and DHMCT. 

## User Review Required
> [!IMPORTANT]
> This upgrade requires a small database schema update and changes how users navigate the site from the moment they arrive. Please review the proposed user flow to ensure it matches your vision.

## Proposed Changes

### Database Layer (Models)
We will introduce a new top-level database table to categorize all notes and subjects.

#### [MODIFY] `notes/models.py`
- **Add `Programme` Model**: We will create a model with `name` (e.g., "Artificial Intelligence") and `code` (e.g., "DAI", "DCSE").
- **Update `Subject` Model**: We will add a `ForeignKey` linking every subject to a specific `Programme`. This allows each department to have its distinct set of subjects per semester without collision.

### Routing Layer (URLs)
We are fundamentally changing the entry point structure.

#### [MODIFY] `notes/urls.py`
- We will update the root path `''` to show the new Programme selection view.
- `[NEW]` We will add `path('programme/<str:prog_code>/')` which replaces the current home screen's functionality (showing the 1st/2nd/3rd year semesters for a *specific* programme).
- We will modify the subject list route to include the programme context: `path('programme/<str:prog_code>/semester/<int:semester_number>/')`.

### View Business Logic (Views)
#### [MODIFY] `notes/views.py`
- **`home` View**: Will now fetch all available `Programme` records and pass them to the template.
- **`[NEW] programme_detail` View**: Accepts `prog_code`. It will act as the "portal" for a specific department (which is what the old `home` view did, but dynamically for any department).
- **`subject_list` View**: Will evaluate both `prog_code` and `semester_number` to only show subjects that belong to the user's specific programme.

### Presentation Layer (Templates)
We will create a stunning new entry point for the website.

#### [MODIFY] `notes/templates/notes/home.html`
- **Repurposed:** This file will become the absolute root frontend. It will feature a grid of premium-designed cards representing each Diploma Programme (DCSE, DAI, DEEE, DME, DHMCT). Users will select their department here first.

#### [NEW] `notes/templates/notes/programme_detail.html`
- This will be a refactored version of the *current* `home.html`.
- It will dynamically display the department's title (e.g., `<h1 class="display-4 fw-extrabold text-dark mb-3 reveal">{{ programme.code }} notes HUB</h1>`) instead of being hardcoded to DCSE. 

#### [MODIFY] `notes/templates/notes/base.html` & `subjects.html`
- Adjust breadcrumbs and "Back" buttons so users correctly navigate back to their chosen programme instead of the top-level programme selection page.
- Adding a quick "Change Programme" dropdown/link in the navbar.

### Administration
#### [MODIFY] `notes/admin.py` (if currently used)
- Register the new `Programme` model so you can seamlessly add new ones in the future.

---

## Open Questions

> [!WARNING]
> 1. Do you have any existing Subjects in your database that currently belong to DCSE? When we add the `Programme` model, we will need to bulk-assign existing subjects to DCSE.
> 2. Should students be "locked" into a programme by setting their Programme in their `Profile`, or should they continue logging in and browsing whichever programme they want freely? Setting it freely is easier and matches current flow.

## Verification Plan

### Manual Verification
1. Open the home page (`/`) — Ensure the screen lists DCSE, DAI, DEEE, DME, DHMCT as clickable vibrant cards.
2. Click "DAI" — Ensure the URL changes to `/programme/DAI/` and shows the 6 semester layout with "DAI notes HUB" as the title.
3. Click "Semester 1" under DAI — Ensure it goes to `/programme/DAI/semester/1/` and only loads Subjects bound to the DAI programme.
4. Perform an admin upload of a Note inside a DAI Subject, then verify it's only visible there.
