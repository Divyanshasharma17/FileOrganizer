import os
import hashlib

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect, get_object_or_404

from .forms import MultiFileUploadForm, SignUpForm
from .models import UploadedFile


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Map file extensions → category folder name
CATEGORY_MAP = {
    'Images':    {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.tiff'},
    'Videos':    {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'},
    'Documents': {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
                  '.txt', '.csv', '.odt', '.rtf', '.md'},
}


def get_category(filename: str) -> str:
    """Return the category name based on the file extension."""
    ext = os.path.splitext(filename)[1].lower()
    for category, extensions in CATEGORY_MAP.items():
        if ext in extensions:
            return category
    return 'Others'


def compute_hash(file_obj) -> str:
    """Compute SHA-256 hash of an in-memory uploaded file."""
    sha256 = hashlib.sha256()
    # Read in 64 KB chunks to handle large files without loading all into RAM
    for chunk in file_obj.chunks(chunk_size=65536):
        sha256.update(chunk)
    file_obj.seek(0)   # reset pointer so Django can save it afterwards
    return sha256.hexdigest()


def unique_filename(directory: str, filename: str) -> str:
    """
    If `filename` already exists in `directory`, append a counter suffix.
    e.g. report.pdf → report_1.pdf → report_2.pdf …
    """
    base, ext = os.path.splitext(filename)
    candidate = filename
    counter = 1
    while os.path.exists(os.path.join(directory, candidate)):
        candidate = f"{base}_{counter}{ext}"
        counter += 1
    return candidate


# ---------------------------------------------------------------------------
# Authentication views
# ---------------------------------------------------------------------------

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = SignUpForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f'Welcome, {user.username}! Your account has been created.')
        return redirect('home')

    return render(request, 'organizer_app/signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, f'Welcome back, {user.username}!')
        return redirect('home')

    return render(request, 'organizer_app/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


# ---------------------------------------------------------------------------
# Main app views
# ---------------------------------------------------------------------------

@login_required
def home(request):
    """
    GET  → show upload form + list of user's files
    POST → process uploaded files
    """
    form = MultiFileUploadForm()
    uploaded_results = []   # info shown in the success banner

    if request.method == 'POST':
        form = MultiFileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # request.FILES.getlist('files') gives us all selected files
            raw_files = request.FILES.getlist('files')

            for raw_file in raw_files:
                category = get_category(raw_file.name)
                file_hash = compute_hash(raw_file)

                # --- Duplicate detection ---
                existing = UploadedFile.objects.filter(
                    user=request.user,
                    file_hash=file_hash
                ).first()

                if existing:
                    # Same content already stored — skip saving to disk
                    uploaded_results.append({
                        'name': raw_file.name,
                        'status': 'duplicate',
                        'category': category,
                    })
                    continue

                # --- Determine save directory ---
                # e.g. media/Images/, media/Documents/ …
                save_dir = os.path.join(settings.MEDIA_ROOT, category)
                os.makedirs(save_dir, exist_ok=True)

                # --- Avoid overwriting existing files with same name ---
                safe_name = unique_filename(save_dir, raw_file.name)

                # --- Save file using FileSystemStorage ---
                fs = FileSystemStorage(location=save_dir)
                fs.save(safe_name, raw_file)

                # Relative path stored in DB (for building URLs later)
                relative_path = os.path.join(category, safe_name)

                # --- Persist metadata ---
                UploadedFile.objects.create(
                    user=request.user,
                    original_name=raw_file.name,
                    saved_name=safe_name,
                    category=category,
                    file_hash=file_hash,
                    file_path=relative_path,
                    size=raw_file.size,
                )

                uploaded_results.append({
                    'name': raw_file.name,
                    'saved_as': safe_name,
                    'status': 'saved',
                    'category': category,
                })

            if uploaded_results:
                saved_count = sum(1 for r in uploaded_results if r['status'] == 'saved')
                dup_count   = sum(1 for r in uploaded_results if r['status'] == 'duplicate')
                msg = f'{saved_count} file(s) uploaded successfully.'
                if dup_count:
                    msg += f' {dup_count} duplicate(s) skipped.'
                messages.success(request, msg)

    # Fetch all files for this user, grouped by category
    user_files = UploadedFile.objects.filter(user=request.user)

    context = {
        'form': form,
        'user_files': user_files,
        'uploaded_results': uploaded_results,
        'media_url': settings.MEDIA_URL,
    }
    return render(request, 'organizer_app/home.html', context)


@login_required
def delete_file(request, file_id):
    """Delete a file record and its physical file from disk."""
    file_obj = get_object_or_404(UploadedFile, id=file_id, user=request.user)

    # Remove from disk
    full_path = os.path.join(settings.MEDIA_ROOT, file_obj.file_path)
    if os.path.exists(full_path):
        os.remove(full_path)

    file_obj.delete()
    messages.success(request, f'"{file_obj.original_name}" has been deleted.')
    return redirect('home')
