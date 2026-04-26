import { useState } from 'react'
import { api } from '../api/client'
import { waitRandomSimulationDelay } from '../utils/simulationDelay'

export type VaultEncryptRequest = {
  input_kind: 'text' | 'file'
  plaintext?: string
  content_base64?: string
  item_name?: string
  mime_type?: string
  algorithm: string
  signing: string
}

export function useVault() {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const encrypt = async (payload: VaultEncryptRequest) => {
    setLoading(true)
    setError(null)
    try {
      await waitRandomSimulationDelay()
      const res = await api.post('/vault/encrypt', payload)
      setData(res.data)
    } catch (err: any) {
      const detail = err?.response?.data?.detail
      setError(detail || 'Vault instrumentation request failed.')
    } finally {
      setLoading(false)
    }
  }

  return { data, loading, error, encrypt }
}
