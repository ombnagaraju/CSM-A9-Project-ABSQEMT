# Adaptive Selection of Quantum Error Mitigation Techniques for Noisy Quantum Circuits on IBM Quantum Hardware

## Project Overview

Quantum computers based on superconducting and other noisy intermediate-scale quantum (NISQ) technologies are affected by gate errors, measurement errors, decoherence, limited connectivity, and time-varying hardware calibration. These noise sources can significantly degrade the reliability of quantum algorithms executed on real quantum processors.

Quantum Error Mitigation (QEM) provides a practical approach for reducing the effect of noise without requiring the full overhead of fault-tolerant Quantum Error Correction (QEC). However, different mitigation techniques are effective under different noise conditions. Readout error mitigation is primarily useful when measurement errors dominate, whereas Zero-Noise Extrapolation (ZNE) can be more relevant for circuits with substantial gate-level noise, depth, and two-qubit operations.

This project investigates an **adaptive, circuit- and hardware-aware approach for selecting QEM techniques** according to the characteristics of the quantum circuit and the current calibration state of the IBM Quantum processor.

The central research question is:

> **Can quantum-circuit characteristics and IBM Quantum hardware calibration data be used to adaptively select an appropriate error-mitigation strategy while improving computational reliability with reasonable experimental overhead?**

The proposed framework evaluates raw execution, fixed mitigation strategies, and adaptive QEM using real IBM Quantum hardware.

---

## Research Objective

The primary objective is to develop and experimentally evaluate a transparent adaptive framework that selects among different QEM strategies based on:

- Circuit depth
- Number of qubits
- One-qubit gate count
- Two-qubit gate count
- CX/CZ count
- SWAP count
- Readout assignment error
- One-qubit gate error
- Two-qubit gate error
- T1 and T2 coherence characteristics
- Hardware connectivity and transpiled circuit structure

The framework is designed to determine whether **circuit-aware and hardware-aware mitigation selection** can provide a better reliability-versus-overhead trade-off than applying a single mitigation method to all circuits.

---

## Proposed Framework

```text
                 Quantum Benchmark Circuit
                           |
                           v
                  Circuit Characterization
                           |
              +------------+------------+
              |                         |
              v                         v
       Circuit Features          IBM Hardware
       - Qubit count             Calibration
       - Depth                   - Readout error
       - 1Q gates                - 1Q gate error
       - 2Q gates                - 2Q gate error
       - CX/CZ                   - T1 / T2
       - SWAP                    - Connectivity
              |                         |
              +------------+------------+
                           |
                           v
                  Adaptive QEM Selector
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
        RAW             READOUT            ZNE
                       MITIGATION
          |                |                |
          +----------------+----------------+
                           |
                           v
                  Optional Combined QEM
                           |
                           v
                  IBM Quantum Hardware
                           |
                           v
                 Measurement Distribution
                           |
                           v
              Statistical / Fidelity Analysis
                           |
                           v
             Reliability vs. Execution Overhead
```

---

## Adaptive Strategy Selection

The current implementation uses a transparent rule-based selection mechanism.

Available strategies:

```text
RAW
READOUT MITIGATION
ZERO-NOISE EXTRAPOLATION (ZNE)
COMBINED READOUT + ZNE
```

The initial decision logic is based on circuit and hardware characteristics.

### Readout-dominated conditions

When measurement assignment error is relatively high, the framework increases the priority of readout error mitigation.

### Gate-noise-dominated conditions

When circuit depth, two-qubit gate count, or two-qubit gate error is high, ZNE receives a higher priority.

### Combined conditions

When both readout and execution-related noise indicators are significant, the framework can select a combined readout-mitigation + ZNE workflow.

### Low-noise conditions

When the estimated noise contribution and circuit complexity are sufficiently low, raw execution may be retained to avoid unnecessary mitigation overhead.

The thresholds are configurable experimental parameters. They are **not treated as universal hardware-independent constants** and will be evaluated against the experimental dataset.

---

## Quantum Error Mitigation Techniques

### 1. Raw Hardware Execution

The original transpiled circuit is executed directly on IBM Quantum hardware.

This provides the baseline against which all mitigation strategies are evaluated.

### 2. Readout Error Mitigation

Readout mitigation models measurement errors using an assignment matrix.

For a single qubit:

```text
        Measured
          0     1
True 0   p00   p01
True 1   p10   p11
```

For multiple qubits, the corresponding measurement model is constructed from individual assignment matrices.

The measured probability vector is corrected using a pseudoinverse-based procedure followed by probability clipping and normalization.

### 3. Zero-Noise Extrapolation

Zero-Noise Extrapolation is used to estimate the circuit result at an effective noise level approaching zero.

Digital gate folding is used to increase the effective circuit noise:

```text
U  →  U U† U
```

The current experimental design uses scale factors:

```text
{1, 3, 5}
```

A linear extrapolation model is used:

\[
M(\lambda)=a+b\lambda
\]

with zero-noise estimate:

\[
M_{\mathrm{ZNE}}=a.
\]

---

## Benchmark Suite

| Benchmark | Purpose |
|---|---|
| Bell State | Basic entanglement |
| GHZ-3 | Multi-qubit entanglement |
| GHZ-4 | Entanglement scaling |
| GHZ-5 | Increased entanglement depth |
| Quantum Teleportation | Quantum communication |
| Superdense Coding | Quantum communication |
| QFT-3 | Quantum Fourier Transform |
| QFT-4 | Increased QFT complexity |
| Grover-2Q | Quantum search |
| QAOA-2Q | Variational optimization |
| QPE | Phase estimation |
| QRNG-4 | Randomness generation |

Superdense coding is evaluated for multiple input messages:

```text
00
01
10
11
```

---

## Experimental Conditions

The experimental campaign evaluates four principal conditions:

```text
1. RAW
2. FIXED-READOUT
3. FIXED-ZNE
4. ADAPTIVE
```

The central comparison is:

\[
\boxed{
\mathrm{RAW}
\quad vs \quad
\mathrm{FIXED\!-\!READOUT}
\quad vs \quad
\mathrm{FIXED\!-\!ZNE}
\quad vs \quad
\mathrm{ADAPTIVE}
}
\]

The objective is not merely to show that mitigation can improve a circuit, but to investigate whether **adaptive selection itself provides useful experimental value compared with applying a fixed mitigation strategy to every circuit**.

---

## IBM Quantum Hardware

The experimental framework is designed for IBM Quantum superconducting quantum processors.

The current experimental campaign targets:

```text
Backend: ibm_kingston
Architecture: IBM Heron r2
Qubit count: 156
```

The exact calibration state is recorded for every experimental campaign because IBM Quantum hardware characteristics change over time.

Recorded hardware parameters include:

- Qubit T1
- Qubit T2
- Readout assignment error
- One-qubit gate error
- Two-qubit gate error
- Coupling/connectivity information
- Calibration timestamp

---

## Circuit Characterization

After transpilation, each circuit is characterized using:

\[
\mathbf{C}
=
[
N_q,
D,
N_{1Q},
N_{2Q},
N_{CX},
N_{CZ},
N_{SWAP}
]
\]

where:

- \(N_q\) = number of physical qubits
- \(D\) = circuit depth
- \(N_{1Q}\) = one-qubit gate count
- \(N_{2Q}\) = two-qubit gate count
- \(N_{CX}\) = CX gate count
- \(N_{CZ}\) = CZ gate count
- \(N_{SWAP}\) = SWAP gate count

Hardware characteristics are represented by:

\[
\mathbf{H}
=
[
\epsilon_{RO},
\epsilon_{1Q},
\epsilon_{2Q},
T_1,
T_2
]
\]

The adaptive decision can therefore be expressed as:

\[
m^*=f(\mathbf{C},\mathbf{H})
\]

---

## Evaluation Metrics

### Success Probability

\[
P_{\mathrm{success}}
=
\frac{N_{\mathrm{correct}}}{N_{\mathrm{shots}}}
\]

### Error Probability

\[
P_{\mathrm{error}}
=
1-P_{\mathrm{success}}
\]

### Total Variation Distance

\[
D_{\mathrm{TV}}
=
\frac{1}{2}
\sum_x
|P(x)-P_{\mathrm{ideal}}(x)|
\]

### Distribution Fidelity

\[
F_{\mathrm{dist}}
=
\left(
\sum_x
\sqrt{P(x)P_{\mathrm{ideal}}(x)}
\right)^2
\]

### Statistical Uncertainty

The framework calculates:

- Standard error
- Wilson confidence intervals
- Benchmark-level paired differences
- Bootstrap confidence intervals

### Execution Overhead

\[
O_s
=
\frac{N_{\mathrm{exec},s}}
{N_{\mathrm{exec,raw}}}
\]

---

## Reliability--Overhead Trade-off

Improving reliability alone is not sufficient to establish practical usefulness.

The project therefore evaluates:

```text
Reliability improvement
          vs.
Experimental execution overhead
```

This is particularly important for ZNE because multiple noise-scaled executions are required.

---

## Experimental Data Organization

```text
data/
├── ideal/
├── noisy/
├── hardware/
├── calibration/
└── mitigated/

results/
├── tables/
├── figures/
└── reports/
```

- **ideal/** — noiseless reference distributions
- **noisy/** — controlled-noise simulation results
- **hardware/** — raw IBM Quantum execution results and job metadata
- **calibration/** — calibration snapshots
- **mitigated/** — readout-mitigated, ZNE, combined, and adaptive results
- **results/tables/** — publication tables
- **results/figures/** — publication figures
- **results/reports/** — experimental reports

---

## Project Structure

```text
Adaptive_QEM_IBM/
│
├── circuits/
│   ├── bell.py
│   ├── ghz.py
│   ├── teleportation.py
│   ├── superdense.py
│   ├── qft.py
│   ├── grover.py
│   ├── qaoa.py
│   ├── qpe.py
│   └── qrng.py
│
├── simulation/
│   ├── ideal_simulation.py
│   └── noisy_simulation.py
│
├── hardware/
│   ├── backend_info.py
│   ├── transpile_circuits.py
│   └── execute_ibm.py
│
├── mitigation/
│   ├── readout_mitigation.py
│   ├── zne.py
│   └── adaptive_qem.py
│
├── analysis/
│   ├── metrics.py
│   ├── fidelity.py
│   ├── statistics.py
│   └── plots.py
│
├── data/
│   ├── ideal/
│   ├── noisy/
│   ├── hardware/
│   ├── calibration/
│   └── mitigated/
│
├── results/
│   ├── tables/
│   ├── figures/
│   └── reports/
│
├── notebooks/
│   ├── 01_environment_check.ipynb
│   ├── 02_ideal_benchmarks.ipynb
│   ├── 03_noise_benchmarks.ipynb
│   ├── 04_hardware_benchmarks.ipynb
│   ├── 05_qem_analysis.ipynb
│   ├── 06_final_results.ipynb
│   ├── 07_adaptive_qem_experiment.ipynb
│   ├── 08_ibm_hardware_runner.ipynb
│   ├── 09_ibm_environment_calibration.ipynb
│   ├── 10_adaptive_qem_hardware_campaign.ipynb
│   ├── 11_hardware_result_extraction_qem_evaluation.ipynb
│   ├── 12_adaptive_vs_fixed_qem_statistical_comparison.ipynb
│   ├── 13_publication_figures_tables_generator.ipynb
│   └── 14_complete_experimental_report_generator.ipynb
│
├── config/
│   └── experiment_config.json
│
├── requirements.txt
├── README.md
└── LICENSE
```

---

## Experimental Workflow

```text
Step 1
Environment and dependency verification
        ↓
Step 2
Generate benchmark circuits
        ↓
Step 3
Run ideal simulations
        ↓
Step 4
Run controlled-noise simulations
        ↓
Step 5
Connect to IBM Quantum
        ↓
Step 6
Capture backend calibration
        ↓
Step 7
Transpile benchmark circuits
        ↓
Step 8
Extract circuit-level features
        ↓
Step 9
Execute raw circuits
        ↓
Step 10
Apply readout mitigation
        ↓
Step 11
Execute ZNE circuits
        ↓
Step 12
Run adaptive QEM selection
        ↓
Step 13
Extract hardware results
        ↓
Step 14
Compare RAW / FIXED-READOUT / FIXED-ZNE / ADAPTIVE
        ↓
Step 15
Statistical analysis
        ↓
Step 16
Generate publication figures and tables
        ↓
Step 17
Generate experimental report
```

---

## Reproducibility

Each hardware experiment records:

- Benchmark identifier
- Original circuit
- Transpiled circuit characteristics
- Backend name
- Backend architecture
- Calibration timestamp
- Calibration parameters
- Transpiler optimization level
- Physical qubit mapping
- Mitigation strategy
- ZNE scale factors
- Number of shots
- IBM Quantum job ID
- Raw counts
- Mitigated counts
- Derived metrics
- Software environment

Hardware results are therefore linked to their corresponding execution metadata.

---

## Current Research Status

The following components are implemented or organized:

- Benchmark circuit generation
- Ideal simulation workflow
- Controlled-noise simulation workflow
- IBM Quantum backend characterization
- Circuit transpilation pipeline
- Readout mitigation implementation
- ZNE implementation
- Adaptive QEM selection logic
- Hardware campaign controller
- Hardware result extraction
- Statistical comparison framework
- Publication figure generation
- Experimental report generation

The final numerical results will be populated after completion and extraction of the IBM Quantum hardware execution campaign.

**No hardware performance values are hard-coded or synthetically generated.**

---

## Expected Research Contributions

The project investigates:

1. A transparent circuit- and hardware-aware QEM selection framework.
2. Experimental comparison of raw execution, fixed mitigation, and adaptive mitigation.
3. Integration of circuit complexity with IBM Quantum calibration information.
4. Evaluation across heterogeneous quantum benchmark families.
5. Joint analysis of reliability improvement and execution overhead.
6. Statistical evaluation of adaptive versus fixed mitigation strategies.
7. A reproducible experimental workflow for QEM studies on IBM Quantum hardware.

The work does not assume that one mitigation technique is universally optimal. Instead, it investigates whether the appropriate mitigation strategy depends on the interaction between **circuit characteristics and hardware noise conditions**.

---

## Research Scope and Limitations

The current framework uses a transparent rule-based selector. Decision thresholds are configurable and require experimental validation.

The study is also constrained by:

- Time-varying IBM Quantum calibration
- Finite hardware shot budgets
- Backend queue and execution availability
- Limited benchmark sizes
- Statistical uncertainty
- Dependence on the selected IBM processor
- Potential instability of extrapolation-based mitigation
- Additional execution overhead introduced by QEM

The experimental conclusions will therefore be interpreted within the hardware and software conditions under which the experiments are performed.

---

## Future Extensions

Potential extensions include:

- Machine-learning-based mitigation selection
- Automatic threshold optimization
- Reinforcement-learning-based QEM selection
- Dynamic calibration-aware strategy updates
- Additional QEM methods such as probabilistic error cancellation
- Layer-wise noise characterization
- Larger quantum algorithms
- Cross-backend evaluation
- Cross-day calibration stability analysis
- Automated QEM cost-performance optimization
- Integration with IBM Quantum Runtime resilience workflows

---

## Software Stack

- Python
- Qiskit
- Qiskit Aer
- Qiskit Runtime
- NumPy
- SciPy
- Matplotlib
- Pandas
- Jupyter Notebook
- IBM Quantum hardware

---

## Reproducibility and Security

Users should provide their own IBM Quantum credentials through the supported IBM Quantum authentication mechanism.

**Never commit IBM Quantum API tokens, credentials, or other secrets to GitHub.**

Recommended workflow:

```text
Credentials
    ↓
Secure credential storage / environment
    ↓
Experiment configuration
    ↓
IBM Quantum backend
```

---

## Citation

If this repository is used in academic work, please cite the associated research paper:

```bibtex
@article{adaptiveQEMIBM,
  title   = {Adaptive Selection of Quantum Error Mitigation Techniques
             for Noisy Quantum Circuits on IBM Quantum Hardware},
  author  = {Bathula, Naga Raju},
  journal = {To be submitted},
  year    = {2026}
}
```

The citation information will be updated after publication.

---

## Disclaimer

This repository is an experimental research project.

Hardware results depend on the IBM Quantum processor, calibration state, circuit mapping, transpilation configuration, shot count, queue conditions, and execution time. Results obtained from one hardware campaign should not automatically be interpreted as universal characteristics of IBM Quantum processors.

---

## Acknowledgment

This work uses IBM Quantum services and software for experimental evaluation of quantum circuits on real quantum hardware.

The project is intended to contribute to research on practical quantum computing, quantum error mitigation, hardware-aware quantum compilation, and reliable execution of quantum algorithms on NISQ-era quantum processors.
