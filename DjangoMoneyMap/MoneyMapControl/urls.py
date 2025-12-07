from django.urls import path
from MoneyMapControl import views

urlpatterns=[
    path('', views.login_view, name="login"),
    path('register/', views.register_view, name="register"),
    path('logout/', views.logout_view, name="logout"),
    path('forgot_password/', views.forgot_password, name="forgot_password"),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('dashboard', views.dashboard, name="dashboard"),
    path('dashboard/data/', views.dashboard_data, name='dashboard_data'),
    path('transactions/', views.transactions_view, name='transactions'),
    path('budget/', views.budget, name='budget'),
    path('investments/', views.investments, name='investments'),
    path('goals/', views.goals, name='goals'),
    path('reports/', views.reports, name='reports'),
    path('add-expense/', views.add_expense, name='add_expense'),
]