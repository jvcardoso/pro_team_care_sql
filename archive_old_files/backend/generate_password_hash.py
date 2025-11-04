#!/usr/bin/env python3
"""
Script para gerar hash de senha usando bcrypt.

Uso: python generate_password_hash.py
"""
import bcrypt

# Senha a ser hashada
password = "admin123"

# Gera o hash
salt = bcrypt.gensalt()
hashed = bcrypt.hashpw(password.encode('utf-8'), salt)

print("\n" + "="*60)
print("HASH GERADO PARA SENHA: admin123")
print("="*60)
print(f"\nHash: {hashed.decode('utf-8')}")
print("\n" + "="*60)
print("\nUse este hash no script SQL abaixo.")
print("="*60 + "\n")
