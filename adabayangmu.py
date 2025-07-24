from web3 import Web3
import time
from datetime import datetime
import requests
from dotenv import load_dotenv
import os
import json
from colorama import init, Fore

init(autoreset=True)
load_dotenv()

# === ENV VAR ===
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
RPC_URL = os.getenv('RPC_URL')
WALLET1 = os.getenv('WALLET1')
WALLET2 = os.getenv('WALLET2')
WALLET3 = os.getenv('WALLET3')

if not all([TELEGRAM_TOKEN, CHAT_ID, RPC_URL, WALLET1]):
    print(Fore.RED + "❌ Error: .env tidak lengkap!")
    exit()

WATCH_WALLETS = [
    {'address': WALLET1.lower(), 'name': 'Wallet 1'},
    {'address': WALLET2.lower() if WALLET2 else '', 'name': 'Wallet 2'},
    {'address': WALLET3.lower() if WALLET3 else '', 'name': 'Wallet 3'}
]
WATCH_WALLETS = [w for w in WATCH_WALLETS if w['address']]

# === RPC CONNECT ===
web3 = Web3(Web3.HTTPProvider(RPC_URL))
if not web3.is_connected():
    print(Fore.RED + "❌ Gagal konek ke RPC ITA.")
    exit()

print(f"{Fore.CYAN}🎯 Memantau {len(WATCH_WALLETS)} wallet:")
for wallet in WATCH_WALLETS:
    print(f"   • {wallet['name']}: {wallet['address'][:10]}...{wallet['address'][-6:]}")

print(Fore.CYAN + "🚀 Monitoring dimulai...\n")

# === VARIABEL & FILE ===
LOG_FILE = "ita_log.txt"
SESSION_FILE = "ita_session.json"

def load_session_total():
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, 'r') as f:
                return float(json.load(f).get('total', 0))
        except:
            return 0.0
    return 0.0

def save_session_total(total):
    with open(SESSION_FILE, 'w') as f:
        json.dump({'total': float(total)}, f)  # 💡 Konversi aman

def write_log(entry):
    with open(LOG_FILE, 'a') as f:
        f.write(entry + '\n')

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg}
    try:
        res = requests.post(url, data=data)
        if res.status_code == 200:
            print(Fore.GREEN + "✅ Telegram terkirim")
        else:
            print(Fore.RED + f"❌ Telegram gagal: {res.text}")
    except Exception as e:
        print(Fore.RED + f"❌ Telegram error: {e}")

# === MONITORING ===
last_block = web3.eth.block_number
total_ita_received = load_session_total()

try:
    while True:
        latest_block = web3.eth.block_number

        for block_num in range(last_block + 1, latest_block + 1):
            try:
                block = web3.eth.get_block(block_num, full_transactions=True)
                for tx in block.transactions:
                    if tx.to:
                        tx_to = tx.to.lower()
                        for wallet in WATCH_WALLETS:
                            if tx_to == wallet['address']:
                                amount = web3.from_wei(tx.value, 'ether')
                                timestamp = datetime.fromtimestamp(block.timestamp).strftime('%d/%m/%Y %H:%M:%S')
                                total_ita_received += float(amount)

                                message = (
                                    f"🎉 ITA Masuk ke {wallet['name']}!\n\n"
                                    f"💰 Jumlah : {amount} ITA\n"
                                    f"📱 Wallet : {wallet['name']}\n"
                                    f"🔗 Hash   : {tx.hash.hex()}\n"
                                    f"⏰ Blok   : {block_num}\n"
                                    f"📅 Waktu  : {timestamp}\n"
                                    f"💳 Address: {wallet['address'][:10]}...{wallet['address'][-6:]}"
                                )

                                print(Fore.GREEN + f"📥 {wallet['name']} menerima {amount} ITA di blok {block_num}")
                                print(Fore.YELLOW + f"📊 Total kumulatif: {total_ita_received:.6f} ITA\n")

                                send_telegram(message)
                                write_log(f"[{timestamp}] {wallet['name']} menerima {amount} ITA di blok {block_num}")
                                save_session_total(total_ita_received)
                                break
            except Exception as e:
                print(Fore.RED + f"❌ Error blok {block_num}: {e}")
                continue

        last_block = latest_block
        time.sleep(10)

        # Status tiap menit
        if int(time.time()) % 60 == 0:
            print(Fore.CYAN + f"⏰ {datetime.now().strftime('%H:%M:%S')} - Monitoring aktif (Blok: {latest_block})")

except KeyboardInterrupt:
    print(Fore.RED + "\n🛑 Bot dihentikan oleh pengguna.")
    print(Fore.YELLOW + f"📊 Total ITA sesi ini: {total_ita_received:.6f} ITA")
    save_session_total(total_ita_received)
    write_log(f"[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] Bot dihentikan. Total: {total_ita_received:.6f} ITA")

except Exception as e:
    print(Fore.RED + f"❌ Error fatal: {e}")
    send_telegram(f"🚨 Bot Error!\n\n{e}")
