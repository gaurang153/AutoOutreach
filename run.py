import argparse
import json
from InstagramBot import InstagramBot
import random
from database import Base, engine

def load_accounts():
        try:
            with open("accounts.json", "r") as file:
                accounts = json.load(file)
        except FileNotFoundError:
            accounts = []
        return accounts

def save_accounts(accounts):
    with open("accounts.json", "w") as file:
        json.dump(accounts, file)


def create_bot(account):
    bot = InstagramBot()
    print("Instragrambot created")
    # bot.login(email=account["username"], password=account["password"])
    return bot


def main():
    Base.metadata.create_all(engine)
    parser = argparse.ArgumentParser(description="Instagram Bot")

    parser.add_argument("-a", "--account", help="Which account to Use")
    parser.add_argument("-kw", "--keyword", help="Keyword to scrape posts from")
    parser.add_argument("-ht", "--hashtag", help="To Scrape post on explore page of instagram")

    args = parser.parse_args()
    accounts = load_accounts()
    account_choice = int(args.account)
    hashtag = args.hashtag
    keyword = args.keyword

    if(account_choice < 1 or account_choice > len(accounts)):
        print("Please provide correct account no. The account no provided is not present!")
        return
    
    if len(accounts) == 0:
        print("No accounts found. Please add accounts first in accounts.json file.")
        return
    
    if account_choice:
        account = accounts[account_choice - 1]
        bot = create_bot(account)
        bot.login(account["username"], account["password"])

        if hashtag:
            print(f"scraping post from hashtag: {hashtag}")
            post_links = bot.scrape_hashtag_posts(hashtag=hashtag)
            print("Scraping usernames")
            usernames = bot.scrape_usernames(post_links)
            print("Sending DMs to usernames")
            # bot.send_dm(usernames=usernames)
        elif keyword:
            print(f"scraping post from keyword: {keyword}")
            profile_links = bot.scrape_profiles_google(keyword=keyword)
            bot.save_profiles_to_db(profile_links)
        elif not keyword and not hashtag:
            bot.perform_outreach_actions()
            bot.close_browser()
        else:
            print("Keyword, Hashtag or Account not added")

    # if args.comment:
    #     if not args.hashtag or not args.message:
    #         print("Please provide a hashtag and a message to comment.")
    #         return

    #     post_links = bot.scrape_hashtag_posts(hashtag=args.hashtag)
    #     bot.comment_on_posts(links=post_links, comment=args.message, delay_time=args.delay)
    # elif args.dm:
    #     if not args.message:
    #         print("Please provide a message to send.")
    #         return

    #     post_links2 = bot.scrape_hashtag_posts(hashtag=args.hashtag)
    #     usernames = bot.scrape_usernames(post_links2)
    #     print(usernames)
    #     usernames = ["_go.wrong_"]
    #     bot.send_dm(usernames=usernames, message=args.message, delay_time=args.delay)
    # else:
    #     print("Please choose whether to comment (-c) or send direct messages (-d).")

if __name__ == "__main__":
    main()
