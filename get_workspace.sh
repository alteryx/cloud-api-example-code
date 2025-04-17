#!/bin/bash

# This program prints the current workspace using credentials stored in a file

# Requirements: jq, curl

api_project_id_file="api_project_id.txt"
creds_file="creds.json"
aac_url_file="aac_url.txt"

# Main function
main() {
  api_project_id=$(cat $api_project_id_file | xargs)
  access_token=$(get_access_token)
  aac_url=$(cat $aac_url_file | xargs)
  echo $(get_current_workspace "$access_token" "$api_project_id" "$aac_url")
}

# Function to get the access token (with refresh logic)
get_access_token() {

  # Read the old creds.json and extract the access token and refresh token
  old_access_token=$(cat $creds_file | jq -r '.access_token')
  refresh_token=$(cat $creds_file | jq -r '.refresh_token')

  # Decode the payload from the access token
  payload=$(echo "$(echo "$old_access_token" | cut -d '.' -f2)==" | base64 --decode)
  client_id_from_token=$(echo "$payload" | jq -r '.client_id')
  iss=$(echo "$payload" | jq -r '.iss')

  # Prepare the body for the refresh request
  body="grant_type=refresh_token&refresh_token=$refresh_token&client_id=$client_id_from_token"

  # Make the refresh request using curl
  new_creds=$(curl -s -X POST "$iss/token" \
    -d "$body" \
    -H "Content-Type: application/x-www-form-urlencoded")

  # Extract new access token and refresh token
  new_access_token=$(echo "$new_creds" | jq -r '.access_token')

  # Save the new tokens back into creds.json
  echo "$new_creds" > "$creds_file"

  echo "$new_access_token"
}

# Function to get the current workspace using the access token
get_current_workspace() {

  access_token="$1"
  api_project_id="$2"
  aac_url="$3"

  # Make the request to get the current workspace using curl
  response=$(curl -s -X GET "$aac_url/iam/v1/workspaces/current" \
    -H "Authorization: Bearer $access_token" \
    -H "x-api-project-id: $api_project_id" \
    -H "User-Agent: myApp")  # Describe your application here

  # Output the response (current workspace)
  echo "$response" | jq
}

# Run the main function
main
