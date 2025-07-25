from web3 import Web3
import time
from datetime import datetime
import requests
from dotenv import load_dotenv
import os
import json
from colorama import init, Fore, Style
from decimal import Decimal
import random

init(autoreset=True)
load_dotenv()

# === ASCII ART FUNCTIONS ===
def generate_random_chars(width=30, height=8):
    """Generate random characters for background effect"""
    chars = "!@#$%^&*()_+-=[]{}|;:,.<>?/~`"
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    numbers = "0123456789"
    all_chars = chars + letters + numbers
    
    background = []
    for _ in range(height):
        line = ""
        for _ in range(width):
            if random.random() < 0.6:  # 60% chance for character
                line += random.choice(all_chars)
            else:
                line += " "
        background.append(line)
    return background

def display_motivation():
    """Display motivational ASCII art"""
    print("\033[2J\033[H", end="")  # Clear screen
    
    # Random background characters in red
    background = generate_random_chars(35, 6)
    for line in background:
        print(Fore.RED + line)
    
    print()
    
    # Main motivational text
    art = """
██╗████████╗███████╗     ██████╗ ██╗  ██╗ █████╗ ██╗   ██╗
██║╚══██╔══╝██╔════╝    ██╔═══██╗██║ ██╔╝██╔══██╗╚██╗ ██╔╝
██║   ██║   ███████╗    ██║   ██║█████╔╝ ███████║ ╚████╔╝ 
██║   ██║   ╚════██║    ██║   ██║██╔═██╗ ██╔══██║  ╚██╔╝  
██║   ██║   ███████║    ╚██████╔╝██║  ██╗██║  ██║   ██║   
╚═╝   ╚═╝   ╚══════╝     ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   

    ██╗   ██╗ ██████╗ ██╗   ██╗     ██████╗ █████╗ ███╗   ██╗
    ╚██╗ ██╔╝██╔═══██╗██║   ██║    ██╔════╝██╔══██╗████╗  ██║
     ╚████╔╝ ██║   ██║██║   ██║    ██║     ███████║██╔██╗ ██║
      ╚██╔╝  ██║   ██║██║   ██║    ██║     ██╔══██║██║╚██╗██║
       ██║   ╚██████╔╝╚██████╔╝    ╚██████╗██║  ██║██║ ╚████║
       ╚═╝    ╚═════╝  ╚═════╝      ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝

        ██████╗  ██████╗     ██╗████████╗
        ██╔══██╗██╔═══██╗    ██║╚══██╔══╝
        ██║  ██║██║   ██║    ██║   ██║   
        ██║  ██║██║   ██║    ██║   ██║   
        ██████╔╝╚██████╔╝    ██║   ██║   
        ╚═════╝  ╚═════╝     ╚═╝   ╚═╝   
"""
    
    # Display art with colors
    colors = [Fore.CYAN, Fore.GREEN, Fore.YELLOW, Fore.MAGENTA, Fore.WHITE]
    art_lines = art.strip().split('\n')
    
    for i, line in enumerate(art_lines):
        if line.strip():
            color = colors[i % len(colors)]
            print(color + Style.BRIGHT + line)
        else:
            print()
    
    print()
    print(Fore.GREEN + Style.BRIGHT + "🚀 " + "="*60 + " 🚀")
    print(Fore.YELLOW + Style.BRIGHT + "        Starting ITA Wallet Monitor - Keep Going! 💪")
    print(Fore.GREEN + Style.BRIGHT + "🚀 " + "="*60 + " 🚀")
    print()
    
    # Random background at bottom
    bottom_bg = generate_random_chars(35, 4)
    for line in bottom_bg:
        print(Fore.RED + line)
    
    time.sleep(3)  # Show for 3 seconds
    print("\033[2J\033[H", end="")  # Clear screen again

# === ENVIRONMENT VARIABLES ===
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
RPC_URL = os.getenv('RPC_URL')
WALLET1 = os.getenv('WALLET1')
WALLET2 = os.getenv('WALLET2')
WALLET3 = os.getenv('WALLET3')

# Show motivation first
display_motivation()

if not all([TELEGRAM_TOKEN, CHAT_ID, RPC_URL, WALLET1]):
    print(Fore.RED + "❌ Error: .env file is incomplete!")
    exit()

WATCH_WALLETS = [
    {'address': WALLET1.lower(), 'name': 'Wallet 1'},
    {'address': WALLET2.lower() if WALLET2 else '', 'name': 'Wallet 2'},
    {'address': WALLET3.lower() if WALLET3 else '', 'name': 'Wallet 3'}
]
WATCH_WALLETS = [w for w in WATCH_WALLETS if w['address']]

# === RPC CONNECTION ===
web3 = Web3(Web3.HTTPProvider(RPC_URL))
if not web3.is_connected():
    print(Fore.RED + "❌ Failed to connect to ITA RPC.")
    exit()

print(f"{Fore.CYAN}🎯 Monitoring {len(WATCH_WALLETS)} wallets:")
for wallet in WATCH_WALLETS:
    print(f"   • {wallet['name']}: {wallet['address'][:10]}...{wallet['address'][-6:]}")

print(Fore.CYAN + "🚀 Monitoring started...\n")

# === VARIABLES & FILES ===
LOG_FILE = "ita_log.txt"
SESSION_FILE = "ita_session.json"

# Reset cumulative total to 0 on every restart
def reset_session_total():
    """Reset cumulative total to 0 and save to file"""
    try:
        with open(SESSION_FILE, 'w') as f:
            json.dump({'total': 0.0}, f)
        print(Fore.YELLOW + "🔄 Cumulative total has been reset to 0")
        return 0.0
    except Exception as e:
        print(Fore.YELLOW + f"⚠️ Warning: Failed to reset session file: {e}")
        return 0.0

def save_session_total(total):
    try:
        # Convert Decimal to float to avoid JSON serialization error
        total_float = float(total) if isinstance(total, Decimal) else total
        with open(SESSION_FILE, 'w') as f:
            json.dump({'total': total_float}, f)
    except Exception as e:
        print(Fore.YELLOW + f"⚠️ Warning: Failed to save session: {e}")

def write_log(entry):
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(entry + '\n')
    except Exception as e:
        print(Fore.YELLOW + f"⚠️ Warning: Failed to write log: {e}")

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg}
    try:
        res = requests.post(url, data=data, timeout=10)
        if res.status_code == 200:
            print(Fore.GREEN + "✅ Telegram message sent")
        else:
            print(Fore.RED + f"❌ Telegram failed: {res.text}")
    except Exception as e:
        print(Fore.RED + f"❌ Telegram error: {e}")

def celebration_animation():
    """Show celebration when ITA is received"""
    celebration = [
        "🎉 🎊 🎉 🎊 🎉 🎊 🎉 🎊 🎉",
        "💰 ITA RECEIVED! AWESOME! 💰",
        "🎉 🎊 🎉 🎊 🎉 🎊 🎉 🎊 🎉"
    ]
    
    for line in celebration:
        print(Fore.GREEN + Style.BRIGHT + line.center(50))
    print()

# === MONITORING ===
last_block = web3.eth.block_number

# AUTO RESET: Start with 0 on every restart
total_ita_received = reset_session_total()

print(Fore.CYAN + f"📊 Current cumulative total: {total_ita_received:.6f} ITA")
print(Fore.CYAN + f"🔍 Starting monitoring from block: {last_block}")

try:
    while True:
        try:
            latest_block = web3.eth.block_number

            # Process new blocks
            for block_num in range(last_block + 1, latest_block + 1):
                try:
                    block = web3.eth.get_block(block_num, full_transactions=True)
                    
                    for tx in block.transactions:
                        if tx.to:
                            tx_to = tx.to.lower()
                            for wallet in WATCH_WALLETS:
                                if tx_to == wallet['address']:
                                    # Convert Wei to Ether and handle Decimal properly
                                    amount = web3.from_wei(tx.value, 'ether')
                                    amount_float = float(amount)
                                    
                                    timestamp = datetime.fromtimestamp(block.timestamp).strftime('%d/%m/%Y %H:%M:%S')
                                    total_ita_received += amount_float

                                    # Show celebration animation
                                    celebration_animation()

                                    message = (
                                        f"🎉 ITA Received in {wallet['name']}!\n\n"
                                        f"💰 Amount  : {amount_float:.6f} ITA\n"
                                        f"📱 Wallet  : {wallet['name']}\n"
                                        f"🔗 Hash    : {tx.hash.hex()}\n"
                                        f"⏰ Block   : {block_num}\n"
                                        f"📅 Time    : {timestamp}\n"
                                        f"💳 Address : {wallet['address'][:10]}...{wallet['address'][-6:]}\n"
                                        f"📊 Total   : {total_ita_received:.6f} ITA"
                                    )

                                    print(Fore.GREEN + f"📥 {wallet['name']} received {amount_float:.6f} ITA at block {block_num}")
                                    print(Fore.YELLOW + f"📊 Cumulative total: {total_ita_received:.6f} ITA\n")

                                    send_telegram(message)
                                    write_log(f"[{timestamp}] {wallet['name']} received {amount_float:.6f} ITA at block {block_num}")
                                    save_session_total(total_ita_received)
                                    break
                                    
                except Exception as e:
                    print(Fore.RED + f"❌ Error processing block {block_num}: {e}")
                    continue

            last_block = latest_block
            
            # Status every 60 seconds with motivational messages
            current_time = int(time.time())
            if current_time % 60 == 0:
                motivational_messages = [
                    "Stay strong! Monitoring is active 💪",
                    "Keep going! You're doing great 🚀",
                    "Patience pays off! Still watching 👀",
                    "Never give up! Monitoring continues 💎",
                    "You've got this! System running smooth ⚡"
                ]
                msg = random.choice(motivational_messages)
                print(Fore.CYAN + f"⏰ {datetime.now().strftime('%H:%M:%S')} - {msg} (Block: {latest_block})")
                time.sleep(1)  # Prevent multiple prints in the same second
            
            time.sleep(10)
            
        except requests.exceptions.RequestException as e:
            print(Fore.RED + f"❌ RPC Connection error: {e}")
            print(Fore.YELLOW + "🔄 Don't worry! Trying to reconnect in 30 seconds... 💪")
            time.sleep(30)
            continue
            
        except Exception as e:
            print(Fore.RED + f"❌ Unexpected error: {e}")
            print(Fore.YELLOW + "🔄 No problem! Recovering in 5 seconds... 🚀")
            time.sleep(5)
            continue

except KeyboardInterrupt:
    print(Fore.RED + "\n🛑 Bot stopped by user.")
    print(Fore.YELLOW + f"📊 Total ITA this session: {total_ita_received:.6f} ITA")
    save_session_total(total_ita_received)
    write_log(f"[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] Bot stopped. Total: {total_ita_received:.6f} ITA")
    
    # Final motivation
    print(Fore.GREEN + Style.BRIGHT + "\n🌟 " + "="*50 + " 🌟")
    print(Fore.CYAN + Style.BRIGHT + "  Thank you for using ITA Monitor!")
    print(Fore.YELLOW + Style.BRIGHT + "  Remember: Success comes to those who persist!")
    print(Fore.MAGENTA + Style.BRIGHT + "  Keep coding, keep dreaming! 🚀💎")
    print(Fore.GREEN + Style.BRIGHT + "🌟 " + "="*50 + " 🌟")
    print(Fore.GREEN + "✅ Session data saved. See you next time! 👋")

except Exception as e:
    error_msg = f"🚨 Bot Fatal Error!\n\n{str(e)}"
    print(Fore.RED + f"❌ Fatal error: {e}")
    print(Fore.YELLOW + "💪 Don't give up! This is just a temporary setback!")
    save_session_total(total_ita_received)
    send_telegram(error_msg)
    write_log(f"[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] Bot fatal error: {e}")
