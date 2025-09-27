import tkinter as tk
from tkinter import messagebox
import requests
import base64
import datetime
from requests.auth import HTTPBasicAuth

# ----------------------------
# Safaricom Daraja credentials (sandbox)
consumer_key = "gxs1xHg6Sdq147hMPuoFEGvW2I54Bm1qc0Z24hR9EUrxbxR7"
consumer_secret = "9ZEkCTRHwXVQUvCcipDiXHJwXbb7GNrfLEx6gZUV5ogUzGMBWIglMiN0OlX2DkP8"
shortcode = "174379"
passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
COST_PER_GAME = 20

# Global trackers
games_left = 0
balance = 0

# ----------------------------
# Get access token
def get_access_token():
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    return response.json()["access_token"]

# ----------------------------
# STK Push
def stk_push(phone_number, amount):
    access_token = get_access_token()
    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode((shortcode + passkey + timestamp).encode()).decode()

    headers = {"Authorization": f"Bearer {access_token}"}
    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": shortcode,
        "PhoneNumber": phone_number,
        "CallBackURL": "https://mydummyurl.com/callback",
        "AccountReference": "PoolGame",
        "TransactionDesc": "Pool Table Payment"
    }

    response = requests.post(api_url, json=payload, headers=headers)
    return response.json()

# ----------------------------
# GUI Logic
def pay():
    global games_left, balance
    try:
        phone = phone_entry.get().strip()
        amount = int(amount_entry.get())
        if not phone.startswith("2547"):
            messagebox.showerror("Error", "Use format 2547XXXXXXXX")
            return

        response = stk_push(phone, amount)
        if "ResponseCode" in response and response["ResponseCode"] == "0":
            new_games = amount // COST_PER_GAME
            balance += amount % COST_PER_GAME

            games_left += new_games

            # Auto-convert balance into games if >= 20
            while balance >= COST_PER_GAME:
                games_left += 1
                balance -= COST_PER_GAME

            update_labels()
            messagebox.showinfo("Success", f"Payment successful!\nYou now have {games_left} game(s) and Ksh {balance} balance.")
        else:
            messagebox.showerror("Error", f"Payment failed: {response}")
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid amount.")

def play_game():
    global games_left
    if games_left > 0:
        games_left -= 1
        update_labels()
    else:
        messagebox.showinfo("No Games", "You don’t have any games left!")

def update_labels():
    games_label.config(text=f"Games Left: {games_left}")
    balance_label.config(text=f"Balance: Ksh {balance}")

# ----------------------------
# Tkinter UI
root = tk.Tk()
root.title("Pool Game Payment System")

tk.Label(root, text="Phone Number (2547...):").pack(pady=5)
phone_entry = tk.Entry(root)
phone_entry.pack(pady=5)

tk.Label(root, text="Amount to Pay (Ksh):").pack(pady=5)
amount_entry = tk.Entry(root)
amount_entry.pack(pady=5)

tk.Button(root, text="Pay with M-Pesa", command=pay).pack(pady=10)

games_label = tk.Label(root, text="Games Left: 0", font=("Arial", 14))
games_label.pack(pady=10)

balance_label = tk.Label(root, text="Balance: Ksh 0", font=("Arial", 14))
balance_label.pack(pady=5)

tk.Button(root, text="Play Game", command=play_game).pack(pady=10)

root.mainloop()
