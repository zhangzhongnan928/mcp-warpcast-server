import axios from 'axios';
import * as dotenv from 'dotenv';

dotenv.config();

const API_BASE_URL = 'https://api.warpcast.com';

// Create an axios instance with default configuration
const warpcastApi = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
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

export interface Channel {
  id: string;
  url: string;
  name: string;
  description: string;
  imageUrl?: string;
  headerImageUrl?: string;
  leadFid: number;
  moderatorFids: number[];
  createdAt: number;
  followerCount: number;
  memberCount: number;
  pinnedCastHash?: string;
  publicCasting: boolean;
  externalLink?: {
    title: string;
    url: string;
  };
}

export interface ApiResponse<T> {
  result: {
    data: T;
    next?: {
      cursor: string;
    };
  };
}

interface PaginationOptions {
  cursor?: string;
  limit?: number;
}

/**
 * Post a new cast to Warpcast
 * @param text The content of the cast (max 320 characters)
 * @param authToken The authentication token
 * @returns The created cast
 */
export async function postCast(text: string, authToken: string): Promise<Cast> {
  try {
    if (text.length > 320) {
      text = text.substring(0, 320); // Truncate to 320 characters
    }

    const response = await warpcastApi.post('/v2/casts', 
      { text },
      { 
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      }
    );

    return response.data.result.cast;
  } catch (error) {
    console.error('Error posting cast:', error);
    throw new Error('Failed to post cast to Warpcast');
  }
}

/**
 * Get recent casts from a specific user
 * @param username The username to fetch casts for
 * @param options Pagination options
 * @returns List of casts
 */
export async function getUserCasts(username: string, options: PaginationOptions = {}): Promise<Cast[]> {
  try {
    const { cursor, limit = 10 } = options;
    let url = `/v2/user-casts?username=${username}&limit=${limit}`;
    
    if (cursor) {
      url += `&cursor=${cursor}`;
    }
    
    const response = await warpcastApi.get<{result: {casts: Cast[], next?: {cursor: string}}}>(url);
    return response.data.result.casts;
  } catch (error) {
    console.error(`Error fetching casts for user ${username}:`, error);
    throw new Error(`Failed to fetch casts for ${username}`);
  }
}

/**
 * Search for casts by query string
 * @param query The search query
 * @param options Pagination options
 * @returns List of matching casts
 */
export async function searchCasts(query: string, options: PaginationOptions = {}): Promise<Cast[]> {
  try {
    const { cursor, limit = 10 } = options;
    let url = `/v2/search?q=${encodeURIComponent(query)}&limit=${limit}`;
    
    if (cursor) {
      url += `&cursor=${cursor}`;
    }
    
    const response = await warpcastApi.get<{result: {casts: Cast[], next?: {cursor: string}}}>(url);
    return response.data.result.casts;
  } catch (error) {
    console.error(`Error searching casts for "${query}":`, error);
    throw new Error(`Failed to search for casts containing "${query}"`);
  }
}

/**
 * Get trending casts
 * @param options Pagination options
 * @returns List of trending casts
 */
export async function getTrendingCasts(options: PaginationOptions = {}): Promise<Cast[]> {
  try {
    const { cursor, limit = 10 } = options;
    let url = `/v2/trending-casts?limit=${limit}`;
    
    if (cursor) {
      url += `&cursor=${cursor}`;
    }
    
    const response = await warpcastApi.get<{result: {casts: Cast[], next?: {cursor: string}}}>(url);
    return response.data.result.casts;
  } catch (error) {
    console.error('Error fetching trending casts:', error);
    throw new Error('Failed to fetch trending casts');
  }
}

/**
 * Get all channels
 * @returns List of all channels
 */
export async function getAllChannels(): Promise<Channel[]> {
  try {
    const response = await warpcastApi.get<{result: {channels: Channel[]}}>(
      '/v2/all-channels'
    );
    return response.data.result.channels;
  } catch (error) {
    console.error('Error fetching all channels:', error);
    throw new Error('Failed to fetch channels');
  }
}

/**
 * Get a specific channel by ID
 * @param channelId The channel ID
 * @returns Channel data
 */
export async function getChannel(channelId: string): Promise<Channel> {
  try {
    const response = await warpcastApi.get<{result: {channel: Channel}}>(
      `/v1/channel?channelId=${channelId}`
    );
    return response.data.result.channel;
  } catch (error) {
    console.error(`Error fetching channel ${channelId}:`, error);
    throw new Error(`Failed to fetch channel ${channelId}`);
  }
}

/**
 * Get casts from a specific channel
 * @param channelId The channel ID
 * @param options Pagination options
 * @returns List of channel casts
 */
export async function getChannelCasts(channelId: string, options: PaginationOptions = {}): Promise<Cast[]> {
  try {
    const { cursor, limit = 10 } = options;
    let url = `/v2/channel-casts?channelId=${channelId}&limit=${limit}`;
    
    if (cursor) {
      url += `&cursor=${cursor}`;
    }
    
    const response = await warpcastApi.get<{result: {casts: Cast[], next?: {cursor: string}}}>(url);
    return response.data.result.casts;
  } catch (error) {
    console.error(`Error fetching casts for channel ${channelId}:`, error);
    throw new Error(`Failed to fetch casts for channel ${channelId}`);
  }
}

/**
 * Follow a channel
 * @param channelId The channel ID to follow
 * @param authToken The authentication token
 * @returns Success status
 */
export async function followChannel(channelId: string, authToken: string): Promise<boolean> {
  try {
    const response = await warpcastApi.post(
      '/fc/channel-follows',
      { channelId },
      {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      }
    );
    return response.data.success === true;
  } catch (error) {
    console.error(`Error following channel ${channelId}:`, error);
    throw new Error(`Failed to follow channel ${channelId}`);
  }
}

/**
 * Unfollow a channel
 * @param channelId The channel ID to unfollow
 * @param authToken The authentication token
 * @returns Success status
 */
export async function unfollowChannel(channelId: string, authToken: string): Promise<boolean> {
  try {
    const response = await warpcastApi.delete(
      '/fc/channel-follows',
      {
        headers: {
          'Authorization': `Bearer ${authToken}`
        },
        data: { channelId }
      }
    );
    return response.data.success === true;
  } catch (error) {
    console.error(`Error unfollowing channel ${channelId}:`, error);
    throw new Error(`Failed to unfollow channel ${channelId}`);
  }
}

export default {
  postCast,
  getUserCasts,
  searchCasts,
  getTrendingCasts,
  getAllChannels,
  getChannel,
  getChannelCasts,
  followChannel,
  unfollowChannel
};