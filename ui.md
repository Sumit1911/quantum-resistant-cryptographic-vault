# UI Specification — CryptoArena Platform
## Section-wise Feature Reference (Updated: April 12, 2026)

---

## 1. Product UX Structure

The active UI experience is the **platform frontend**:

- Stack: React + TypeScript + Vite
- Root: `platform/frontend/src/`
- Layout model: single top navigation, panel-based pages, responsive grid

Primary routes:
- `/` -> Dashboard
- `/arena` -> Algorithm Arena
- `/attack` -> Attack Lab
- `/vault` -> Vault Lens

---

## 2. Design System Features

File: `platform/frontend/src/index.css`

Implemented UI/UX features:
- CSS token system (`--bg`, `--panel`, `--accent`, `--danger`, etc.)
- Two-font hierarchy:
  - `Space Grotesk` for product readability
  - `IBM Plex Mono` for technical/crypto labels
- Atmospheric background layers (radial gradients + floating blur orbs)
- Semantic card tones:
  - neutral
  - good (positive signal)
  - warn (risk/exposure signal)
- Mobile-responsive behavior:
  - flexible controls
  - wrapping navigation
  - stacked race bars on smaller screens

---

## 3. Global Navigation & Shell

File: `platform/frontend/src/App.tsx`

Features:
- Sticky top navigation with active route highlighting
- Section labels:
  - Overview
  - Arena
  - Attack Lab
  - Vault Lens
- Branded header:
  - product title + research-context kicker
- Background visual layer separated from content layer for depth

---

## 4. Dashboard Section (`/`)

File: `platform/frontend/src/pages/Dashboard.tsx`

Feature blocks:
1. Hero narrative block
- Explains platform value for research and report usage
- CTA buttons for each lab

2. Key capability cards
- Research dimensions
- Quantum readiness range
- Telemetry richness

3. Guided workflow panel
- Recommends how to use Arena + Attack + Vault together for academic evidence

---

## 5. Algorithm Arena Section (`/arena`)

File: `platform/frontend/src/pages/Arena.tsx`

### Controls
- Classical algorithm selector
- PQC algorithm selector
- Operation selector (`keygen`, `encrypt`, `sign`, `verify`)
- Iterations input
- File-size input (MB)

### Visual outputs
1. Top metrics
- Winner
- Speedup factor
- Energy reduction
- Latency gap / P95 gap

2. Comparative bars
- Classical vs PQC average latency race bar

3. Risk/performance cards
- Quantum risk per branch
- Memory indicators
- Throughput ratio

4. Chart
- Iteration-wise latency evolution line chart

5. Research notes panel
- Backend-generated interpretation lines for report narrative

### Loading UX
- Animated `CryptoLoader` shown while benchmark is running

---

## 6. Attack Lab Section (`/attack`)

File: `platform/frontend/src/pages/AttackLab.tsx`

### Simulation modes (tabbed)
1. **Shor**
- Input: RSA key size
- Outputs: break ratio, complexity curves, verdict

2. **Grover**
- Input: target (`AES-128`, `AES-192`, `AES-256`, `SHA-256`)
- Outputs: effective bit reduction, recommendation, security bars

3. **Lattice SVP**
- Input: lattice dimension
- Outputs: security level, BKZ block size, hardness curves

4. **HNDL (Harvest-Now Decrypt-Later)**
- Inputs: years to protect, data value tier
- Outputs: risk today, risk horizon, compromise year estimate, recommendation
- Visualization: dedicated risk timeline chart

### Shared attack visuals
- Verdict/risk metric cards
- Mode-aware chart rendering
- Mode-specific section blocks (bars or timeline)

### Loading UX
- `CryptoLoader` during attack simulation execution

---

## 7. Vault Lens Section (`/vault`)

File: `platform/frontend/src/pages/Vault.tsx`

### Controls
- KEM selection (`Kyber-512`, `Kyber-768`)
- Signature scheme selection (`Dilithium2`, `Dilithium3`, `ML-DSA-65`)
- Plaintext payload textarea

### Instrumentation outputs
1. Pipeline summary cards
- Total time
- Quantum readiness score
- Throughput

2. Overhead cards
- Ciphertext size
- Signature and capsule overhead
- Total overhead percent

3. Flow visualizer
- Stage-by-stage cards with timing and output size

4. Execution log
- Ordered textual events from cryptographic pipeline

5. Research notes
- Interpretation lines for overhead and security behavior

### Loading UX
- `CryptoLoader` while instrumentation request is running

---

## 8. Shared UI Components

Location: `platform/frontend/src/components/`

- `MetricCard.tsx` -> reusable metric tile with tone support
- `LiveChart.tsx` -> Arena latency chart
- `AttackCurve.tsx` -> Shor/Lattice trend chart
- `RiskTimeline.tsx` -> HNDL risk growth chart
- `AlgoRaceBar.tsx` -> dual normalized race bars
- `FlowVisualizer.tsx` -> animated cryptographic stage map
- `TerminalLog.tsx` -> numbered event stream
- `CryptoLoader.tsx` -> animated cryptographic loading indicator

---

## 9. Frontend Data Layer

API client:
- `platform/frontend/src/api/client.ts`
- Base URL: `http://127.0.0.1:8000/api`

Hooks:
- `useBenchmark.ts` -> benchmark requests + loading/error state
- `useAttack.ts` -> shor/grover/lattice/hndl requests + loading/error state
- `useVault.ts` -> vault instrumentation request + loading/error state

---

## 10. UX Intent (Current)

The current UI is intentionally tuned for:
- report-ready comparison storytelling
- explicit risk communication (not just raw timing)
- easy parameterized experiments
- clean transitions between benchmarking, threat simulation, and vault internals

---

## 11. Legacy UI Note

The Streamlit UI (`app/`) still exists and remains functional for the original vault flow.
This document describes the **platform UI** in `platform/frontend`, which is the current primary UX for research demos.
