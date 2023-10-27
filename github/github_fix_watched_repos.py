"""
This script updates the subscription settings for all repositories the user is watching on GitHub.
"""

import getpass
import requests

# To generate a personal access token in GitHub:
# 1. Sign in to your GitHub account.
# 2. Click on your profile photo in the upper-right corner of any page.
# 3. Click on `Settings` in the drop-down menu.
# 4. In the left sidebar, click on `Developer settings`.
# 5. Click on `Personal access tokens`.
# 6. Click on `Generate new token`.
# 7. Give your token a descriptive name in the `Note` field.
# 8. Select the scopes, or permissions, you'd like to grant this token.
#    For this script, you'll need at least the `repo` scope.
# 9. Click `Generate token`.
# 10. After generating the token, make sure to copy it. You won't be able to see it again!
# Remember to keep your tokens secret; treat them just like passwords.
# If a token is ever compromised, you can go back to the token settings and revoke it.

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

    response = requests.put(subscription_url, headers=headers, json=subscription_settings, timeout=10)

    # Check if the request was successful
    if response.status_code == 200:
        print(f'Successfully updated settings for {repo_name}')
    else:
        print(f'Failed to update settings for {repo_name}')
