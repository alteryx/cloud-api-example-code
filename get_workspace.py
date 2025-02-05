import json
import base64
import urllib.parse
import urllib.request

"""
This program prints the current workspace using credentials stored in a file
"""

"""
Get a new Client ID here: https://us1.alteryxcloud.com/cloud-portal/library/alteryx-io
This uniquely identifies your application
"""
client_id_file = 'client_id.txt'
creds_file = 'creds.json'
aac_url_file = 'aac_url.txt'

def main():
  with open(client_id_file) as f:
    client_id = f.read().rstrip()
  access_token = get_access_token()
  with open(aac_url_file) as f:
    aac_url = f.read().rstrip()
  print(get_current_workspace(aac_url, access_token, client_id))

def get_access_token():
  """
  This function reads the access and refresh token from the credentials file, 
  refreshes the access token, 
  and writes the new tokens back to the credentials file

  It returns a new access token that can be used to call APIs
  """
  # Load the credentials from their JSON file
  with open(creds_file, 'r') as f:
    old_creds = json.load(f);
  
  # Get the second part of the access token, which is its payload
  payload = old_creds['access_token'].split('.')[1]

  # Decode the base64-encoded access token
  info = json.loads(base64.b64decode(f'{payload}===='))

  # Create the body for the refresh request
  body = {
    'grant_type': 'refresh_token',
    'refresh_token': old_creds['refresh_token'],
    'client_id': info['client_id'],
  }

  # URL encode the body for the refresh request
  encoded_body = urllib.parse.urlencode(body).encode()

  # Make the refresh request
  request = urllib.request.Request(f"{info['iss']}/token", data=encoded_body, method='POST')
  with urllib.request.urlopen(request) as response:
    new_creds = json.load(response)

  # Overwrite the contents of the credneitals file with the new access and refresh tokens
  with open(creds_file, 'w') as f:
      json.dump(new_creds, f)

  return new_creds['access_token']
  
def get_current_workspace(aac_url, access_token, client_id):
  """
  Given an access token and client id,
  Gets the current workspace, and returns it as an object
  """
  # These headers are necessary in every request to the AAC API
  headers = {
    'Authorization': f'Bearer {access_token}',
    'x-client-id': client_id,
    'User-Agent': 'my_app', # Descirbe your application here
  }

  request = urllib.request.Request(f'{aac_url}/iam/v1/workspaces/current', headers=headers)
  with urllib.request.urlopen(request) as response:
    return json.load(response)
  
if __name__ == '__main__':
  main()