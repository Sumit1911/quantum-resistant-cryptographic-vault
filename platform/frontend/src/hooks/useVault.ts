import { useState } from 'react'
import { api } from '../api/client'

export function useVault() {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const encrypt = async (plaintext: string, algorithm: string, signing: string) => {
    setLoading(true)
    setError(null)
    try {
      const res = await api.post('/vault/encrypt', { plaintext, algorithm, signing })
      setData(res.data)
    } catch {
      setError('Vault instrumentation request failed.')
    } finally {
      setLoading(false)
    }
  }

  return { data, loading, error, encrypt }
}
