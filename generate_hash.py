from werkzeug.security import generate_password_hash

admin_hash = generate_password_hash("admin123")
citizen_hash = generate_password_hash("citizen123")

print("ADMIN HASH:")
print(admin_hash)

print("\nCITIZEN HASH:")
print(citizen_hash)