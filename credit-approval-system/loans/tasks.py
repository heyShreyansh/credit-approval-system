import pandas as pd
import django_rq
from django.conf import settings
from datetime import datetime
from .models import Customer, Loan

def ingest_customer_data():
    """
    Background task to ingest customer data from Excel file
    """
    try:
        # Read customer data
        df = pd.read_excel('customer_data.xlsx')
        
        customers_created = 0
        for _, row in df.iterrows():
            try:
                # Calculate approved limit (36 * monthly_salary rounded to nearest lakh)
                approved_limit = round((36 * row['monthly_salary']) / 100000) * 100000
                
                customer, created = Customer.objects.get_or_create(
                    customer_id=row['customer_id'],
                    defaults={
                        'first_name': row['first_name'],
                        'last_name': row['last_name'],
                        'phone_number': str(row['phone_number']),
                        'monthly_salary': row['monthly_salary'],
                        'approved_limit': approved_limit,
                        'current_debt': row.get('current_debt', 0),
                        'age': row.get('age', 25)  # Use age from Excel or default to 25
                    }
                )
                if created:
                    customers_created += 1
            except Exception as e:
                print(f"Error creating customer {row.get('customer_id', 'unknown')}: {e}")
                continue
        
        print(f"Successfully created {customers_created} customers")
        return f"Created {customers_created} customers"
        
    except Exception as e:
        print(f"Error ingesting customer data: {e}")
        return f"Error: {e}"

def ingest_loan_data():
    """
    Background task to ingest loan data from Excel file
    """
    try:
        # Read loan data
        df = pd.read_excel('loan_data.xlsx')
        
        loans_created = 0
        for _, row in df.iterrows():
            try:
                # Get customer
                customer = Customer.objects.get(customer_id=row['customer_id'])
                
                # Parse dates
                start_date = pd.to_datetime(row['start_date']).date()
                end_date = pd.to_datetime(row['end_date']).date()
                
                # Determine if loan is still active
                is_active = end_date > datetime.now().date()
                
                loan, created = Loan.objects.get_or_create(
                    loan_id=row['loan_id'],
                    defaults={
                        'customer': customer,
                        'loan_amount': row['loan_amount'],
                        'tenure': row['tenure'],
                        'interest_rate': row['interest_rate'],
                        'monthly_repayment': row['monthly_repayment'],
                        'emis_paid_on_time': row['EMIs_paid_on_time'],
                        'start_date': start_date,
                        'end_date': end_date,
                        'is_active': is_active
                    }
                )
                if created:
                    loans_created += 1
                    
            except Customer.DoesNotExist:
                print(f"Customer {row.get('customer_id', 'unknown')} not found for loan {row.get('loan_id', 'unknown')}")
                continue
            except Exception as e:
                print(f"Error creating loan {row.get('loan_id', 'unknown')}: {e}")
                continue
        
        print(f"Successfully created {loans_created} loans")
        return f"Created {loans_created} loans"
        
    except Exception as e:
        print(f"Error ingesting loan data: {e}")
        return f"Error: {e}"

def ingest_all_data():
    """
    Ingest both customer and loan data
    """
    customer_result = ingest_customer_data()
    loan_result = ingest_loan_data()
    
    return {
        'customers': customer_result,
        'loans': loan_result
    }