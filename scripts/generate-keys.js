#!/usr/bin/env node
/**
 * This script helps generate an Ed25519 key pair for use with the Warpcast MCP server.
 * It requires @noble/ed25519, axios, and qrcode-terminal packages.
 * 
 * Usage:
 * 1. npm install @noble/ed25519 axios qrcode-terminal
 * 2. node generate-keys.js
 */

const crypto = require('crypto');
const axios = require('axios');
const qrcode = require('qrcode-terminal');
const fs = require('fs');
const readline = require('readline');

// Create readline interface for user input
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

const askQuestion = (query) => new Promise((resolve) => rl.question(query, resolve));

// EIP-712 constants for Signed Key Request
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

async function main() {
  console.log('Warpcast Key Pair Generator');
  console.log('==========================');
  console.log('This script will help you generate and register an Ed25519 key pair with Warpcast.');
  console.log('');

  // Generate a random Ed25519 key pair
  const { publicKey, privateKey } = crypto.generateKeyPairSync('ed25519');
  const publicKeyBytes = publicKey.export({ format: 'raw', type: 'raw' });
  const privateKeyBytes = privateKey.export({ format: 'raw', type: 'raw' });

  // Convert to hex strings for storage
  const publicKeyHex = Buffer.from(publicKeyBytes).toString('hex');
  const privateKeyHex = Buffer.from(privateKeyBytes).toString('hex');

  console.log('Generated Ed25519 Key Pair:');
  console.log(`Public Key: 0x${publicKeyHex}`);
  console.log(`Private Key: 0x${privateKeyHex}`);
  console.log('');
  console.log('Important: Keep your private key secure! It should never be shared.');
  console.log('');

  // Ask if the user wants to proceed with registering the key with Warpcast
  const shouldRegister = await askQuestion('Do you want to register this key with Warpcast? (y/n): ');
  
  if (shouldRegister.toLowerCase() !== 'y') {
    console.log('');
    console.log('Key registration skipped. You can manually update your .env file with these credentials:');
    console.log('');
    console.log(`WARPCAST_FID=your_fid_here`);
    console.log(`WARPCAST_PRIVATE_KEY=${privateKeyHex}`);
    console.log(`WARPCAST_PUBLIC_KEY=${publicKeyHex}`);
    rl.close();
    return;
  }

  // Get user's FID and custody account details for signing
  console.log('');
  console.log('To register this key, you need your Farcaster ID (FID) and a way to sign messages from your custody account.');
  console.log('');
  
  const appFid = await askQuestion('Enter your FID: ');
  
  // Since signing with the custody account is complex and requires additional dependencies,
  // we'll just provide instructions for the user to complete this process
  console.log('');
  console.log('To complete the registration process, you need to:');
  console.log('1. Sign a message with your custody account');
  console.log('2. Submit the signature to the Warpcast API');
  console.log('3. Approve the request in the Warpcast app');
  console.log('');
  console.log('For detailed instructions, visit: https://docs.warpcast.com/docs/signer-requests');
  console.log('');
  
  // Update .env file with the new keys
  try {
    let envContent = '';
    if (fs.existsSync('.env')) {
      envContent = fs.readFileSync('.env', 'utf8');
    }
    
    // Replace or add the environment variables
    const updateEnvVar = (name, value) => {
      const regex = new RegExp(`^${name}=.*$`, 'm');
      if (regex.test(envContent)) {
        envContent = envContent.replace(regex, `${name}=${value}`);
      } else {
        envContent += `\n${name}=${value}`;
      }
    };
    
    updateEnvVar('WARPCAST_FID', appFid);
    updateEnvVar('WARPCAST_PRIVATE_KEY', privateKeyHex);
    updateEnvVar('WARPCAST_PUBLIC_KEY', publicKeyHex);
    
    fs.writeFileSync('.env', envContent);
    console.log('Updated .env file with your new credentials.');
  } catch (error) {
    console.error('Error updating .env file:', error);
    console.log('Please manually update your .env file with the following:');
    console.log(`WARPCAST_FID=${appFid}`);
    console.log(`WARPCAST_PRIVATE_KEY=${privateKeyHex}`);
    console.log(`WARPCAST_PUBLIC_KEY=${publicKeyHex}`);
  }
  
  rl.close();
}

main().catch(error => {
  console.error('Error:', error);
  rl.close();
});
