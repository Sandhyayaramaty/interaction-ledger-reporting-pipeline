from solution.processing.encryption import decrypt_value


def mask_phone(encrypted_phone):
    """
    Decrypt a stored phone number and immediately mask it
    for reporting.
    """
    phone = decrypt_value(encrypted_phone)

    if not phone:
        return ""

    return "+91******" + phone[-4:]