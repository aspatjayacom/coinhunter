import time
import requests
import os
from datetime import datetime
import hashlib
import ecdsa
import base58

def generate_wallets(number_of_wallets=20):
    wallets = []
    for _ in range(number_of_wallets):
        private_key = generate_private_key()
        address = private_key_to_address(private_key)
        wallets.append({"address": address, "privateKeyWIF": private_key})
    return wallets

def generate_private_key():
    return os.urandom(32).hex()

def private_key_to_address(private_key_hex):
    private_key_bytes = bytes.fromhex(private_key_hex)
    sk = ecdsa.SigningKey.from_string(private_key_bytes, curve=ecdsa.SECP256k1)
    vk = sk.verifying_key
    public_key = b'\x04' + vk.to_string()

    sha256 = hashlib.sha256(public_key).digest()

    ripemd160 = hashlib.new('ripemd160')
    ripemd160.update(sha256)
    hashed_public_key = ripemd160.digest()

    network_byte = b'\x00' + hashed_public_key

    checksum = hashlib.sha256(hashlib.sha256(network_byte).digest()).digest()[:4]

    binary_address = network_byte + checksum

    return base58.b58encode(binary_address).decode()

def fetch_balances(addresses):
    try:
        response = requests.get(f"https://blockchain.info/balance?active={addresses}")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Balance fetch error: {e}")
        return {}

def save_wallets_with_balance(wallets, balances):
    non_zero_balance_wallets = [
        wallet for wallet in wallets if balances.get(wallet["address"], {}).get("final_balance", 0) > 0
    ]

    if non_zero_balance_wallets:
        date_time = datetime.now().strftime("%Y%m%d-%H%M")
        file_name = f"btc{date_time}.txt"
        file_path = os.path.join("c:/CoinHunter/Btc", file_name)

        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w") as file:
            for wallet in non_zero_balance_wallets:
                balance_satoshis = balances[wallet["address"]]["final_balance"]
                balance_btc = balance_satoshis / 100000000
                file.write(f"Address: {wallet['address']}\n")
                file.write(f"WIF: {wallet['privateKeyWIF']}\n")
                file.write(f"Balance: {balance_btc:.8f} BTC\n\n")

        print(f"Saved wallets with balance to {file_path}")
    else:
        for wallet in wallets:
            address = wallet["address"]
            balance_satoshis = balances.get(address, {}).get("final_balance", 0)
            balance_btc = balance_satoshis / 100000000
            print(f"Address: {address} Balance: {balance_btc:.8f} BTC")

def auto_reload():
    while True:
        wallets = generate_wallets()
        addresses = "|".join(wallet["address"] for wallet in wallets)
        balances = fetch_balances(addresses)
        save_wallets_with_balance(wallets, balances)
        time.sleep(1)

if __name__ == "__main__":
    auto_reload()