"""
Generate multiple unique premium tokens for distribution
Each token has a unique timestamp to ensure uniqueness
"""
import os
import sys
import time
from datetime import datetime

# Set the JWT secret to match Railway
os.environ['JWT_SECRET_KEY'] = 'lRWZXEoTdCfkN-iIsNdx5AoP7Y9aSsIdKw0MaEm59_IDG1DHEBxaSwpzeK4MczG6RX5ezecHTuwk6KvT1jrRSQ'

# Now import the function
from telegram_bot.premium import generate_test_token

print("=" * 70)
print("🎫 GENERATING 15 UNIQUE PREMIUM TOKENS (30 DAYS EACH)")
print("=" * 70)
print(f"\n✅ Using Railway JWT Secret Key")
print(f"🕐 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 70)
print()

tokens = []
for i in range(15):
    token = generate_test_token(30)
    tokens.append(token)
    print(f"Token {i+1}:")
    print(token)
    print()
    # Small delay to ensure unique timestamps
    time.sleep(0.1)

print("=" * 70)
print("✅ All 15 tokens generated successfully!")
print("=" * 70)
print()
print("📋 USAGE:")
print("1. Copy any token above")
print("2. Send /premium to the bot")
print("3. Paste the token when prompted")
print()
print("⚠️  IMPORTANT:")
print("- Each token can only be used ONCE")
print("- Tokens expire in 30 days from generation")
print("- Keep these tokens secure!")
print()

# Save to file for easy distribution
output_file = 'premium_tokens.txt'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write("=" * 70 + "\n")
    f.write("15 PREMIUM TOKENS (30 DAYS)\n")
    f.write("Generated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
    f.write("=" * 70 + "\n\n")
    for i, token in enumerate(tokens, 1):
        f.write(f"Token {i}:\n{token}\n\n")
    f.write("\nUSAGE INSTRUCTIONS:\n")
    f.write("=" * 70 + "\n")
    f.write("1. Give one token to each user\n")
    f.write("2. User sends /premium to the bot\n")
    f.write("3. User pastes the token when prompted\n")
    f.write("\nIMPORTANT NOTES:\n")
    f.write("=" * 70 + "\n")
    f.write("- Each token can only be used ONCE\n")
    f.write("- Tokens are valid for 30 days from generation\n")
    f.write("- After use, the token will be marked as 'used' in database\n")
    f.write("- Keep tokens secure and distribute carefully\n")

print(f"💾 Tokens also saved to: {output_file}")
print()
