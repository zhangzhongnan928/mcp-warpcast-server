import * as crypto from 'crypto';
import * as dotenv from 'dotenv';

dotenv.config();

// Environment variables
const FID = process.env.WARPCAST_FID;
const PRIVATE_KEY = process.env.WARPCAST_PRIVATE_KEY;
const PUBLIC_KEY = process.env.WARPCAST_PUBLIC_KEY;

/**
 * Generates an authentication token for Warpcast API
 * This is a simplified implementation of the Ed25519 signing process described
 * in the Warpcast API documentation. Production uses should consider using
 * the proper Farcaster SDK libraries for token generation.
 */
export async function generateAuthToken(): Promise<string> {
  if (!FID || !PRIVATE_KEY || !PUBLIC_KEY) {
    throw new Error('Missing required environment variables for authentication');
  }

  try {
    // Create the header
    const header = {
      fid: Number(FID),
      type: 'app_key',
      key: PUBLIC_KEY
    };
    const encodedHeader = Buffer.from(JSON.stringify(header)).toString('base64url');

    // Create the payload (5 minutes expiration)
    const payload = { 
      exp: Math.floor(Date.now() / 1000) + 300 
    };
    const encodedPayload = Buffer.from(JSON.stringify(payload)).toString('base64url');

    // Message to sign
    const message = `${encodedHeader}.${encodedPayload}`;
    
    // Sign the message using Ed25519
    // NOTE: In production, use the proper Farcaster SDK for signing
    const privateKeyBuffer = Buffer.from(PRIVATE_KEY, 'hex');
    const messageBuffer = Buffer.from(message, 'utf-8');
    
    // Create a signing key pair
    const { privateKey } = crypto.generateKeyPairSync('ed25519', {
      privateKey: {
        format: 'raw',
        key: privateKeyBuffer
      }
    });
    
    // Sign the message
    const signature = crypto.sign(null, messageBuffer, privateKey);
    const encodedSignature = Buffer.from(signature).toString('base64url');

    // Combine to form the complete JWT-like token
    return `${encodedHeader}.${encodedPayload}.${encodedSignature}`;
  } catch (error) {
    console.error('Error generating auth token:', error);
    throw new Error('Failed to generate authentication token');
  }
}

/**
 * Note: This is a simplified implementation for demonstration purposes.
 * In production, you should use the proper Farcaster SDK for authentication.
 * 
 * From the documentation:
 * ```
 * import { NobleEd25519Signer } from "@farcaster/hub-nodejs";
 * 
 * // private / public keys of an App Key you are holding for an FID
 * const fid = 6841; //replace
 * const privateKey = 'secret'; // replace
 * const publicKey = 'pubkey'; // replace
 * const signer = new NobleEd25519Signer(new Uint8Array(Buffer.from(privateKey)));
 * 
 * const header = {
 *   fid,
 *   type: 'app_key',
 *   key: publicKey
 * };
 * const encodedHeader = Buffer.from(JSON.stringify(header)).toString('base64url');
 * 
 * const payload = { exp: Math.floor(Date.now() / 1000) + 300 }; // 5 minutes
 * const encodedPayload = Buffer.from(JSON.stringify(payload)).toString('base64url');
 * 
 * const signatureResult = await signer.signMessageHash(Buffer.from(`${encodedHeader}.${encodedPayload}`, 'utf-8'));
 * if (signatureResult.isErr()) {
 *   throw new Error("Failed to sign message");
 * }
 * 
 * const encodedSignature = Buffer.from(signatureResult.value).toString("base64url");
 * 
 * const authToken = encodedHeader + "." + encodedPayload + "." + encodedSignature;
 * ```
 */