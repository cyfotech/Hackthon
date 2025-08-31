from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import User, UserProfile, Report, Leaderboard, Reward, UserReward
from decimal import Decimal
from django.urls import path
from . import views



# ----------------------------
# Helper: get current user from cookie
# ----------------------------
def get_current_user(request):
    user_id = request.COOKIES.get('user_id')
    if user_id:
        try:
            return User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return None
    return None

# ----------------------------
# Home Page
from django.shortcuts import render
from .models import User, Report, Leaderboard

def home_view(request):
    # Get user from cookie
    user_id = request.COOKIES.get("user_id")  # cookie set during login
    logged_user = None
    if user_id:
        try:
            logged_user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            logged_user = None

    # Reports data
    recent_reports = Report.objects.filter(status='verified').order_by('-timestamp')[:5]
    total_reports = Report.objects.count()
    verified_reports = Report.objects.filter(status='verified').count()
    top_contributors = Leaderboard.objects.order_by('-points')[:3]

    # ✅ Pass logged_user into context (for base.html navbar also)
    context = {
        "logged_user": logged_user,
        "recent_reports": recent_reports,
        "total_reports": total_reports,
        "verified_reports": verified_reports,
        "top_contributors": top_contributors,
    }

    return render(request, "webapp/home.html", context)


from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.hashers import check_password
from .models import User  # Make sure this is your custom User model

def login_view(request):
    if request.method == "POST":
        username_or_email = request.POST.get("username")
        password = request.POST.get("password")

        if not username_or_email or not password:
            messages.error(request, "Please enter both username/email and password.")
            return render(request, "webapp/login.html")

        try:
            # Fetch user by email or phone
            user = User.objects.get(Q(email=username_or_email) | Q(phone=username_or_email))
            
            # Check hashed password
            if check_password(password, user.password_hash):
                response = redirect("home")  # Redirect to home page
                response.set_cookie("user_id", user.user_id)  # Optional: store user_id in cookie
                messages.success(request, "Login successful!")
                return response
            else:
                messages.error(request, "Invalid password.")
        except User.DoesNotExist:
            messages.error(request, "User not found.")

    # GET request or failed login
    return render(request, "webapp/login.html")


# ----------------------------
# Login
# ----------------------------
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import User

def signup_view(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")  # optional if you store full name only
        email = request.POST.get("email")
        location = request.POST.get("location")
        phone_number = request.POST.get("phone_number")
        community_role = request.POST.get("community_role")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # Validate passwords
        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("signup")

        # Create full name
        name = f"{first_name} {last_name}".strip()

        if not name or not email or not password:
            messages.error(request, "All required fields must be filled")
            return redirect("signup")

        # Check if email or phone already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect("signup")
        if phone_number and User.objects.filter(phone=phone_number).exists():
            messages.error(request, "Phone number already registered")
            return redirect("signup")

        # -----------------------------
        # Hash the password before saving
        password_hash = make_password(password)

        # Create user in database
        user = User.objects.create(
            name=name,
            email=email,
            phone=phone_number,
            role=community_role,
            location=location,
            password_hash=password_hash  # store hashed password
        )
        # -----------------------------

        messages.success(request, "Account created successfully! Please log in.")
        return redirect("login")

    return render(request, "webapp/signup.html")

# ----------------------------
# Signup
# ----------------------------
# webapp/views.pyp.html")

# ----------------------------
# Logout
# ----------------------------
def logout_view(request):
    response = redirect('home')
    response.delete_cookie('user_id')
    messages.success(request, 'Logged out successfully!')
    return response

# ----------------------------
# Dashboard
# ----------------------------
def dashboard(request):
    user = get_current_user(request)
    if not user:
        messages.error(request, 'Please login first.')
        return redirect('login')

    user_profile = get_object_or_404(UserProfile, user=user)
    user_reports = Report.objects.filter(user=user).order_by('-timestamp')[:5]
    leaderboard_position = Leaderboard.objects.get(user=user)
    user_rewards = UserReward.objects.filter(user=user).order_by('-earned_at')

    return render(request, 'webapp/dashboard.html', {
        'user_profile': user_profile,
        'user_reports': user_reports,
        'leaderboard_position': leaderboard_position,
        'user_rewards': user_rewards,
    })

# ----------------------------
# Submit Report
# ----------------------------
def submit_report(request):
    user = get_current_user(request)
    if not user:
        messages.error(request, 'Please login first.')
        return redirect('login')

    if request.method == 'POST':
        report_type = request.POST.get('report_type')
        description = request.POST.get('description')
        photo_url = request.POST.get('photo_url')
        geotag_lat = Decimal(request.POST.get('geotag_lat'))
        geotag_long = Decimal(request.POST.get('geotag_long'))

        report = Report.objects.create(
            user=user,
            report_type=report_type,
            description=description,
            photo_url=photo_url,
            geotag_lat=geotag_lat,
            geotag_long=geotag_long
        )

        # Award points
        user.points += 10
        user.save()

        # Update leaderboard
        leaderboard = Leaderboard.objects.get(user=user)
        leaderboard.points = user.points
        leaderboard.save()

        messages.success(request, 'Report submitted successfully! You earned 10 points.')
        return redirect('dashboard')

    return render(request, 'webapp/submit_report.html')


from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render
from .models import Report

# ----------------------------
# Reports List
# ----------------------------
def reports_list(request):
    reports = Report.objects.all().order_by('-timestamp')

    # Filters
    status_filter = request.GET.get('status')
    if status_filter:
        reports = reports.filter(status=status_filter)

    type_filter = request.GET.get('type')
    if type_filter:
        reports = reports.filter(report_type=type_filter)

    search_query = request.GET.get('search')
    if search_query:
        reports = reports.filter(
            Q(description__icontains=search_query) |
            Q(report_type__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(reports, 10)  # 10 reports per page
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'webapp/reports_list.html', {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'search_query': search_query,
    })

from django.shortcuts import render, get_object_or_404
from .models import Report

def report_detail(request, report_id):
    report = get_object_or_404(Report, report_id=report_id)
    return render(request, 'webapp/report_detail.html', {'report': report})


from django.shortcuts import render
from .models import Leaderboard

def leaderboard_view(request):
    leaderboard = Leaderboard.objects.order_by('-points')[:20]
    # Update ranks dynamically
    for idx, entry in enumerate(leaderboard, start=1):
        entry.rank = idx
        entry.save()
    return render(request, 'webapp/leaderboard.html', {'leaderboard': leaderboard})


 # if you use a helper for cookie-based login

from django.shortcuts import render
from .models import Reward, User

def rewards_view(request):
    user_id = request.COOKIES.get('user_id')
    if not user_id:
        return redirect('login')

    user = User.objects.get(user_id=user_id)
    rewards = Reward.objects.filter(is_active=True)
    return render(request, 'webapp/rewards.html', {'rewards': rewards, 'user': user})


# webapp/views.py
from django.shortcuts import render

def profile_view(request):
    # you can pass user info here later
    return render(request, 'webapp/profile.html')

from django.shortcuts import render

def about(request):
    return render(request, 'webapp/about.html')

from django.shortcuts import render

def contact(request):
    return render(request, 'webapp/contact.html')


# webapp/views.py
from django.shortcuts import render

def password_reset_view(request):
    return render(request, "webapp/password_reset.html")


from django.shortcuts import get_object_or_404, redirect
from .models import Reward, User, UserReward

def claim_reward(request, reward_id):
    user_id = request.COOKIES.get('user_id')
    if not user_id:
        return redirect('login')

    user = User.objects.get(user_id=user_id)
    
    # Correct field: reward_id
    reward = get_object_or_404(Reward, reward_id=reward_id)

    # Check if user already claimed it
    already_claimed = UserReward.objects.filter(user=user, reward=reward).exists()
    if not already_claimed:
        UserReward.objects.create(user=user, reward=reward)
        # Optionally add points deduction
        user.points -= reward.points_required
        user.save()

    return redirect('rewards')  # or wherever you want to redirect


# webapp/views.py
import os
from django.shortcuts import render, redirect
from .models import Report
from .ml_model.predict import predict_report

def submit_report(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        report_type = request.POST['report_type']
        uploaded_file = request.FILES['image']

        file_path = os.path.join('media/reports/', uploaded_file.name)
        with open(file_path, 'wb+') as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)

        predicted_type = predict_report(file_path)
        status = 'verified' if predicted_type == report_type else 'pending_review'

        Report.objects.create(
            title=title,
            description=description,
            report_type=report_type,
            predicted_report_type=predicted_type,
            status=status,
            image=uploaded_file
        )
        return redirect('reports_list')

    return render(request, 'webapp/submit_report.html')


# webapp/views.py
from django.http import JsonResponse, HttpResponseServerError
from .ml_model.predict import predict_report, get_model

def classify_view(request):
    try:
        # ensure model present (optional); or call predict_report directly
        _ = get_model()  
        # TODO: build input_data from request
        input_data = [[0.0, 1.0]]  # example
        result = predict_report(input_data).tolist()
        return JsonResponse({"ok": True, "result": result})
    except FileNotFoundError as e:
        return HttpResponseServerError(
            "ML model not found. Please place 'report_model.h5' in webapp/ml_model/."
        )


def rewards_view(request):
    user_id = request.COOKIES.get('user_id')
    if not user_id:
        return redirect('login')

    user = User.objects.get(user_id=user_id)
    rewards = Reward.objects.filter(is_active=True)
    return render(request, 'webapp/rewards.html', {'rewards': rewards, 'user': user})


# helpers.py or views.py
def get_logged_user(request):
    user_id = request.COOKIES.get("user_id")
    if user_id:
        try:
            return User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return None
    return None
