from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from datetime import datetime, timedelta
from time import perf_counter
import logging
logging.basicConfig(level=logging.INFO)

def log_error(message):
    logging.error(message)

def log_info(message):
    logging.info(message)


def scrap_deez(password, username):
    # User does not exist or password does not match, use Selenium to log in
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--ignore-certificate-errors")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://lms.svuonline.org/login/index.php")
    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)
    try:
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, "page-my-index"))
        )
        log_info("logged in successful")
        # Scrape user courses and homeworks
        courses = scrape_courses_and_homework(driver)
        if not courses:
            log_error("Oh, empty courses. Let's try again..")
            courses = scrape_courses_and_homework(driver)
        print(courses)
        driver.quit()

        response_data = {
            "courses": courses
        }
        return response_data
    except TimeoutException:
        log_error("Timeout while logging in")
        driver.quit()
        return {"error": "Timeout Error"}
    except ConnectionAbortedError as e:
        log_error("Connection Aborted while logging in")
        driver.quit()
        return {"error": f"Connection Aborted {e}"}

def scrape_courses_and_homework(driver):
    courses = []

    def load_courses_from_current_page():
        # Find all course elements within the container
        elements = driver.find_elements(By.CSS_SELECTOR, 'div.card.dashboard-card')
        log_info(f"Getting {len(elements)} [dashboard-card] elements")
        for course_element in elements:
            try:
                # course_id = course_element.get_attribute('data-course-id')
                # role = course_element.get_attribute('role')
                course_url = course_element.find_element(By.TAG_NAME, 'a').get_attribute('href')
                course_name = course_element.find_element(By.CLASS_NAME, 'multiline').text.strip()
            except NoSuchElementException:
                continue

            if not course_url:
                continue
            # print(course_id)
            # print(role)
            print(course_url)
            print(course_name)

            # Skip non-course links
            if "view.php?id=" not in course_url:
                continue

            # Initialize homeworks list (assuming you'll extract homework info later)
            homeworks = []
            log_info(f"Getting {course_name}")
            # Append the course data
            courses.append({
                "name": course_name,
                "url": course_url,
                "homeworks": homeworks
            })


    try:
        load_courses_from_current_page()

        for course in courses:
            driver.get(course["url"])
            WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.CLASS_NAME, "page-header-headings")))
            course_name = driver.find_element(By.CLASS_NAME, "page-header-headings").text

            try:
                assignment_elements = driver.find_elements(By.CSS_SELECTOR, ".activity.assign.modtype_assign")
                for element in assignment_elements:
                    id = element.get_attribute("id").split("-")[1]
                    homework_url = f"https://lms.svuonline.org/mod/assign/view.php?id={id}"
                    driver.get(homework_url)
                    days_left = "No Homework"
                    if driver.find_elements(By.CSS_SELECTOR, "td.lastcol")[2].text.split()[0].isdigit():
                        days_left = driver.find_elements(By.CSS_SELECTOR, "td.lastcol")[2].text.split()[0]

                    dates = driver.find_elements(By.CSS_SELECTOR, "div[data-region='activity-dates'] span")
                    start_date = dates[1].text
                    end_date = dates[3].text

                    date_format = f"%A, %d %B %Y, %I:%M %p"
                    homework = {
                        "name": driver.find_element(By.CSS_SELECTOR, "h2").text,
                        "start_date": datetime.strptime(start_date.replace("،", ","), date_format).ctime(),
                        "end_date": datetime.strptime(end_date.replace("،", ","), date_format).ctime(),
                        "days_left": days_left,
                        "url": homework_url
                    }
                    log_info(f"Getting {homework['name']}")
                    course["homeworks"].append(homework)
                    
            except Exception as e:
                log_error(f"Error processing homework: {e}")
                print(f"Error processing homework for course {course_name}: {e}")
                continue

        return courses
    except TimeoutException as e:
        log_error(f"Timeout Error while getting courses: {e}")
        return [{"error": "Timeout Error"}]
