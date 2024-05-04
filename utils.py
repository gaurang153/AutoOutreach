import json
import os
import csv
from datetime import date
import time
import sys

from models.ProfileOutreach import ProfileOutreach

volume_path = '/reports'
old_stdout = sys.stdout

def load_accounts():
        try:
            with open("accounts.json", "r") as file:
                accounts = json.load(file)
        except FileNotFoundError:
            print("accounts.json not found! Please create accounts.json in C:\\dm_tool directory")
            accounts = []
        return accounts

def todays_date():
    today = date.today()
    # dd/mm/YY
    current_date = today.strftime("%d-%m-%Y")
    return current_date

def create_reports():
     csv_reports = ["replied", "messaged", "followed_up", "re_followed_up"]
     csv_headers = ["Sr No", "Profile Link", "Profile Name", "Message Sent", "Replied Message", "Sent By", "Sent Time", "City", "Industry", "Replied", "Followed Up"]
     date = todays_date() 
     lock_file = os.path.join(volume_path, 'create_lock')
     # Check if the lock file exists
     if not os.path.exists(lock_file):
        try:
            # Create a lock file to prevent other containers from creating the CSV file
            with open(lock_file, 'w') as f:
                f.write('lock')

            # Create the the reports
            for r in csv_reports:
                csv_file_path = os.path.join(volume_path, f"{date}_{r}_report.csv")
                if not os.path.exists(csv_file_path):
                    with open(csv_file_path, 'w', newline='') as csvfile:
                        writer = csv.writer(csvfile)
                        # Write header if necessary
                        writer.writerow(csv_headers)
                        # Write data
                        # writer.writerow(['data1', 'data2', 'data3'])
            
            print("CSV Reports created successfully.")
        except Exception as e:
            print("Error creating CSV Reports:", e)
        finally:
            # Remove the lock file after CSV file creation
            os.remove(lock_file)
     else:
          print("Another container is already creating the CSV Reports.")

def write_data_to_report(profile, report_name):
    try:
        profile_outreach = ProfileOutreach.get_profile_outreach(profile)
        if profile_outreach:
            date = todays_date()
            csv_file_path = os.path.join(volume_path, f"{date}_{report_name}_report.csv")
            row_count = 0
            with open(csv_file_path, 'r', newline='') as csvfile:
                row_count = sum(1 for row in csv.reader(csvfile))

            with open(csv_file_path, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                data = [row_count, f"{profile_outreach.profile}", f"{profile_outreach.profile_name}", f"{profile_outreach.message_sent}", f"{profile_outreach.replied_message}", f"{profile_outreach.sent_by}", f"{profile_outreach.sent_time}", f"{profile_outreach.city}", f"{profile_outreach.industry}", f"{profile_outreach.replied}", f"{profile_outreach.followed_up}"]
                writer.writerow(data)
    except Exception as e:
        print("Error writing data to CSV Reports:", e)
        

# def init_logs():
#     lock_file = os.path.join(volume_path, 'logs_lock')
#      # Check if the lock file exists

#     if not os.path.exists(lock_file):
#         try:
#             # Create a lock file to prevent other containers from creating the CSV file
#             with open(lock_file, 'w') as f:
#                 f.write('lock')
    
#             log_file_path = os.path.join(volume_path, f"{date}_backend.log")
#             log_file = open(log_file_path, 'w')
#             sys.stdout = log_file

#         except Exception as e:
#             print("Error creating logs file: ", e)
#         finally:
#             os.remove(lock_file)

#         return log_file
    
# def destruct_logs(log_file):
#     sys.stdout = old_stdout
#     log_file.close()