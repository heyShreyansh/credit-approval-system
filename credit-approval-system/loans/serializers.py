from rest_framework import serializers
from django.core.exceptions import ValidationError
from .models import Customer, Loan
from .validators import (
    validate_phone_number, validate_loan_amount, validate_interest_rate,
    validate_tenure, validate_monthly_income, validate_age, validate_name
)

class CustomerRegistrationSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    age = serializers.IntegerField(min_value=18, max_value=100)
    monthly_income = serializers.DecimalField(max_digits=10, decimal_places=2)
    phone_number = serializers.CharField(max_length=15)
    
    def validate_first_name(self, value):
        return validate_name(value, 'First name')
    
    def validate_last_name(self, value):
        return validate_name(value, 'Last name')
    
    def validate_age(self, value):
        return validate_age(value)
    
    def validate_monthly_income(self, value):
        return validate_monthly_income(value)
    
    def validate_phone_number(self, value):
        return validate_phone_number(value)

    def create(self, validated_data):
        # Calculate approved limit: 36 * monthly_salary (rounded to nearest lakh)
        monthly_income = validated_data['monthly_income']
        approved_limit = round((36 * monthly_income) / 100000) * 100000
        
        customer = Customer.objects.create(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            age=validated_data['age'],
            monthly_salary=monthly_income,
            phone_number=validated_data['phone_number'],
            approved_limit=approved_limit
        )
        return customer

class CustomerResponseSerializer(serializers.ModelSerializer):
    customer_id = serializers.IntegerField(source='pk')
    name = serializers.SerializerMethodField()
    monthly_income = serializers.DecimalField(source='monthly_salary', max_digits=10, decimal_places=2)

    class Meta:
        model = Customer
        fields = ['customer_id', 'name', 'age', 'monthly_income', 'approved_limit', 'phone_number']

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

class LoanEligibilitySerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    tenure = serializers.IntegerField(min_value=1, max_value=360)
    
    def validate_loan_amount(self, value):
        return validate_loan_amount(value)
    
    def validate_interest_rate(self, value):
        return validate_interest_rate(value)
    
    def validate_tenure(self, value):
        return validate_tenure(value)

class LoanEligibilityResponseSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    approval = serializers.BooleanField()
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    corrected_interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    tenure = serializers.IntegerField()
    monthly_installment = serializers.DecimalField(max_digits=10, decimal_places=2)

class LoanCreationSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    tenure = serializers.IntegerField(min_value=1, max_value=360)
    
    def validate_loan_amount(self, value):
        return validate_loan_amount(value)
    
    def validate_interest_rate(self, value):
        return validate_interest_rate(value)
    
    def validate_tenure(self, value):
        return validate_tenure(value)

class LoanCreationResponseSerializer(serializers.Serializer):
    loan_id = serializers.IntegerField(allow_null=True)
    customer_id = serializers.IntegerField()
    loan_approved = serializers.BooleanField()
    message = serializers.CharField()
    monthly_installment = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)

class CustomerDetailSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='customer_id')

    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'last_name', 'phone_number', 'age']

class LoanDetailSerializer(serializers.ModelSerializer):
    customer = CustomerDetailSerializer(read_only=True)
    repayments_left = serializers.IntegerField(read_only=True)

    class Meta:
        model = Loan
        fields = ['loan_id', 'customer', 'loan_amount', 'interest_rate', 'monthly_repayment', 'tenure', 'repayments_left']

class LoanListSerializer(serializers.ModelSerializer):
    repayments_left = serializers.IntegerField(read_only=True)
    monthly_installment = serializers.DecimalField(source='monthly_repayment', max_digits=10, decimal_places=2)

    class Meta:
        model = Loan
        fields = ['loan_id', 'loan_amount', 'interest_rate', 'monthly_installment', 'repayments_left']