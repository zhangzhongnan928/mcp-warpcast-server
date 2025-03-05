# Warpcast MCP Server

A Model Context Protocol (MCP) server for Warpcast integration that allows you to use Claude to interact with your Warpcast account.

## Features

- Post casts to your Warpcast account
- Read casts from Warpcast
- Search casts by keyword or hashtag
- Browse and interact with channels
- Follow/unfollow channels
- Get trending casts

## Setup

1. Clone this repository
   ```bash
   git clone https://github.com/zhangzhongnan928/mcp-warpcast-server.git
   cd mcp-warpcast-server
   ```

2. Install dependencies
   ```bash
   npm install
   ```

3. Generate API Keys and Configure Authentication

   This MCP server provides a helper script to generate the necessary Ed25519 key pair:

   ```bash
   npm run generate-keys
   ```

   Follow the prompts to:
   - Generate a random Ed25519 key pair
   - Save the keys to your `.env` file
   - Get instructions for registering the key with Warpcast

   Alternatively, if you prefer to set things up manually:

   ### Option 1: Using Signed Key Requests

   1. Generate an Ed25519 key pair
   2. Use the Warpcast Signed Key Request API to ask for permission to sign messages on behalf of your account
   3. Complete the authorization in the Warpcast app

   Here's an example implementation:

   ```typescript
   import * as ed from '@noble/ed25519';
   import { mnemonicToAccount, signTypedData } from 'viem/accounts';
   import axios from 'axios';

   // Generate a keypair
   const privateKey = ed.utils.randomPrivateKey();
   const publicKeyBytes = await ed.getPublicKey(privateKey);
   const key = '0x' + Buffer.from(publicKeyBytes).toString('hex');

   // EIP-712 domain and types for SignedKeyRequest
   const SIGNED_KEY_REQUEST_VALIDATOR_EIP_712_DOMAIN = {
     name: 'Farcaster SignedKeyRequestValidator',
     version: '1',
     chainId: 10,
     verifyingContract: '0x00000000fc700472606ed4fa22623acf62c60553',
   };

   const SIGNED_KEY_REQUEST_TYPE = [
     { name: 'requestFid', type: 'uint256' },
     { name: 'key', type: 'bytes' },
     { name: 'deadline', type: 'uint256' },
   ];

   // Generate a Signed Key Request signature
   const appFid = process.env.APP_FID;
   const account = mnemonicToAccount(process.env.APP_MNEMONIC);

   const deadline = Math.floor(Date.now() / 1000) + 86400; // signature is valid for 1 day
   const signature = await account.signTypedData({
     domain: SIGNED_KEY_REQUEST_VALIDATOR_EIP_712_DOMAIN,
     types: {
       SignedKeyRequest: SIGNED_KEY_REQUEST_TYPE,
     },
     primaryType: 'SignedKeyRequest',
     message: {
       requestFid: BigInt(appFid),
       key,
       deadline: BigInt(deadline),
     },
   });

   // Create a Signed Key Request
   const warpcastApi = 'https://api.warpcast.com';
   const { token, deeplinkUrl } = await axios
     .post(`${warpcastApi}/v2/signed-key-requests`, {
       key,
       requestFid: appFid,
       signature,
       deadline,
     })
     .then((response) => response.data.result.signedKeyRequest);

   console.log('Deep link URL:', deeplinkUrl);
   console.log('Open this URL on your mobile device with Warpcast installed to authorize this key');
   ```

   ### Option 2: Using an Existing App Key

   If you already have an App Key set up for your Farcaster account, you can use the FID, private key, and public key directly.

4. Build the server
   ```bash
   npm run build
   ```

5. Configure Claude for Desktop to use this server

## Configuration with Claude for Desktop

Add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "warpcast": {
      "command": "node",
      "args": [
        "/absolute/path/to/mcp-warpcast-server/build/index.js"
      ],
      "env": {
        "WARPCAST_FID": "your_fid_here",
        "WARPCAST_PRIVATE_KEY": "your_private_key_here",
        "WARPCAST_PUBLIC_KEY": "your_public_key_here"
      }
    }
  }
}
```

Replace `/absolute/path/to/mcp-warpcast-server` with the actual absolute path to where you cloned this repository, and update the environment variables with your actual credentials.

## Usage

Once configured, you can ask Claude to:

- "Post a cast about [topic]"
- "Read the latest casts from [username]"
- "Search for casts about [topic]"
- "Show me trending casts on Warpcast"
- "Show me popular channels on Warpcast"
- "Get casts from the [channel] channel"
- "Follow the [channel] channel for me"

## Available Tools

This MCP server provides several tools that Claude can use:

1. **post-cast**: Create a new post on Warpcast (max 320 characters)
2. **get-user-casts**: Retrieve recent casts from a specific user
3. **search-casts**: Search for casts by keyword or phrase
4. **get-trending-casts**: Get the currently trending casts on Warpcast
5. **get-all-channels**: List available channels on Warpcast
6. **get-channel**: Get information about a specific channel
7. **get-channel-casts**: Get casts from a specific channel
8. **follow-channel**: Follow a channel
9. **unfollow-channel**: Unfollow a channel

## Authentication Notes

This server uses Warpcast's App Key authentication method, which requires an Ed25519 key pair registered with your Farcaster account. The authentication flow is:

1. Create a header containing your FID and public key
2. Create a payload with an expiration time
3. Sign the header and payload using your private key
4. Use the resulting token for API calls

In production applications, it's recommended to use the official Farcaster SDK for generating authentication tokens.

## Security Considerations

- Keep your private key secure and never share it
- Consider rotating your keys periodically
- The server logs authentication errors to help with debugging

## Troubleshooting

If you encounter issues:

1. Check that your environment variables are set correctly
2. Ensure your keys are properly registered with your Farcaster account
3. Check Claude for Desktop logs for any errors
4. Verify that your Warpcast account has the necessary permissions

## License

MIT
