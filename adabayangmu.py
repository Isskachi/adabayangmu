from web3 import Web3
import time
from datetime import datetime
import requests
from dotenv import load_dotenv
import os

load_dotenv()  # Load dari .env

# === Konfigurasi dari Environment Variables SAJA ===
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
RPC_URL = os.getenv('RPC_URL')
WALLET1 = os.getenv('WALLET1')
WALLET2 = os.getenv('WALLET2')
WALLET3 = os.getenv('WALLET3')

# Validasi environment variables
if not all([TELEGRAM_TOKEN, CHAT_ID, RPC_URL, WALLET1]):
    print("❌ Error: Environment variables tidak lengkap!")
    print("Pastikan .env berisi: TELEGRAM_TOKEN, CHAT_ID, RPC_URL, WALLET1, dll")
    exit()

# Daftar wallet yang ingin dipantau
WATCH_WALLETS = [
    {
        'address': WALLET1.lower(),
        'name': 'Wallet 1'
    },
    {
        'address': WALLET2.lower() if WALLET2 else '',
        'name': 'Wallet 2'  
    },
    {
        'address': WALLET3.lower() if WALLET3 else '',
        'name': 'Wallet 3'
    }
]

# Filter wallet yang tidak kosong
WATCH_WALLETS = [w for w in WATCH_WALLETS if w['address']]

print(f"🎯 Memantau {len(WATCH_WALLETS)} wallet:")
for wallet in WATCH_WALLETS:
    print(f"   • {wallet['name']}: {wallet['address'][:10]}...{wallet['address'][-6:]}")

# Koneksi ke RPC
web3 = Web3(Web3.HTTPProvider(RPC_URL))
if not web3.is_connected():
    print("❌ Gagal konek ke ITA node.")
    exit()

print("🚀 Monitoring wallets via RPC...")

# Menyimpan blok terakhir yang sudah diperiksa
last_block = web3.eth.block_number

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg}
    try:
        requests.post(url, data=data)
        print("✅ Pesan Telegram terkirim")
    except Exception as e:
        print("❌ Gagal kirim ke Telegram:", e)

def get_wallet_name(address):
    """Mendapatkan nama wallet berdasarkan address"""
    for wallet in WATCH_WALLETS:
        if wallet['address'] == address.lower():
            return wallet['name']
    return "Unknown Wallet"

# === Loop Utama ===
try:
    while True:
        latest_block = web3.eth.block_number

        # Cek setiap blok baru
        for block_num in range(last_block + 1, latest_block + 1):
            try:
                block = web3.eth.get_block(block_num, full_transactions=True)
                
                # Cek setiap transaksi dalam blok
                for tx in block.transactions:
                    if tx.to:  # Pastikan tx.to tidak None
                        tx_to = tx.to.lower()
                        
                        # Cek apakah transaksi menuju salah satu wallet yang dipantau
                        for wallet in WATCH_WALLETS:
                            if tx_to == wallet['address']:
                                amount = web3.from_wei(tx.value, 'ether')
                                timestamp = datetime.fromtimestamp(block.timestamp).strftime('%d/%m/%Y %H:%M:%S')
                                
                                # Format pesan dengan nama wallet
                                message = (
                                    f"🎉 ITA Masuk ke {wallet['name']}!\n\n"
                                    f"💰 Jumlah : {amount} ITA\n"
                                    f"📱 Wallet : {wallet['name']}\n"
                                    f"🔗 Hash   : {tx.hash.hex()}\n"
                                    f"⏰ Blok   : {block_num}\n"
                                    f"📅 Waktu  : {timestamp}\n"
                                    f"💳 Address: {wallet['address'][:10]}...{wallet['address'][-6:]}"
                                )
                                
                                send_telegram(message)
                                print(f"✅ Notifikasi dikirim untuk {wallet['name']}: {amount} ITA")
                                break  # Keluar dari loop wallet setelah menemukan match
                                
            except Exception as e:
                print(f"❌ Error saat memproses blok {block_num}: {e}")
                continue

        last_block = latest_block
        time.sleep(10)  # Cek setiap 10 detik
        
        # Status update setiap menit
        if int(time.time()) % 60 == 0:
            print(f"⏰ {datetime.now().strftime('%H:%M:%S')} - Monitoring aktif (Blok: {latest_block})")

except KeyboardInterrupt:
    print("\n🛑 Bot dihentikan oleh user")
except Exception as e:
    print(f"❌ Error fatal: {e}")
    # Kirim notifikasi error ke Telegram
    error_msg = f"🚨 Bot ITA Monitor Error!\n\nError: {str(e)}\nWaktu: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
    send_telegram(error_msg)