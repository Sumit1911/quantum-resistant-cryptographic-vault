import { useState } from 'react'
import { api } from '../api/client'

export type BenchmarkConfig = {
  classical_algo: string
  pqc_algo: string
  operation: string
  iterations: number
  file_size_mb: number
}

export function useBenchmark() {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const run = async (config: BenchmarkConfig) => {
    setLoading(true)
    setError(null)
    try {
      const res = await api.post('/benchmark/run', config)
      setData(res.data)
    } catch {
      setError('Benchmark run failed. Check backend status and try again.')
    } finally {
      setLoading(false)
    }
  }

  return { data, loading, error, run }
}
