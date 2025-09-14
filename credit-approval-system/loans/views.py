from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render
from django.db import transaction
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

from .models import Customer, Loan
from .serializers import (
    CustomerRegistrationSerializer, CustomerResponseSerializer,
    LoanEligibilitySerializer, LoanEligibilityResponseSerializer,
    LoanCreationSerializer, LoanCreationResponseSerializer,
    LoanDetailSerializer, LoanListSerializer
)
from .utils import check_loan_eligibility, calculate_monthly_installment

def dashboard(request):
    """
    Dashboard view for the credit approval system
    """
    return render(request, 'loans/dashboard.html')

def api_docs(request):
    """
    API Documentation page
    """
    return render(request, 'loans/api_docs.html')

@api_view(['GET'])
def api_documentation(request):
    """
    API Documentation endpoint
    """
    api_info = {
        "message": "Credit Approval System API",
        "version": "1.0.0",
        "endpoints": {
            "register_customer": {
                "url": "/register/",
                "method": "POST",
                "description": "Register a new customer",
                "required_fields": ["first_name", "last_name", "age", "monthly_income", "phone_number"]
            },
            "check_loan_eligibility": {
                "url": "/check-eligibility/",
                "method": "POST",
                "description": "Check if a customer is eligible for a loan",
                "required_fields": ["customer_id", "loan_amount", "interest_rate", "tenure"]
            },
            "create_loan": {
                "url": "/create-loan/",
                "method": "POST",
                "description": "Create a new loan if eligible",
                "required_fields": ["customer_id", "loan_amount", "interest_rate", "tenure"]
            },
            "view_loan": {
                "url": "/view-loan/{loan_id}/",
                "method": "GET",
                "description": "View details of a specific loan"
            },
            "view_customer_loans": {
                "url": "/view-loans/{customer_id}/",
                "method": "GET",
                "description": "View all active loans for a customer"
            }
        }
    }
    return Response(api_info, status=status.HTTP_200_OK)

@api_view(['POST'])
def register_customer(request):
    """
    Register a new customer
    """
    logging.info(f"Customer registration request received: {request.data}")
    serializer = CustomerRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        try:
            customer = serializer.save()
            logging.info(f"Customer created successfully with ID: {customer.customer_id}")
            response_serializer = CustomerResponseSerializer(customer)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response(
                {'error': 'Invalid data provided', 'details': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logging.error(f"Unexpected error creating customer: {str(e)}")
            return Response(
                {'error': 'Failed to create customer', 'details': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def check_loan_eligibility_view(request):
    """
    Check loan eligibility for a customer
    """
    logging.info(f"Loan eligibility check request received: {request.data}")
    serializer = LoanEligibilitySerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data
        
        eligibility_result = check_loan_eligibility(
            data['customer_id'],
            data['loan_amount'],
            data['interest_rate'],
            data['tenure']
        )
        logging.info(f"Eligibility result for customer {data['customer_id']}: {eligibility_result['approval']}")
        
        response_data = {
            'customer_id': data['customer_id'],
            'approval': eligibility_result['approval'],
            'interest_rate': float(data['interest_rate']),
            'corrected_interest_rate': eligibility_result['corrected_interest_rate'],
            'tenure': data['tenure'],
            'monthly_installment': eligibility_result['monthly_installment']
        }
        
        response_serializer = LoanEligibilityResponseSerializer(response_data)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def create_loan(request):
    """
    Create a new loan if eligible
    """
    logging.info(f"Loan creation request received: {request.data}")
    serializer = LoanCreationSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data
        
        # Check eligibility first
        eligibility_result = check_loan_eligibility(
            data['customer_id'],
            data['loan_amount'],
            data['interest_rate'],
            data['tenure']
        )
        logging.info(f"Eligibility check for loan creation: {eligibility_result['approval']}")
        
        if not eligibility_result['approval']:
            response_data = {
                'loan_id': None,
                'customer_id': data['customer_id'],
                'loan_approved': False,
                'message': eligibility_result['message'],
                'monthly_installment': None
            }
            response_serializer = LoanCreationResponseSerializer(response_data)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        
        try:
            # Get customer
            customer = get_object_or_404(Customer, customer_id=data['customer_id'])
            
            # Use corrected interest rate
            corrected_rate = eligibility_result['corrected_interest_rate']
            monthly_installment = eligibility_result['monthly_installment']
            
            # Calculate loan dates
            start_date = datetime.now().date()
            end_date = start_date + relativedelta(months=data['tenure'])
            
            # Use transaction to ensure data consistency
            with transaction.atomic():
                # Create loan
                loan = Loan.objects.create(
                    customer=customer,
                    loan_amount=data['loan_amount'],
                    tenure=data['tenure'],
                    interest_rate=corrected_rate,
                    monthly_repayment=monthly_installment,
                    start_date=start_date,
                    end_date=end_date,
                    is_active=True
                )
                
                # Update customer's current debt
                customer.current_debt += data['loan_amount']
                customer.save()
            
            response_data = {
                'loan_id': loan.loan_id,
                'customer_id': data['customer_id'],
                'loan_approved': True,
                'message': 'Loan approved successfully',
                'monthly_installment': monthly_installment
            }
            
            logging.info(f"Loan created successfully with ID: {loan.loan_id} for customer: {data['customer_id']}")
            response_serializer = LoanCreationResponseSerializer(response_data)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except Customer.DoesNotExist:
            return Response(
                {'error': 'Customer not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response(
                {'error': 'Invalid data provided', 'details': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logging.error(f"Unexpected error creating loan: {str(e)}")
            return Response(
                {'error': 'Failed to create loan', 'details': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def view_loan(request, loan_id):
    """
    View details of a specific loan
    """
    try:
        loan = get_object_or_404(Loan, loan_id=loan_id)
        serializer = LoanDetailSerializer(loan)
        
        # Adjust the response to match the required format
        data = serializer.data
        data['monthly_installment'] = data.pop('monthly_repayment')
        
        return Response(data, status=status.HTTP_200_OK)
    except Loan.DoesNotExist:
        return Response(
            {'error': 'Loan not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logging.error(f"Unexpected error viewing loan {loan_id}: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def view_customer_loans(request, customer_id):
    """
    View all current loans for a customer
    """
    try:
        customer = get_object_or_404(Customer, customer_id=customer_id)
        loans = customer.loans.filter(is_active=True).select_related('customer')
        serializer = LoanListSerializer(loans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Customer.DoesNotExist:
        return Response(
            {'error': 'Customer not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logging.error(f"Unexpected error viewing customer loans {customer_id}: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )