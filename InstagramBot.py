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


class InstagramBot:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--window-size=930,820")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument('--disable-dev-shm-usage')
        # chrome_options.add_argument("--start-maximized")  # Maximize the Chrome window
        # Use webdriver_manager to automatically download and manage the ChromeDriver
        # add undetected_chromedriver here 
        print("Creating chrome driver")
        driver = ChromeDriverManager().install()
        service = Service(driver)
        self.driver = uc.Chrome(service=service, options=chrome_options)

    def find_values_appearing_at_least_twice_excluding_specific_values(self, array, values_to_exclude):
        # Remove specified values from the array
        filtered_array = [item for item in array if item not in values_to_exclude]
        filtered_array_without_hashtag = [item for item in filtered_array if not item.startswith("#")]
        # Count the occurrences of each element in the filtered array
        count = Counter(filtered_array_without_hashtag)
        
        # Find all elements that are listed at least twice
        values_appearing_at_least_twice = [key for key, value in count.items() if value >= 2]

        return values_appearing_at_least_twice[0]
    
    @staticmethod
    def random_time_delay():
        rand_no = random.randint(5,20)
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

    def scrape_hashtag_posts(self, hashtag):
        # Open Instagram and navigate to the hashtag page
        self.driver.get(f"https://www.instagram.com/explore/tags/{hashtag}/")
        time.sleep(8)
        # Wait for the posts to load
        wait = WebDriverWait(self.driver, 10)

        all_links = self.driver.execute_script("return Array.from(document.querySelectorAll('a[href][role][tabIndex]')).map(a=> a.attributes.href.value)")
        links = [x for x in all_links if x.startswith("/p")]

        return links
    
    def scrape_usernames(self, links):
        usernames = []
        for link in links:
            self.driver.get(f'https://www.instagram.com/{link}')
            time.sleep(3)
            # Wait for the username element to load
            wait = WebDriverWait(self.driver, 10)
            alist = self.driver.execute_script("return Array.from(document.querySelectorAll(`a[href][role][tabIndex]`)).map(p=> p.text)")
            # Extract the username text
            username = self.find_values_appearing_at_least_twice_excluding_specific_values(alist, ['Clip', 'Carousel', ''])
            usernames.append(username)
        
        # Remove duplicate usernames
        usernames = list(set(usernames))
        return usernames
    
    def send_dm(self, usernames):
        # Go to the Instagram Direct Inbox
        self.driver.get("https://www.instagram.com/direct/inbox/")
        time.sleep(3)

        # Check if the notification pop-up is displayed
        notification_popup = self.driver.find_element(By.XPATH, "//button[contains(text(),'Not Now')]")
        if notification_popup.is_displayed():
            notification_popup.click()
            time.sleep(2)
        print("after notification pop")
        for username in usernames:
            # Click the 'New Message' button
            new_message_button = self.driver.find_element(By.CSS_SELECTOR, 'svg[aria-label="New message"]:first-of-type')
            new_message_button.click()
            time.sleep(2)

            # Wait for the recipient input field to become available
            wait = WebDriverWait(self.driver, 10)
            recipient_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input:first-of-type')))
            # Type each username and press Enter to add as a recipient
            # input_actions = ActionChains(self.driver)
            # input_actions.send_keys(username)
            # input_actions.perform()
            self.type_keys(username)
            time.sleep(1)
            # enter_actions = ActionChains(self.driver)
            # enter_actions.send_keys(Keys.RETURN)
            # enter_actions.perform()
            self.type_keys(Keys.ENTER)
            time.sleep(1)
            # recipient_input.clear()
            # recipient_input.send_keys(f"{username}")
            # time.sleep(1)
            # recipient_input.send_keys(Keys.ENTER)
            # time.sleep(1)

            select_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[aria-label="Toggle selection"]:first-of-type')))
            select_button.click()
            time.sleep(2)
            
            # Wait for the next button to become clickable
            next_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(),'Chat')]")))

            # Click the Next button to proceed to the message input
            next_button.click()
            time.sleep(3)

            # Create an instance of ActionChains
            actions = ActionChains(self.driver)
            
            full_message = InstagramBot.random_message()
            for text in full_message:
                actions.send_keys(text)
                actions.send_keys(Keys.RETURN)
                actions.perform()
                actions.reset_actions()
                time.sleep(2)
            
            # Perform the actions
            print(f"Initial message sent to {username}")
            if usernames[-1] == username:
                break;
            else:
                time_delay = InstagramBot.random_time_delay()
                print(f"Delay Time: {time_delay/60} mins")
                time.sleep(10)
        
        print("Messages sent to all usernames Ending the Process!!")
        self.driver.quit()

    def visit_profile_and_follow(self, profile_model):
        self.driver.get(f"https://www.instagram.com/{profile_model.profile}/")
        try:
            wait = WebDriverWait(self.driver, 15)
            try: 
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




    def save_profiles_to_db(self, profile_links):
        profiles = self.scrape_usernames_from_links(profile_links)
        #save the profiles
        for profile in profiles:
            ProfileOutreach.add_unique_profile(profile=profile, outreach_status=OutreachStatus.NOT_SENT)
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

    def send_message(self, profile_model):
        try:
            username = profile_model.profile
            # Go to the Instagram Profile
            self.driver.get(f"https://www.instagram.com/{username}/")
            time.sleep(5)
            wait = WebDriverWait(self.driver, 10)
            message_button = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Message')]")))
            actions = ActionChains(self.driver)
            actions.move_to_element(message_button).click().perform()
            time.sleep(5)

            # Check if the notification pop-up is displayed
            try:
                notification_popup = self.driver.find_element(By.XPATH, "//button[contains(text(),'Not Now')]")
                if notification_popup.is_displayed():
                    notification_popup.click()
                    time.sleep(2)
                print("after notification pop")
            except NoSuchElementException:
                print("No Popup detected")

            # Create an instance of ActionChains
            actions = ActionChains(self.driver)
            
            full_message = InstagramBot.random_message()
            string_message = ""
            for text in full_message:
                string_message = string_message + " \n" + text
                actions.send_keys(text)
                actions.send_keys(Keys.RETURN)
                actions.perform()
                actions.reset_actions()
                time.sleep(5)
            
            # Perform the actions
            print(f"Initial message sent to {username}")
            ProfileOutreach.set_message_sent_and_status(profile_model.profile, string_message)

            time_delay = InstagramBot.random_time_delay()
            print(f"Delay Time: {time_delay/60} mins")
            time.sleep(time_delay)
        except NoSuchElementException:
            ProfileOutreach.set_failed_status(profile_model.profile)


    def perform_outreach_actions(self):
        dm_limit = 15
        counter = 1
        while(counter < dm_limit):
            failed_profile = ProfileOutreach.get_first_failed_profile()

            if failed_profile:
                self.visit_profile_and_follow(failed_profile)
                post_links = self.check_latest_post(failed_profile)
                self.like_and_comment_on_posts(post_links)
                self.send_message(failed_profile)
                counter = counter + 1

            else:

                not_sent_profile = ProfileOutreach.get_first_not_sent_profile()

                if not_sent_profile:
                    self.visit_profile_and_follow(not_sent_profile)
                    post_links = self.check_latest_post(not_sent_profile)
                    self.like_and_comment_on_posts(post_links)
                    self.send_message(not_sent_profile)
                    counter= counter + 1
                else:
                    print("Please run the scraping bot no other profile left to outreach")
                    return


    def like_and_comment_on_posts(self, links):
        if links:
            comment = "Nice I Love it!!"
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



