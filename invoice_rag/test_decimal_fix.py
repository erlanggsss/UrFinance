"""
Test script to verify Decimal to float conversion works properly
"""
from decimal import Decimal

# Simulate the scenario
monthly_limit = Decimal('100000.00')  # From Supabase
current_spending = Decimal('50000.00')  # From Supabase
new_amount = 50000.0  # From invoice processing (float)

print("Testing Decimal/float arithmetic...")
print(f"Monthly limit (Decimal): {monthly_limit}")
print(f"Current spending (Decimal): {current_spending}")
print(f"New amount (float): {new_amount}")

# This would cause the error before the fix
try:
    result = current_spending + new_amount
    print(f"\n❌ ERROR: This should have failed but didn't: {result}")
except TypeError as e:
    print(f"\n✅ Expected error without conversion: {e}")

# After conversion (the fix)
monthly_limit = float(monthly_limit)
current_spending = float(current_spending)
new_amount = float(new_amount)

print("\nAfter converting to float:")
print(f"Monthly limit (float): {monthly_limit}")
print(f"Current spending (float): {current_spending}")
print(f"New amount (float): {new_amount}")

try:
    total_with_new = current_spending + new_amount
    remaining = monthly_limit - current_spending
    percentage_used = (current_spending / monthly_limit) * 100
    
    print(f"\n✅ Calculations work:")
    print(f"Total with new: Rp {total_with_new:,.2f}")
    print(f"Remaining: Rp {remaining:,.2f}")
    print(f"Percentage used: {percentage_used:.1f}%")
except Exception as e:
    print(f"\n❌ ERROR: {e}")
