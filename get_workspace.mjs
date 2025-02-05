import fs from 'fs/promises';

/**
 * This program prints the current workspace using credentials stored in files
 */

const clientIdFile = 'client_id.txt';
const credsFile = 'creds.json'
const aacURLFile = 'aac_url.txt'

async function main() {
  const accessToken = await getAccessToken();
  const clientId = (await fs.readFile(clientIdFile)).toString().trim();
  const aacURL = (await fs.readFile(aacURLFile)).toString().trim();
  console.log(await getCurrentWorkspace(aacURL, accessToken, clientId));
}

main();

/**
 * This function reads the access and refresh token from the credentials file, 
 * refreshes the access token, 
 * and writes the new tokens back to the credentials file
 * 
 * It returns a new access token that can be used to call APIs
 */
async function getAccessToken() {
  // Load the credentials from their JSON file
  const oldCreds = JSON.parse(await fs.readFile(credsFile)); 

  // Get the second part of the access token, which is its payload
  const payload = oldCreds.access_token.split('.')[1] 

  // Decode the base64-encoded access token
  const info = JSON.parse(atob(payload)) 

  // Create the body for the refresh request
  const body = new URLSearchParams({
    grant_type: 'refresh_token',
    refresh_token: oldCreds.refresh_token,
    client_id: info.client_id,
  });

  // Make the refresh request
  const response = await fetch(`${info.iss}/token`, {
    body,
    method: 'POST'
  });

  const newCreds = await response.json();

  // Overwrite the contents of the credentials file with the response of the refresh request, which includes the new access and refresh tokens
  fs.writeFile(credsFile, JSON.stringify(newCreds));

  return newCreds.access_token;
}

/**
 * Gets the current workspace, and returns it as an object
 */
async function getCurrentWorkspace(aacURL, accessToken, clientId) {

  // These headers are necessary in every request to the AAC API
  const headers = {
    'Authorization': `Bearer ${accessToken}`,
    'x-client-id': clientId,
    'User-Agent': 'myApp', // Describe your application here
  }

  const response = await fetch(`${aacURL}/iam/v1/workspaces/current`, { headers })

  return await response.json()
}