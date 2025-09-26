import requests
import base64
import datetime
from requests.auth import HTTPBasicAuth

# Safaricom Daraja credentials
consumer_key = "mSwsI6ZWD1zGqpFdPBB9jTZd4tmGkhPbGrahAxTrFUzvoBwo"
consumer_secret = "rxFFcAknoWS5ecOCPTWNDHwZGHgayxEM0X1R4CLkcJApiSqxXUm2OG8UGlLUoACC"
shortcode = "174379"  # Use your Paybill/Till Number
passkey = "N/A"

# Get access token
def get_access_token():
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    json_response = response.json()
    return json_response["access_token"]

# STK Push
def stk_push(phone_number, amount, account_reference="Test123", transaction_desc="Payment Test"):
    access_token = get_access_token()
    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode((shortcode + passkey + timestamp).encode("utf-8")).decode("utf-8")

    headers = {"Authorization": f"Bearer {access_token}"}

    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,         # Customer phone number (2547XXXXXXXX)
        "PartyB": shortcode,
        "PhoneNumber": phone_number,
        "CallBackURL": "https://yourdomain.com/callback",
        "AccountReference": account_reference,
        "TransactionDesc": transaction_desc
    }

    response = requests.post(api_url, json=payload, headers=headers)
    return response.json()

# Example usage
if __name__ == "__main__":
    phone = "2547XXXXXXXX"  # Customer's phone number
    amount = 10
    result = stk_push(phone, amount)
    print(result)
