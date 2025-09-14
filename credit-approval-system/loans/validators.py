import re
from decimal import Decimal
from django.core.exceptions import ValidationError


def validate_phone_number(phone_number):
    """
    Validate phone number format
    """
    # Remove all non-digit characters
    cleaned = re.sub(r'\D', '', phone_number)
    
    # Check if it's a valid length (10-15 digits)
    if not (10 <= len(cleaned) <= 15):
        raise ValidationError('Phone number must be between 10 and 15 digits')
    
    # Check if it contains only digits
    if not cleaned.isdigit():
        raise ValidationError('Phone number must contain only digits')
    
    return cleaned


def validate_loan_amount(amount):
    """
    Validate loan amount
    """
    if amount <= 0:
        raise ValidationError('Loan amount must be greater than 0')
    
    if amount > 10000000:  # 1 crore limit
        raise ValidationError('Loan amount cannot exceed 1 crore')
    
    return amount


def validate_interest_rate(rate):
    """
    Validate interest rate
    """
    if rate < 0:
        raise ValidationError('Interest rate cannot be negative')
    
    if rate > 50:  # 50% max interest rate
        raise ValidationError('Interest rate cannot exceed 50%')
    
    return rate


def validate_tenure(tenure):
    """
    Validate loan tenure
    """
    if tenure < 1:
        raise ValidationError('Tenure must be at least 1 month')
    
    if tenure > 360:  # 30 years max
        raise ValidationError('Tenure cannot exceed 360 months')
    
    return tenure


def validate_monthly_income(income):
    """
    Validate monthly income
    """
    if income <= 0:
        raise ValidationError('Monthly income must be greater than 0')
    
    if income > 1000000:  # 10 lakhs max
        raise ValidationError('Monthly income cannot exceed 10 lakhs')
    
    return income


def validate_age(age):
    """
    Validate customer age
    """
    if age < 18:
        raise ValidationError('Age must be at least 18 years')
    
    if age > 100:
        raise ValidationError('Age cannot exceed 100 years')
    
    return age


def validate_name(name, field_name):
    """
    Validate name fields
    """
    if not name or not name.strip():
        raise ValidationError(f'{field_name} cannot be empty')
    
    if len(name.strip()) < 2:
        raise ValidationError(f'{field_name} must be at least 2 characters long')
    
    if len(name.strip()) > 100:
        raise ValidationError(f'{field_name} cannot exceed 100 characters')
    
    # Check for valid characters (letters, spaces, hyphens, apostrophes)
    if not re.match(r"^[a-zA-Z\s\-']+$", name.strip()):
        raise ValidationError(f'{field_name} can only contain letters, spaces, hyphens, and apostrophes')
    
    return name.strip()
