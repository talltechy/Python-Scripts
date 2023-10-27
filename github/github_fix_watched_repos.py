"""
This script updates the subscription settings for all repositories the user is watching on GitHub.
"""

import getpass
import webbrowser
import logging
import os
import requests


# Set up logging
log_file = os.path.join(os.path.dirname(__file__), 'log.txt')
logging.basicConfig(filename=log_file, level=logging.INFO)

print("To generate a personal access token in GitHub:\n"
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
      "If a token is ever compromised, you can go back to the token settings and revoke it.")

# Prompt the user for their GitHub username and personal access token
username = input('Enter your GitHub username: ')
token = getpass.getpass('Enter your GitHub token: ')

# Ask the user if they want to open the URL to create a personal access token in a browser
open_url = input('Do you want to open the URL to create a personal access token in a browser? (y/n): ')
if open_url.lower() == 'y':
    webbrowser.open('https://github.com/settings/tokens/new')

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
        'subscribed': True,
        'ignored': False,
        'reason': 'releases'  # Only get notifications for releases
    }

    RESPONSE = requests.put(subscription_url, headers=headers, json=subscription_settings, timeout=10)

    # Check if the request was successful
    if RESPONSE.status_code == 200:
        SUCCESS_MSG = 'Successfully updated settings for %s'
        print(SUCCESS_MSG % repo_name)
        logging.info(SUCCESS_MSG, repo_name)
    else:
        ERROR_MSG = 'Failed to update settings for %s'
        print(ERROR_MSG % repo_name)
        logging.error(ERROR_MSG, repo_name)
