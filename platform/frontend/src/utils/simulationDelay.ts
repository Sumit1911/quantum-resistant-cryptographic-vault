const MIN_SIM_DELAY_MS = 2000
const MAX_SIM_DELAY_MS = 5000

function randomDelayMs(minMs: number, maxMs: number): number {
  return Math.floor(Math.random() * (maxMs - minMs + 1)) + minMs
}

export async function waitRandomSimulationDelay(): Promise<number> {
  const delay = randomDelayMs(MIN_SIM_DELAY_MS, MAX_SIM_DELAY_MS)
  await new Promise((resolve) => setTimeout(resolve, delay))
  return delay
}
