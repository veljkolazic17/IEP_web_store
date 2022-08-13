import re

def password_check(password):

    # calculating the length
    length_error = len(password) < 8 or len(password) > 256

    # searching for digits
    digit_error = re.search(r"\d", password) is None

    # searching for uppercase
    uppercase_error = re.search(r"[A-Z]", password) is None

    # searching for lowercase
    lowercase_error = re.search(r"[a-z]", password) is None

    # overall result
    password_ok = not ( length_error or digit_error or uppercase_error or lowercase_error )

    return password_ok