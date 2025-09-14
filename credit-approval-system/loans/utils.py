import math
from decimal import Decimal
from datetime import datetime, date
from django.db.models import Sum, Count, Q
from .models import Customer, Loan

def calculate_credit_score(customer):
    """
    Calculate credit score based on:
    1. Past Loans paid on time
    2. Number of loans taken in past
    3. Loan activity in current year
    4. Loan approved volume
    5. If sum of current loans > approved limit, credit score = 0
    """
    
    # Get all loan data in a single query to optimize performance
    loan_stats = customer.loans.aggregate(
        current_loans_sum=Sum('loan_amount', filter=Q(is_active=True)),
        total_emis=Sum('tenure'),
        paid_on_time=Sum('emis_paid_on_time'),
        loan_count=Count('loan_id'),
        current_year_loans=Count('loan_id', filter=Q(start_date__year=datetime.now().year)),
        total_loan_volume=Sum('loan_amount')
    )
    
    # Check if current loans exceed approved limit
    current_loans_sum = loan_stats['current_loans_sum'] or 0
    if current_loans_sum > customer.approved_limit:
        return 0
    
    # Initialize score
    credit_score = 0
    
    # Check if customer has any loans
    if loan_stats['loan_count'] == 0:
        return 50  # Default score for new customers
    
    # 1. Past Loans paid on time (30 points max)
    total_emis = loan_stats['total_emis'] or 0
    paid_on_time = loan_stats['paid_on_time'] or 0
    
    if total_emis > 0:
        payment_ratio = paid_on_time / total_emis
        credit_score += min(30, payment_ratio * 30)
    
    # 2. Number of loans taken (20 points max, diminishing returns)
    loan_count = loan_stats['loan_count']
    if loan_count <= 5:
        credit_score += loan_count * 4  # 4 points per loan up to 5 loans
    else:
        credit_score += 20  # Max 20 points
    
    # 3. Loan activity in current year (25 points max)
    current_year_loans = loan_stats['current_year_loans']
    if current_year_loans > 0:
        credit_score += min(25, current_year_loans * 5)
    
    # 4. Loan approved volume vs income (25 points max)
    total_loan_volume = loan_stats['total_loan_volume'] or 0
    annual_income = customer.monthly_salary * 12
    
    if annual_income > 0:
        volume_ratio = float(total_loan_volume) / float(annual_income)
        if volume_ratio <= 1:  # Good ratio
            credit_score += 25
        elif volume_ratio <= 2:  # Moderate ratio
            credit_score += 15
        elif volume_ratio <= 3:  # High ratio
            credit_score += 10
    
    return min(100, max(0, credit_score))

def calculate_monthly_installment(loan_amount, interest_rate, tenure_months):
    """
    Calculate monthly installment using compound interest formula
    EMI = P * r * (1 + r)^n / ((1 + r)^n - 1)
    Where P = Principal, r = monthly interest rate, n = tenure in months
    """
    if interest_rate == 0:
        return float(loan_amount) / tenure_months
    
    # Convert annual interest rate to monthly decimal
    monthly_rate = float(interest_rate) / (12 * 100)
    
    # Calculate EMI using compound interest formula
    power_factor = math.pow(1 + monthly_rate, tenure_months)
    emi = (float(loan_amount) * monthly_rate * power_factor) / (power_factor - 1)
    
    return round(emi, 2)

def get_corrected_interest_rate(credit_score, original_rate):
    """
    Get corrected interest rate based on credit score
    """
    if credit_score > 50:
        return float(original_rate)  # No correction needed
    elif credit_score > 30:
        return max(12.0, float(original_rate))  # Minimum 12%
    elif credit_score > 10:
        return max(16.0, float(original_rate))  # Minimum 16%
    else:
        return float(original_rate)  # Will be rejected anyway

def check_loan_eligibility(customer_id, loan_amount, interest_rate, tenure):
    """
    Check if a loan can be approved based on various criteria
    """
    try:
        customer = Customer.objects.get(customer_id=customer_id)
    except Customer.DoesNotExist:
        return {
            'approval': False,
            'message': 'Customer not found',
            'corrected_interest_rate': float(interest_rate),
            'monthly_installment': 0
        }
    
    # Calculate credit score
    credit_score = calculate_credit_score(customer)
    
    # Get corrected interest rate
    corrected_rate = get_corrected_interest_rate(credit_score, interest_rate)
    
    # Calculate monthly installment with corrected rate
    monthly_installment = calculate_monthly_installment(loan_amount, corrected_rate, tenure)
    
    # Check credit score based approval
    if credit_score <= 10:
        return {
            'approval': False,
            'message': 'Credit score too low',
            'corrected_interest_rate': corrected_rate,
            'monthly_installment': monthly_installment
        }
    
    # Check if sum of all current EMIs > 50% of monthly salary
    current_emis = customer.loans.filter(is_active=True).aggregate(
        total=Sum('monthly_repayment')
    )['total'] or 0
    
    total_emis_after_loan = float(current_emis) + monthly_installment
    max_allowed_emi = float(customer.monthly_salary) * 0.5
    
    if total_emis_after_loan > max_allowed_emi:
        return {
            'approval': False,
            'message': 'EMI exceeds 50% of monthly salary',
            'corrected_interest_rate': corrected_rate,
            'monthly_installment': monthly_installment
        }
    
    # If all checks pass
    return {
        'approval': True,
        'message': 'Loan approved',
        'corrected_interest_rate': corrected_rate,
        'monthly_installment': monthly_installment
    }