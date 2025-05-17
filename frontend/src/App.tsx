
import React from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import PlayerList from './components/PlayerList'

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
})

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-gray-100 p-6">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-center text-blue-800">NBA Data Explorer</h1>
        </header>
        
        <main className="max-w-4xl mx-auto">
          <PlayerList limit={10} />
        </main>
      </div>
    </QueryClientProvider>
  )
}

export default App