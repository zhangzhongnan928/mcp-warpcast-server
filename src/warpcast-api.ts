import axios from 'axios';
import * as dotenv from 'dotenv';

dotenv.config();

const API_KEY = process.env.WARPCAST_API_KEY;
const API_SECRET = process.env.WARPCAST_API_SECRET;

// Base API URL for Warpcast API
const API_BASE_URL = 'https://api.warpcast.com/v2';

// Create an axios instance with default configuration
const warpcastApi = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${API_KEY}`,
    'X-API-Secret': API_SECRET
  }
});

// Define interfaces for the API responses
export interface Cast {
  hash: string;
  threadHash?: string;
  parentHash?: string;
  author: {
    fid: number;
    username: string;
    displayName: string;
    pfp: {
      url: string;
    };
    profile: {
      bio: string;
    };
  };
  text: string;
  timestamp: string;
  reactions: {
    likes: number;
    recasts: number;
    replies: number;
  };
  embeds?: any[];
}

export interface ApiResponse<T> {
  result: {
    data: T;
    next?: {
      cursor: string;
    };
  };
}

/**
 * Post a new cast to Warpcast
 * @param text The content of the cast (max 320 characters)
 * @returns The created cast
 */
export async function postCast(text: string): Promise<Cast> {
  try {
    if (text.length > 320) {
      text = text.substring(0, 320); // Truncate to 320 characters
    }

    const response = await warpcastApi.post<ApiResponse<Cast>>('/casts', {
      text
    });

    return response.data.result.data;
  } catch (error) {
    console.error('Error posting cast:', error);
    throw new Error('Failed to post cast to Warpcast');
  }
}

/**
 * Get recent casts from a specific user
 * @param username The username to fetch casts for
 * @param limit Maximum number of casts to return
 * @returns List of casts
 */
export async function getUserCasts(username: string, limit: number = 10): Promise<Cast[]> {
  try {
    const response = await warpcastApi.get<ApiResponse<Cast[]>>(`/user-casts?username=${username}&limit=${limit}`);
    return response.data.result.data;
  } catch (error) {
    console.error(`Error fetching casts for user ${username}:`, error);
    throw new Error(`Failed to fetch casts for ${username}`);
  }
}

/**
 * Search for casts by query string
 * @param query The search query
 * @param limit Maximum number of results to return
 * @returns List of matching casts
 */
export async function searchCasts(query: string, limit: number = 10): Promise<Cast[]> {
  try {
    const response = await warpcastApi.get<ApiResponse<Cast[]>>(`/search?q=${encodeURIComponent(query)}&limit=${limit}`);
    return response.data.result.data;
  } catch (error) {
    console.error(`Error searching casts for "${query}":`, error);
    throw new Error(`Failed to search for casts containing "${query}"`);
  }
}

/**
 * Get trending casts
 * @param limit Maximum number of casts to return
 * @returns List of trending casts
 */
export async function getTrendingCasts(limit: number = 10): Promise<Cast[]> {
  try {
    const response = await warpcastApi.get<ApiResponse<Cast[]>>(`/trending-casts?limit=${limit}`);
    return response.data.result.data;
  } catch (error) {
    console.error('Error fetching trending casts:', error);
    throw new Error('Failed to fetch trending casts');
  }
}

export default {
  postCast,
  getUserCasts,
  searchCasts,
  getTrendingCasts
};