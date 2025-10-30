"""
Generate premium tokens using Railway's JWT secret
Run this script to generate tokens that will work with your deployed bot
"""
import os
import sys

# Set the JWT secret to match Railway
os.environ['JWT_SECRET_KEY'] = 'lRWZXEoTdCfkN-iIsNdx5AoP7Y9aSsIdKw0MaEm59_IDG1DHEBxaSwpzeK4MczG6RX5ezecHTuwk6KvT1jrRSQ'

# Now import the function
from telegram_bot.premium import generate_test_token

print("=" * 60)
print("🎫 Premium Token Generator")
print("=" * 60)
print("\n✅ Using Railway JWT Secret Key")
print(f"Secret Key: {os.environ['JWT_SECRET_KEY'][:20]}...")
print("\n" + "=" * 60)

print("\n📅 7-Day Premium Token:")
print("-" * 60)
token_7d = generate_test_token(7)
print(token_7d)
print("-" * 60)

print("\n📅 30-Day Premium Token:")
print("-" * 60)
token_30d = generate_test_token(30)
print(token_30d)
print("-" * 60)

print("\n📅 90-Day Premium Token:")
print("-" * 60)
token_90d = generate_test_token(90)
print(token_90d)
print("-" * 60)

print("\n" + "=" * 60)
print("✅ Tokens generated successfully!")
print("=" * 60)
print("\n📋 Usage Instructions:")
print("1. Copy one of the tokens above")
print("2. In Telegram bot, send: /premium")
print("3. Paste the token when prompted")
print("4. Token will be validated and premium activated!")
print("\n" + "=" * 60)
