from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('api-docs/', views.api_docs, name='api_docs'),
    path('api/', views.api_documentation, name='api_documentation'),
    path('register/', views.register_customer, name='register_customer'),
    path('check-eligibility/', views.check_loan_eligibility_view, name='check_eligibility'),
    path('create-loan/', views.create_loan, name='create_loan'),
    path('view-loan/<int:loan_id>/', views.view_loan, name='view_loan'),
    path('view-loans/<int:customer_id>/', views.view_customer_loans, name='view_customer_loans'),
]