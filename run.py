from InstagramBot import InstagramBot
from database import Base, engine, init_db 
from models.InstagramAccount import InstagramAccount
import os
from dotenv import dotenv_values
from utils import create_reports

def create_bot():
    bot = InstagramBot()
    print("Instragrambot created")
    return bot

def main():
    init_db()

    env_vars = dotenv_values('.env')
    dockerized = os.environ['DOCKERIZED']
    if dockerized == "true":
        city = os.environ['CITY']
        industry = os.environ['INDUSTRY']
        start_dm_tool =  os.environ['START_DM_TOOL']
        additional_search = os.environ['ADDITIONAL_SEARCH']
        seed_data = os.environ['SEED_DATA']
    else:
        city = env_vars.get('CITY')
        industry = env_vars.get('INDUSTRY')
        start_dm_tool =  env_vars.get('START_DM_TOOL')

    if seed_data == "true":
        InstagramAccount.seed_data_accounts()
        return

    keyword = None
    if industry and city:
        keyword = industry + " " + city +' ' + additional_search

    bot = create_bot()
    if start_dm_tool == "true":
        if dockerized == "true":
            create_reports()
        
        account_choice = InstagramAccount.get_account_choice()
        if account_choice:
            print(f"Selected Account: #{account_choice.username}")
            bot.login(account_choice.username, account_choice.password)
            bot.perform_outreach_actions(sent_by=account_choice.username)
            bot.perform_follow_up_actions(sent_by=account_choice.username)
            InstagramAccount.unlock_account_choice(account_choice)
            bot.close_browser()
        else:
            bot.close_browser()
            print("No Account to Choose from Please Add accounts to accounts.json")
    else:
        if keyword:
            print(f"scraping post from keyword: {keyword}")
            profile_links = bot.scrape_profiles_google(keyword=keyword)
            bot.save_profiles_to_db(profile_links, city, industry)
            bot.close_browser()
        else:
            bot.close_browser()
            print("Keyword Not Provided Exiting Bot!...")

if __name__ == "__main__":
    main()
