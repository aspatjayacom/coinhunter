import random
import string
import time
import requests
import threading
from pathlib import Path
from datetime import datetime

ETHERSCAN_URL = "https://api.etherscan.io/api"
API_KEYS_FILE = "Apikey.txt"

# Load API keys from file
def load_api_keys():
    path = Path(API_KEYS_FILE)
    if not path.exists():
        print(f"{API_KEYS_FILE} not found.")
        return []
    with open(path, "r") as f:
        keys = [line.strip() for line in f if line.strip()]
    return keys

# Generate dummy Ethereum address and private key
def generate_wallet():
    address = "0x" + ''.join(random.choices("abcdef" + string.digits, k=40))
    private_key = "0x" + ''.join(random.choices("abcdef" + string.digits, k=64))
    return address, private_key

# Fetch ETH balance from Etherscan
def fetch_balance(address, api_key):
    params = {
        "module": "account",
        "action": "balance",
        "address": address,
        "tag": "latest",
        "apikey": api_key
    }
    try:
        response = requests.get(ETHERSCAN_URL, params=params)
        data = response.json()
        if data["status"] == "1":
            return float(data["result"]) / 1e18
        else:
            return 0.0
    except:
        return 0.0

# Save wallet to text file
def save_wallet(address, private_key, balance):
    folder = Path("Eth")
    folder.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%d%m%Y-%H%M")
    filename = folder / f"Eth{timestamp}.txt"
    with open(filename, "w") as f:
        f.write(f"Address: {address}\n")
        f.write(f"Private Key: {private_key}\n")
        f.write(f"Balance: {balance:.6f} ETH\n")
    print(f"Wallet with balance found and saved to {filename}")

# Checker loop for each API key
def check_wallets(api_key):
    count = 0
    while True:
        for _ in range(4):  # up to 4 calls per second to avoid rate limit
            address, private_key = generate_wallet()
            balance = fetch_balance(address, api_key)
            count += 1
            print(f"[{api_key[:6]}...] #{count} Address: {address} | Balance: {balance:.6f} ETH")

            if balance > 0:
                print("\n🎉 Wallet with balance found!")
                print(f"Address: {address}")
                print(f"Private Key: {private_key}")
                print(f"Balance: {balance:.6f} ETH\n")
                save_wallet(address, private_key, balance)
                print("🔔 Notification: Wallet with balance detected!")
                return
        time.sleep(1)  # delay to stay within 4 calls per second

# Main function to run threading per API key
def main():
    api_keys = load_api_keys()
    if not api_keys:
        print("No API keys found in Apikey.txt.")
        return

    threads = []
    for key in api_keys:
        t = threading.Thread(target=check_wallets, args=(key,), daemon=True)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
