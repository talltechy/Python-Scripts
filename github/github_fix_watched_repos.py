"""
This script updates the subscription settings for all repositories the user is watching on GitHub.
"""

import getpass
import webbrowser
import logging
import os
import requests
from colorama import just_fix_windows_console

# use Colorama to make Termcolor work on Windows too
just_fix_windows_console()

# Set up logging
log_file = os.path.join(os.path.dirname(__file__), 'log.txt')
logging.basicConfig(filename=log_file, level=logging.INFO)

# ANSI color codes
GREEN = '\033[32m'
YELLOW = '\033[33m'
RED = '\033[31m'
RESET = '\033[0m'

print(f"{GREEN}To generate a personal access token in GitHub:\n"
      "1. Sign in to your GitHub account.\n"
      f"2. Click on your profile photo in the upper-right corner of any page.\n"
      f"3. Click on {YELLOW}'Settings'{RESET} in the drop-down menu.\n"
      f"4. In the left sidebar, click on {YELLOW}'Developer settings'{RESET}.\n"
      f"5. Click on {YELLOW}'Personal access tokens'{RESET}.\n"
      f"6. Click on {YELLOW}'Generate new token'{RESET}.\n"
      f"7. Give your token a descriptive name in the {YELLOW}'Note'{RESET} field.\n"
      f"8. Select the scopes, or permissions, you'd like to grant this token.\n"
      f"   For this script, you'll need at least the {YELLOW}'repo'{RESET} scope.\n"
      f"9. Click {YELLOW}'Generate token'{RESET}.\n"
      "10. After generating the token, make sure to copy it. You won't be able to see it again!\n"
      "Remember to keep your tokens secret; treat them just like passwords.\n"
      "If a token is ever compromised, you can go back to the token settings and revoke it." +
      RESET)

# Ask the user if they want to open the URL to create a personal access token in a browser
open_url = input(f"{YELLOW}Do you want to open the URL to create a personal access token in a browser? (y/n): "
                 f"{RESET}").strip()
if open_url.lower() == 'y':
    webbrowser.open('https://github.com/settings/tokens/new')

# Prompt the user for their GitHub username and personal access token
username = input(f"{YELLOW}Enter your GitHub username: {RESET}")
token = getpass.getpass(f"{YELLOW}Enter your GitHub token: {RESET}")

# Log input
logging.info('Username: %s', username)
logging.info('Open URL: %s', open_url)

# The headers for the API request
headers = {
    'Accept': 'application/vnd.github.v3+json',
    'Authorization': f'token {token}',
}

# Get the list of repositories you're watching
response = requests.get(f'https://api.github.com/users/{username}/subscriptions',
                        headers=headers, timeout=10)
repos = response.json()

# Loop over the repositories
for repo in repos:
    # Get the repo's owner and name
    owner = repo['owner']['login']
    repo_name = repo['name']

    # Change the subscription settings
    subscription_url = f'https://api.github.com/repos/{owner}/{repo_name}/subscription'
    subscription_settings = {
        'subscribed': input(f"{YELLOW}Subscribe to notifications? (y/n): {RESET}").lower() == 'y',
        'ignored': input(f"{YELLOW}Ignore notifications? (y/n): {RESET}").lower() == 'y',
        'reason': input(f"{YELLOW}Reason for notifications (e.g. releases, all, etc.): {RESET}"),
    }

    response = requests.put(subscription_url, headers=headers, json=subscription_settings, timeout=10)

    # Check if the request was successful
    if response.status_code == 200:
        SUCCESS_MSG = f"{GREEN}Successfully updated settings for {repo_name}{RESET}"
        print(SUCCESS_MSG)
        logging.info(SUCCESS_MSG, repo_name)
    else:
        ERROR_MSG = f"{RED}Failed to update settings for {repo_name}{RESET}"
        print(ERROR_MSG)
        logging.error(ERROR_MSG, repo_name)
