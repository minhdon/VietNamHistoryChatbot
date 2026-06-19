import bcrypt
password = b"supersecret"
salt = bcrypt.gensalt()
hashed = bcrypt.hashpw(password, salt)
print(hashed.decode('utf-8'))
print(bcrypt.checkpw(password, hashed))
