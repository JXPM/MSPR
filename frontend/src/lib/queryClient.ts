import { QueryClient } from '@tanstack/react-query'

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60_000,           // 1 minute avant refetch auto
      gcTime: 5 * 60_000,          // 5 minutes en cache
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})
