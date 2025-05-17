import axios from 'axios';

// Create an axios instance 
const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Players API
export const playersApi = {
  // Get all players with optional pagination
  getAllPlayers: async (params?: { limit?: number; offset?: number; order?: string }) => {
    const response = await api.get('/players', { params });
    return response.data;
  },
  
  // Get a specific player's stats
  getPlayerStats: async (playerName: string, seasonId?: string) => {
    const params = seasonId ? { season_id: seasonId } : {};
    const response = await api.get(`/players/${encodeURIComponent(playerName)}/stats`, { params });
    return response.data;
  },
  
  // Get a player's career stats
  getPlayerCareerStats: async (playerName: string) => {
    const response = await api.get(`/players/${encodeURIComponent(playerName)}/career_stats`);
    return response.data;
  }
};

export default api;