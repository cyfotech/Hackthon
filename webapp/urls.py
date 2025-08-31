from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('reports/', views.reports_list, name='reports_list'),
    path('reports/<int:report_id>/', views.report_detail, name='report_detail'),
     path('claim/<int:reward_id>/', views.claim_reward, name='claim_reward'),
    path('leaderboard/', views.leaderboard_view, name='leaderboard'),
    path("password-reset/", views.password_reset_view, name="password_reset"),
  path("submit-report/", views.submit_report, name="submit_report"),
   path('rewards/', views.rewards_view, name='rewards'),
    path('profile/', views.profile_view, name='profile'),

    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
]
