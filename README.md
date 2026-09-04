![CI/CD Pipeline](https://github.com/arryc2021/hybrid-8085-cpu-profiler/actions/workflows/ci.yml/badge.svg)

# Industrial Hybrid 8085 Microarchitecture Profiler & AI Compiler

An industrial-grade 8085 CPU simulator, performance profiler, and AI co-pilot engineered to demonstrate low-latency hardware design, custom Instruction Set Architecture (ISA) extensions, and hardware-software co-design.

The system simulates standard 8085 CISC operations alongside custom 1-cycle RISC extensions (`R_ADD`, `R_SUB`, `R_AND`, `R_XOR`). It features a real-time cycle-accurate telemetry engine and an integrated local Small Language Model (Gemma 3 via Ollama) for natural-language assembly compilation.

---

## Key Features

* **Hybrid CISC/RISC Engine**: Micro-architectural support for classic 8085 CISC instructions (7–13 $T$-states) and optimized 1-cycle RISC extensions.
* **On-Device AI Assembly Compiler**: Integrates **Gemma 3** (via Ollama) to convert plain English intent into executable, placeholder-free assembly.
* **Cycle-Accurate Performance Analytics**: Live tracking of total $T$-states, overall CPI (Cycles Per Instruction), instruction mix ratios, and RISC latency reduction percentage.
* **Industrial Diagnostics GUI**: Full register/flag inspection, step-by-step execution profiling, trace logging, and interactive Matplotlib charts.

---

## Architectural Benchmarks

Below is a latency and performance comparison between standard CISC instructions and custom RISC micro-operations supported by the engine:

### Instruction Latency Breakdown

| Instruction | Type | Opcode | Operations | Clock Cycles ($T$-States) |
| :--- | :--- | :--- | :--- | :---: |
| `MVI A, d8` | CISC | `0x3E` | Immediate Load to Register A | **7** |
| `MVI B, d8` | CISC | `0x06` | Immediate Load to Register B | **7** |
| `MVI C, d8` | CISC | `0x0E` | Immediate Load to Register C | **7** |
| `LDA addr` | CISC | `0x3A` | Memory Read to Register A | **13** |
| `HLT` | CISC | `0x76` | System Halt | **5** |
| `R_ADD A, B` | **RISC** | `0xE0` | Single-cycle Register Addition | **1** |
| `R_SUB A, C` | **RISC** | `0xE1` | Single-cycle Register Subtraction | **1** |
| `R_AND A, B` | **RISC** | `0xE3` | Single-cycle Bitwise AND | **1** |
| `R_XOR A, B` | **RISC** | `0xE5` | Single-cycle Bitwise XOR | **1** |

---

### Execution Profile Case Study

**Program Task**: Load `0x0F` into Register A, load `0x05` into Register C, and perform subtraction.

```assembly
MVI A, 0F      ; Load A (7 T-states)
MVI C, 05      ; Load C (7 T-states)
R_SUB A, C     ; Custom RISC Subtract (1 T-state)
HLT            ; Halt Execution (5 T-states)
```

### Measured Metrics Summary

| Metric | Measured Value | Analysis |
| :--- | :--- | :--- |
| **Total $T$-States** | **15** | $7 + 7 + 1 = 15$ cycles (excluding `HLT` execution) |
| **Overall CPI** | **5.00** | Total Cycles / Total Executed Instructions |
| **RISC Latency Reduction** | **28.6%** | Execution cycle savings compared to legacy CISC arithmetic |
| **Instruction Mix** | **67% CISC / 33% RISC** | 2 Immediate Loads (CISC), 1 Arithmetic (RISC) |

---

## Application Screenshots

### System Interface & Live Execution Diagnostics

Below is the profiler running the generated test sequence, highlighting the side-by-side execution trace, register states, flag indicators, and performance graphs:

<img width="1357" alt="Pre-Execution Initial State" src="https://github.com/user-attachments/assets/b34b30a6-1964-4562-a1e5-bc6a02368683" />

<img width="1352" alt="Post-Execution Telemetry Diagnostics" src="https://github.com/user-attachments/assets/28605c3d-8e59-4827-b6b7-8d448c950a8f" />

---

## Execution Analysis & Telemetry Breakdown

### Image 1: Initialized / Pre-Execution State
* **What it shows:** Profiler right after prompt generation, before machine code execution starts.
* **Program Counter (PC):** `0x0001` (Reset baseline)
* **Registers & Flags:** All set to `0x00` / `0` because no opcodes have been fetched.
* **Calculations:**
  * $	ext{Executed Instructions} = 0$
  * $	ext{Total T-States} = 0$
  * $	ext{CPI (Cycles Per Instruction)} = rac{0}{0} = \mathbf{0.00}$
  * $	ext{Latency Reduction} = \mathbf{0.0\%}$
* **Brief Explanation:** The charts display "No Data" because the pipeline telemetry engine requires active instruction fetches to calculate instruction mix and cycle burden.

### Image 2: Post-Execution Telemetry
* **What it shows:** System state after executing the 3-instruction sequence plus system halt.
* **Calculations:**
  * **Arithmetic Result:** Register $A = 0x0F - 0x05 = \mathbf{0x0A}$
  * **Parity Flag ($P$):** $0x0A = 0000\,1010_2$ (contains two 1s $
ightarrow$ Even parity, so $P = 1$).
  * **Zero ($Z$), Sign ($S$), Carry ($CY$):** Result is positive, non-zero, with no borrow ($Z=0, S=0, CY=0$).
  * **Total T-States:** $7 + 7 + 1 = \mathbf{15 	ext{ cycles}}$
  * **Overall CPI:** $rac{15}{3} = \mathbf{5.00}$
  * **Instruction Mix Distribution:** CISC = $\mathbf{67\%}$, RISC = $\mathbf{33\%}$
  * **T-State Burden:** CISC Cost = $\mathbf{14 	ext{ T-States}}$, RISC Cost = $\mathbf{1 	ext{ T-State}}$
  * **RISC Latency Reduction:** $rac{21 - 15}{21} 	imes 100 = \mathbf{28.6\%}$

---

## Installation & Setup

### Prerequisites

1. **Python 3.8+**
2. **Ollama**: Download and install from [ollama.com](https://ollama.com).

### 1. Clone the Repository

```bash
git clone https://github.com/arryc2021/hybrid-8085-cpu-profiler.git
cd hybrid-8085-cpu-profiler
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Pull the Local SLM Model

Ensure Ollama is running in the background, then pull the model:

```bash
ollama pull gemma3:1b
```

### 4. Launch the Profiler

```bash
python main.py
```
### 5. Running through Docker
Install Docker Desktop
Open PowerShell in your project folder and build the image:
<img width="861" height="152" alt="image" src="https://github.com/user-attachments/assets/eaf78ac9-36e3-4aed-8015-4ffc30f54800" />
### 6. Run the container passing the DISPLAY environment variable:
<img width="875" height="215" alt="image" src="https://github.com/user-attachments/assets/4d5f267c-a02a-4a61-9a8e-01f2c65de1cd" />
### 7. Option B: Running from WSL2 Terminal (Recommended for Windows)
If you are running Docker commands directly inside a WSL2 Ubuntu terminal:

<img width="978" height="366" alt="image" src="https://github.com/user-attachments/assets/b28aa3d4-f60a-44a4-810a-8a102d5300cc" />

### 8. How my ci/cd works?
Refer to ci.yml 
Trigger: Fires automatically every time you git push code or open a Pull Request to your main branch.

Environment Setup: Provisions an isolated Ubuntu virtual machine and sets up Python 3.10.

Dependency Check: Installs packages from your requirements.txt file and runs basic import tests.

Code Quality Linting: Scans Python files for syntax errors and unused imports using flake8.

Container Build Verification: Compiles your Windows/Linux Dockerfile to guarantee that new commits won't break the container build




