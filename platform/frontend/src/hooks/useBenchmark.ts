import { useState } from 'react'
import { api } from '../api/client'
import { waitRandomSimulationDelay } from '../utils/simulationDelay'

export type BenchmarkConfig = {
  experiment_family: 'kem' | 'signature' | 'encryption'
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
      await waitRandomSimulationDelay()
      const res = await api.post('/benchmark/run', config)
      setData(res.data)
    } catch (err: any) {
      const detail = err?.response?.data?.detail
      setError(detail || 'Benchmark run failed. Check backend status and try again.')
    } finally {
      setLoading(false)
    }
  }

  return { data, loading, error, run }
}
