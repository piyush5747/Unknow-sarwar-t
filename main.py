import requests
import time
import random
from datetime import datetime
import os

# Function to read access token from a file
def read_token():
    try:
        with open('token.txt', 'r') as file:
            access_token = file.readline().strip()  # Read first line for Access Token
        return access_token
    except Exception as e:
        print(f"Error reading token file: {e}")
        return None

# Function to read Post IDs from a file
def read_post_ids():
    try:
        with open('post_ids.txt', 'r') as file:
            post_ids = [line.strip() for line in file.readlines()]  # Read each line for Post IDs
        return post_ids
    except Exception as e:
        print(f"Error reading post IDs file: {e}")
        return []

# Function to read comments and location from a file
def read_comments_and_location():
    try:
        with open('comments.txt', 'r') as file:
            comments = file.readlines()[0].strip().split(",")  # Read the first line for comments
        location = comments[-1]  # Last item as location
        comments = comments[:-1]  # Remove location from comments
        return comments, location
    except Exception as e:
        print(f"Error reading comments file: {e}")
        return [], None

# Function to read live time from a file
def read_live_time():
    try:
        with open('time.txt', 'r') as file:
            live_time = file.readline().strip()  # Format: HH:MM
        return live_time
    except Exception as e:
        print(f"Error reading time file: {e}")
        return None

# Function to check if the token is expired
def is_token_expired(access_token):
    url = f"https://graph.facebook.com/v17.0/me?access_token={access_token}"
    try:
        response = requests.get(url)
        if response.status_code == 401:  # Token expired or invalid
            print("❌ The token has expired or is invalid.")
            return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to check token: {e}")
    return False

# Function to post a comment with location
def post_comment(post_id, comment_text, access_token, location):
    url = f"https://graph.facebook.com/v17.0/{post_id}/comments"
    data = {
        "message": f"{comment_text} - Location: {location}",
        "access_token": access_token,
    }
    
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()  # Raise an exception for bad status codes
        print(f"✅ Comment posted successfully on Post ID: {post_id}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to post comment on Post ID {post_id}: {e}")
        return False
    return True

# Function to check if it's the right time to post a comment
def is_time_to_post(live_time):
    current_time = datetime.now().strftime("%H:%M")
    return current_time == live_time

# Function to control the flow of posting with smooth transitions
def smooth_commenting_flow(access_token, post_ids, comments, location, live_time):
    print("Starting Facebook Auto-Comment Bot...")

    for post_id in post_ids:
        # Wait until it's the right time to post
        while not is_time_to_post(live_time):
            print(f"⏳ Waiting for the right time to post... Current time: {datetime.now().strftime('%H:%M')}")
            time.sleep(30)  # Check every 30 seconds
        
        # Randomize comment
        comment_text = random.choice(comments)
        
        # Try posting a comment, retry up to 3 times if it fails
        attempts = 0
        success = False
        while attempts < 3 and not success:
            success = post_comment(post_id, comment_text, access_token, location)
            if not success:
                attempts += 1
                delay = random.randint(10, 30)  # Short delay between retries
                print(f"⏳ Retrying after {delay} seconds...")
                time.sleep(delay)

        # If the token is expired, remove it and break the loop
        if is_token_expired(access_token):
            print("❌ Expired token detected. Please refresh your token.")
            if os.path.exists("token.txt"):
                os.remove("token.txt")  # Automatically remove expired token
            break  # Stop the script to prevent further actions with an expired token
        
        if not success:
            print(f"❌ Failed to post comment after 3 attempts on Post ID: {post_id}")
            continue  # Skip to the next post ID

        # Random delay between 60 to 120 seconds for smoother operation
        delay = random.randint(60, 120)
        print(f"⏳ Waiting for {delay} seconds before next comment...")
        time.sleep(delay)

    print("All comments posted successfully!")

if __name__ == "__main__":
    # Read data from files
    access_token = read_token()
    post_ids = read_post_ids()
    comments, location = read_comments_and_location()
    live_time = read_live_time()

    # Check if data was successfully retrieved from files
    if access_token and post_ids and comments and location and live_time:
        # Check if the token is expired before proceeding
        if is_token_expired(access_token):
            print("Please provide a valid token and try again.")
        else:
            # Start the commenting flow
            smooth_commenting_flow(access_token, post_ids, comments, location, live_time)
    else:
        print("Error: Could not load necessary data. Please check your files.")