from selenium import webdriver
import os
import time
import requests
from bs4 import BeautifulSoup

def clearGeneratedFiles():
    os.system("rm captcha.jpeg")
    os.system("rm captcha.txt")
    os.chdir("..")
    os.system("rm captcha.jpeg")

def generateAttendanceFile(table_text):
    try:
        print("Generating File.")
        with open('Attendance.html','w+') as f:
            f.write(str(table_text))
        f.close()
        print("File Generated!")
    except:
        print("Error Generating File!")

def scrapeAttendance(page_source):
    soup = BeautifulSoup(page_source,'lxml')
    generateAttendanceFile(soup.table)

def execute():
    erp_url = "http://erp.bitmesra.ac.in"
    captcha_url = erp_url + "/GenerateCaptcha.ashx"

    username = "Your-Username"
    password = "Your-Password"

    browser = webdriver.Chrome(executable_path=os.curdir + '/chromedriver')

    browser.get(erp_url)

    # Creating Session
    cookies = browser.get_cookies()
    session = requests.Session()
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])

    # Downloading Image Captcha
    try:
        read = session.get(captcha_url)
        with open("captcha.jpeg", 'wb') as w:
            for chunk in read.iter_content(chunk_size=512):
                if chunk:
                    w.write(chunk)
    except:
        print("Error Downloading Captcha Image")
        browser.quit()
        execute()
        return

    print("Captcha Downloaded Successfully")

    os.system("cp captcha.jpeg " + os.curdir + "/ocr-convert-image-to-text")
    print("File Copied")

    # Using OCR
    os.chdir(os.curdir + "/ocr-convert-image-to-text")
    os.system("python3 main.py --input_dir captcha.jpeg --output_dir .")
    print("captcha.txt generated")

    # Reading captcha from file
    with open("captcha.txt", "r") as captcha_file:
        for line in captcha_file:
            captcha = line.strip()
            break

    print("Captcha = " + captcha)

    # Filling up Form
    username_element = browser.find_element_by_name('txt_username')
    password_element = browser.find_element_by_name('txt_password')
    captcha_element = browser.find_element_by_name('txtcaptcha')
    submit_btn = browser.find_element_by_id('btnSubmit')

    username_element.send_keys(username)
    password_element.send_keys(password)
    captcha_element.send_keys(captcha)

    # Submitting Form
    submit_btn.click()

    # Fetch Student Detail
    try:
        student_detail_element = browser.find_element_by_id("ctl00_ContentPlaceHolder1_lvQLinks_ctrl1_btnLink")
    except:
        print("Captcha Doesn't Matched")
        browser.quit()
        os.chdir('..')
        execute()
        return

    student_detail_element.click()

    # Switching Browser To New Opened Tab On Click
    browser.switch_to_window(browser.window_handles[1])

    # Clear Temp Files
    clearGeneratedFiles()

    try:
        time.sleep(15)
        html = browser.execute_script("return document.getElementById('divAttendance').innerHTML")
        scrapeAttendance(html)
        browser.quit()
    except:
        print("Loading took too much time!Please Execute Script Again!")
        browser.quit()

#Execution Point
execute()
