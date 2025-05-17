import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { playersApi } from '../services/api';

interface PlayerListProps {
  limit?: number;
  initialOffset?: number;
}

interface PlayerListResponse {
  players: string[];
  count: number;
  total: number;
  offset: number;
  limit: number | null;
}

const PlayerList: React.FC<PlayerListProps> = ({ limit = 20, initialOffset = 0 }) => {
  const [offset, setOffset] = useState(initialOffset);
  
  const { data, isLoading, isError, error } = useQuery<PlayerListResponse>({
    queryKey: ['players', limit, offset],
    queryFn: () => playersApi.getAllPlayers({ limit, offset }),
  });

  if (isLoading) {
    return (
      <div className="p-4">
        <p className="text-lg font-medium">Loading player data...</p>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="p-4 bg-red-100 border border-red-300 rounded-md">
        <p className="text-red-700">Error loading players: {(error as Error).message}</p>
      </div>
    );
  }

  const handlePrevPage = () => {
    setOffset(Math.max(0, offset - limit));
  };

  const handleNextPage = () => {
    if (data && offset + limit < data.total) {
      setOffset(offset + limit);
    }
  };

  return (
    <div className="bg-white shadow-md rounded-lg p-6">
      <h2 className="text-2xl font-bold mb-4">NBA Players</h2>
      
      <div className="mb-4">
        <p className="text-gray-600">
          Showing {data?.count} of {data?.total} players
        </p>
      </div>
      
      <ul className="divide-y divide-gray-200">
        {data?.players.map((player, index) => (
          <li key={index} className="py-3 flex items-center">
            <span className="font-medium">{player}</span>
          </li>
        ))}
      </ul>
      
      <div className="mt-6 flex justify-between">
        <button
          onClick={handlePrevPage}
          disabled={offset === 0}
          className="px-4 py-2 bg-blue-500 text-white rounded disabled:bg-gray-300"
        >
          Previous
        </button>
        
        <button
          onClick={handleNextPage}
          disabled={!data || offset + limit >= data.total}
          className="px-4 py-2 bg-blue-500 text-white rounded disabled:bg-gray-300"
        >
          Next
        </button>
      </div>
    </div>
  );
};

export default PlayerList;