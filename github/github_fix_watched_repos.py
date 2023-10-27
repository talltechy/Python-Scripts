"""
This script updates the subscription settings for all repositories the user is watching on GitHub.
"""

import getpass
import webbrowser
import logging
import os
import requests
from colorama import Fore, Style

# Set up logging
log_file = os.path.join(os.path.dirname(__file__), 'log.txt')
logging.basicConfig(filename=log_file, level=logging.INFO)

print(Fore.GREEN + "To generate a personal access token in GitHub:\n"
      "1. Sign in to your GitHub account.\n"
      "2. Click on your profile photo in the upper-right corner of any page.\n"
      "3. Click on `Settings` in the drop-down menu.\n"
      "4. In the left sidebar, click on `Developer settings`.\n"
      "5. Click on `Personal access tokens`.\n"
      "6. Click on `Generate new token`.\n"
      "7. Give your token a descriptive name in the `Note` field.\n"
      "8. Select the scopes, or permissions, you'd like to grant this token.\n"
      "   For this script, you'll need at least the `repo` scope.\n"
      "9. Click `Generate token`.\n"
      "10. After generating the token, make sure to copy it. You won't be able to see it again!\n"
      "Remember to keep your tokens secret; treat them just like passwords.\n"
      "If a token is ever compromised, you can go back to the token settings and revoke it." + Style.RESET_ALL)

# Ask the user if they want to open the URL to create a personal access token in a browser
open_url = input(Fore.YELLOW + 'Do you want to open the URL to create a personal access token in a browser? (y/n): ' + Style.RESET_ALL)
if open_url.lower() == 'y':
    webbrowser.open('https://github.com/settings/tokens/new')

# Prompt the user for their GitHub username and personal access token
username = input(Fore.YELLOW + 'Enter your GitHub username: ' + Style.RESET_ALL)
token = getpass.getpass(Fore.YELLOW + 'Enter your GitHub token: ' + Style.RESET_ALL)

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
repos = response.json()['items']

# Loop over the repositories
for repo in repos:
    # Get the repo's owner and name
    owner = repo['owner']['login']
    repo_name = repo['name']

    # Change the subscription settings
    subscription_url = f'https://api.github.com/repos/{owner}/{repo_name}/subscription'
    subscription_settings = {}

    # Prompt the user for subscription settings
    print(Fore.CYAN + f'Subscription settings for {repo_name}:' + Style.RESET_ALL)
    subscription_settings['subscribed'] = input(Fore.YELLOW + 'Subscribe to notifications? (y/n): ' + Style.RESET_ALL).lower() == 'y'
    subscription_settings['ignored'] = input(Fore.YELLOW + 'Ignore notifications? (y/n): ' + Style.RESET_ALL).lower() == 'y'
    subscription_settings['reason'] = input(Fore.YELLOW + 'Reason for notifications (e.g. releases, all, etc.): ' + Style.RESET_ALL)

    response = requests.put(subscription_url, headers=headers, json=subscription_settings, timeout=10)

    # Check if the request was successful
    if response.status_code == 200:
        SUCCESS_MSG = Fore.GREEN + 'Successfully updated settings for %s' + Style.RESET_ALL
        print(SUCCESS_MSG % repo_name)
        logging.info(SUCCESS_MSG, repo_name)
    else:
        ERROR_MSG = Fore.RED + 'Failed to update settings for %s' + Style.RESET_ALL
        print(ERROR_MSG % repo_name)
        logging.error(ERROR_MSG, repo_name)
