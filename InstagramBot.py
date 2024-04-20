import time
import json
#from selenium import webdriver
import undetected_chromedriver as uc
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from collections import Counter
import random
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from models.ProfileOutreach import ProfileOutreach, OutreachStatus
from models.InstagramAccount import InstagramAccount
from utils import write_data_to_report


class InstagramBot:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--window-size=930,820")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument("--start-maximized")  # Maximize the Chrome window
        # Use webdriver_manager to automatically download and manage the ChromeDriver
        # add undetected_chromedriver here 
        print("Creating chrome driver")
        driver = ChromeDriverManager().install()
        service = Service(driver)
        self.driver = uc.Chrome(service=service, options=chrome_options)

    # def find_values_appearing_at_least_twice_excluding_specific_values(self, array, values_to_exclude):
    #     # Remove specified values from the array
    #     filtered_array = [item for item in array if item not in values_to_exclude]
    #     filtered_array_without_hashtag = [item for item in filtered_array if not item.startswith("#")]
    #     # Count the occurrences of each element in the filtered array
    #     count = Counter(filtered_array_without_hashtag)
        
    #     # Find all elements that are listed at least twice
    #     values_appearing_at_least_twice = [key for key, value in count.items() if value >= 2]

    #     return values_appearing_at_least_twice[0]
    
    @staticmethod
    def random_time_delay(min, max):
        rand_no = random.randint(min, max)
        return int(rand_no)*60
    
    @staticmethod
    def random_message():

        full_message = []
        messages = InstagramBot.load_messages()
        for i in range(3):
            rand_no = random.randint(0,9)
            if i == 0:
                full_message.append(messages["init_messages"][rand_no])
            elif i == 1:
                full_message.append(messages["mid_messages"][rand_no])
            elif i == 2:
                full_message.append(messages["last_message"][rand_no])

        return full_message


    @staticmethod
    def load_messages():
        try:
            with open("messages.json", "r") as file:
                messages = json.load(file)
        except FileNotFoundError:
            messages = []
        return messages
    
    def type_keys(self, to_type):
        input_actions = ActionChains(self.driver)
        input_actions.send_keys(to_type)
        input_actions.perform()


    def login(self, email, password):
        # Open Instagram
        self.driver.get("https://www.instagram.com/")
        # Wait for the login elements to become available
        wait = WebDriverWait(self.driver, 10)
        email_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        password_field = wait.until(EC.presence_of_element_located((By.NAME, "password")))

        # Find the login elements and enter email and password
        email_field.send_keys(email)
        password_field.send_keys(password)

        # Submit the login form
        password_field.send_keys(Keys.RETURN)

        # Wait for the login process to complete (you may need to adjust the delay based on your internet speed)
        time.sleep(10)  # Wait for 5 seconds (adjust as needed)

    def visit_profile_and_follow(self, profile_model):
        self.driver.get(f"https://www.instagram.com/{profile_model.profile}/")
        try:
            wait = WebDriverWait(self.driver, 15)
            try: 
                profile_name_element = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "span[dir=auto][style^='line-height: var(--base-line-clamp-line-height); --base-line-clamp-line-height: 18px;']")))[0]
                if profile_name_element:
                    profile_name = profile_name_element.get_attribute('innerText')
                    ProfileOutreach.set_profile_name(profile_name=profile_name, profile_id=profile_model.id)
                follow_button = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Follow')]")))
                if follow_button:
                    actions = ActionChains(self.driver)
                    actions.move_to_element(follow_button).click().perform()
            except TimeoutException:
                print("Already Following or Not able to Follow")
                
            following = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Following')]")))
            if following:
                print(f"Successfully Followed {profile_model.profile}")
            time.sleep(2)
        except TimeoutException:
            print(f"Failed to follow the profile or Requested follow if profile is private: {profile_model.profile}")
    
    def check_latest_post(self, profile_model):
        username = profile_model.profile
        self.driver.get(f"https://instagram.com/{username}/")
        time.sleep(5)
        links = set()

        #post
        #a[href^='/p/']
        post_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href^='/p/']")
        if post_links:
            links.add(post_links[0].get_attribute("href"))
        
        #reel
        #a[href^='/reel/']
        reel_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href^='/reel/']")
        if reel_links:
            links.add(reel_links[0].get_attribute("href"))

        #return array of links for posts or reels
        return list(links)

    def scrape_profiles_google(self, keyword):
        # Create an instance of ActionChains
        actions = ActionChains(self.driver)

        #Go to Google search home page
        self.driver.get("https://www.google.com/")
        time.sleep(3)

        #Select Search Bar
        search_text = "site:instagram.com "+ keyword
        self.type_keys(search_text)
        time.sleep(1)
        self.type_keys(Keys.ENTER)
        time.sleep(5)

        # Check if the location pop-up is displayed
        # Set a maximum wait time
        timeout = 15  # seconds
        try:
            # Wait for the element to be present
            location_popup = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='dialog']"))
            )
            print("Element found:", location_popup)
            if location_popup:
                not_now = self.driver.find_element(By.XPATH, "//div[contains(text(),'Not now')]")
                actions.move_to_element(not_now).click().perform()
                time.sleep(2)
            # Continue with further execution
        except TimeoutException:
            print("Element not found within the specified time limit. Continuing execution...")
        except NoSuchElementException:
            print("No location popup detected")


        #Scroll to Bottom of the page
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        last_link = self.driver.find_elements(By.CSS_SELECTOR, "a[href^='https://www.instagram']:last-child")[-1].get_attribute('href')
        
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Adjust the sleep time as needed
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                more_results = self.driver.find_element(By.XPATH, "//span[contains(text(),'More results')]")
                if more_results:
                    actions.move_to_element(more_results).click().perform()
                    time.sleep(2)
                    new_last_link = self.driver.find_elements(By.CSS_SELECTOR, "a[href^='https://www.instagram']:last-child")[-1].get_attribute('href')
                    if new_last_link == last_link:
                        break
                    else:
                        last_link = new_last_link
                else:
                    break
                
            last_height = new_height

        #get instagram profile link elements
        instagram_link_elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href^='https://www.instagram']")
        
        profile_links_set = set()

        #get profile url from elements
        for element in instagram_link_elements:
            profile_links_set.add(element.get_attribute("href"))

        #converting set to array
        profile_links = list(profile_links_set)
        print(len(profile_links))
        return profile_links




    def save_profiles_to_db(self, profile_links, city, industry):
        profiles = self.scrape_usernames_from_links(profile_links)
        #save the profiles
        for profile in profiles:
            ProfileOutreach.add_unique_profile(profile=profile, outreach_status=OutreachStatus.NOT_SENT, city=city, industry=industry)
        print("Saved all the profiles to database with status NOT_SENT")
    
    def scrape_usernames_from_links(self, profile_links):
        #filter reels and post links maybe get profile data from post or reel by visiting that and getting username from that
        #skip /reel/:reel_id
        #skip /p/:post_id
        #/username/reel
        #/username/p
        #/username
        profiles_set = set()
        skip_uris = ["p", "reel"]
        for link in profile_links:
            username = link.split("/")[3]
            if username not in skip_uris:
                profiles_set.add(username)

        profiles = list(profiles_set)
        return profiles
    
    def visit_and_click_message(self, profile_name):
        self.driver.get(f"https://www.instagram.com/{profile_name}/")
        time.sleep(5)
        wait = WebDriverWait(self.driver, 10)
        message_button = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Message')]")))
        actions = ActionChains(self.driver)
        actions.move_to_element(message_button).click().perform()
        time.sleep(5)

    def close_notification_popup(self):
        try:
            notification_popup = self.driver.find_element(By.XPATH, "//button[contains(text(),'Not Now')]")
            if notification_popup.is_displayed():
                notification_popup.click()
                time.sleep(2)
            print("after notification pop")
        except NoSuchElementException:
            print("No Popup detected")

    def send_message(self, profile_model, sent_by):
        min_delay = 7
        max_delay = 10
        try:
            profile_name = profile_model.profile
            # Go to the Instagram Profile
            self.visit_and_click_message(profile_name=profile_name)

            # Check if the notification pop-up is displayed
            self.close_notification_popup()

            # Create an instance of ActionChains
            actions = ActionChains(self.driver)
            
            full_message = InstagramBot.random_message()
            string_message = ""
            for text in full_message:
                string_message = string_message + " \n" + text
                actions.send_keys(text)
                actions.key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.SHIFT).key_up(Keys.ENTER).perform()
                actions.perform()
                actions.reset_actions()
                time.sleep(1)
            actions.send_keys(Keys.RETURN)
            actions.perform()
            
            # Perform the actions
            print(f"Initial message sent to {profile_name}")
            ProfileOutreach.set_message_sent_and_status(profile_name, string_message, sent_by)
            write_data_to_report(profile=profile_name, report_name="messaged")
            time_delay = InstagramBot.random_time_delay(min_delay, max_delay)
            print(f"Delay Time: {time_delay/60} mins")
            time.sleep(time_delay)
        except NoSuchElementException:
            ProfileOutreach.set_failed_status(profile_name)

    
    def perform_follow_up_actions(self, sent_by):
        min_delay = 2
        max_delay = 4
        follow_up_message = InstagramBot.load_messages()["follow_up_message"]
        re_follow_up_message = InstagramBot.load_messages()["re_follow_up_message"]
        #get profile where sent_time is not null and sent time difference > 48hrs and sent_by is current account
        follow_up_profiles = ProfileOutreach.get_follow_up_profiles(sent_by=sent_by)
        if follow_up_profiles:
            for profile in follow_up_profiles:
                #check if profile replied
                replied = self.check_reply_status(profile_name=profile.profile)
                if replied:
                    #if yes then update replied as true
                    ProfileOutreach.set_replied(profile_name=profile.profile, replied=True)
                    write_data_to_report(profile=profile.profile, report_name="replied")
                else:
                    #if no then update replied as false and send 1st follow up message
                    ProfileOutreach.set_replied(profile_name=profile.profile, replied=False)
                    actions = ActionChains(self.driver)
                    actions.send_keys(follow_up_message)
                    actions.send_keys(Keys.RETURN)
                    actions.perform()
                    write_data_to_report(profile=profile.profile, report_name="followed_up")
                    time_delay = InstagramBot.random_time_delay(min_delay, max_delay)
                    print(f"Delay Time: {time_delay/60} mins")
                    time.sleep(time_delay)               
        #get profile where sent time difference > 96hrs and replied is false and sent_by is current account
        re_follow_up_profiles = ProfileOutreach.get_re_follow_up_profiles(sent_by=sent_by)
        if re_follow_up_profiles:
            for profile in re_follow_up_profiles:
                replied = self.check_reply_status(profile_name=profile.profile)
                if replied:
                    #if yes then update replied as yes
                    ProfileOutreach.set_replied(profile_name=profile.profile, replied=True)
                    write_data_to_report(profile=profile.profile, report_name="replied")
                else:
                    #if no then update replied as false and send 2nd follow up message
                    ProfileOutreach.set_replied(profile_name=profile.profile, replied=False)
                    actions = ActionChains(self.driver)
                    actions.send_keys(re_follow_up_message)
                    actions.send_keys(Keys.RETURN)
                    actions.perform()
                    #set followed up as true so no more follow ups
                    ProfileOutreach.set_followed_up(profile_name=profile.profile, followed_up=True)
                    write_data_to_report(profile=profile.profile, report_name="re_followed_up")
                    time_delay = InstagramBot.random_time_delay(min_delay, max_delay)
                    print(f"Delay Time: {time_delay/60} mins")
                    time.sleep(time_delay)
        print("Follow Up Actions Performed Successfully!")
    
    def check_reply_status(self, profile_name):
        try:
            self.visit_and_click_message(profile_name=profile_name)
            # Check if the notification pop-up is displayed
            self.close_notification_popup()
            wait = WebDriverWait(self.driver, 10)
            replied_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[style^='background-color: rgb(var(--ig-highlight-background))']")))
            replied_message = ""
            for element in replied_elements:
                replied_message = replied_message + element.get_attribute('innerText') + "\n"

            ProfileOutreach.set_replied_message(profile = profile_name, replied_message=replied_message)
            return True
        except TimeoutException:
            print(f"Did not Reply: #{profile_name}")
            return False

    def perform_outreach_actions(self, sent_by):
        dm_limit = 15
        counter = 1
        while(counter < dm_limit):
            failed_profile = ProfileOutreach.get_first_failed_profile()

            if failed_profile:
                self.visit_profile_and_follow(failed_profile)
                post_links = self.check_latest_post(failed_profile)
                self.like_and_comment_on_posts(post_links)
                self.send_message(failed_profile, sent_by)
                counter = counter + 1

            else:

                not_sent_profile = ProfileOutreach.get_first_not_sent_profile()

                if not_sent_profile:
                    self.visit_profile_and_follow(not_sent_profile)
                    post_links = self.check_latest_post(not_sent_profile)
                    self.like_and_comment_on_posts(post_links)
                    self.send_message(not_sent_profile, sent_by)
                    counter= counter + 1
                else:
                    print("Please run the scraping bot no other profile left to outreach")
                    return


    def like_and_comment_on_posts(self, links):
        if links:
            comment = InstagramBot.load_messages()["comment"]
            delay_time = 5
            for link in links:
                
                # Open each post link
                self.driver.get(link)
                time.sleep(2)

                actions = ActionChains(self.driver)
                #Like the Photo
                wait = WebDriverWait(self.driver, 15)

                try:
                    like_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "svg[aria-label='Like']")))
                    if like_button:
                        actions.move_to_element(like_button).click().perform()
                        time.sleep(2)
                except TimeoutException:
                    print("Not able to Like the Post")

                # Find the comment input field
                try:
                    comment_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'textarea[aria-label="Add a comment…"]')))
                    if comment_input:
                        comment_input.click()
                        time.sleep(1)
                        #get comment from files or database

                        # Create an instance of ActionChains
                        actions = ActionChains(self.driver)
                        actions.send_keys(comment)
                        actions.send_keys(Keys.RETURN)
                        # Perform the actions
                        actions.perform()
                except TimeoutException:
                    print("Not able to comment on post")
                

                time.sleep(delay_time)
                
            print("Liked and Commented on posts")
        else:
            print("No posts or reels to comment on!")
            return

    def close_browser(self):
        self.driver.quit()