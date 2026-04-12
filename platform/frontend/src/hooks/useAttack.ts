import { useState } from 'react'
import { api } from '../api/client'

export function useAttack() {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const runShors = async (keySize = 2048) => {
    setLoading(true)
    setError(null)
    try {
      const res = await api.post('/attack/shors', { key_size_bits: keySize })
      setData(res.data)
    } catch {
      setError("Shor's simulation failed.")
    } finally {
      setLoading(false)
    }
  }

  const runGrovers = async (algorithm = 'AES-128') => {
    setLoading(true)
    setError(null)
    try {
      const res = await api.post('/attack/grovers', { algorithm })
      setData(res.data)
    } catch {
      setError("Grover's simulation failed.")
    } finally {
      setLoading(false)
    }
  }

  const runLattice = async (dimension = 768) => {
    setLoading(true)
    setError(null)
    try {
      const res = await api.post('/attack/lattice', { dimension })
      setData(res.data)
    } catch {
      setError('Lattice simulation failed.')
    } finally {
      setLoading(false)
    }
  }

  const runHarvestRisk = async (yearsToProtect = 15, dataValue = 'high') => {
    setLoading(true)
    setError(null)
    try {
      const res = await api.post('/attack/harvest-risk', {
        years_to_protect: yearsToProtect,
        data_value: dataValue,
      })
      setData(res.data)
    } catch {
      setError('Harvest-risk simulation failed.')
    } finally {
      setLoading(false)
    }
  }

  return { data, loading, error, runShors, runGrovers, runLattice, runHarvestRisk }
}
