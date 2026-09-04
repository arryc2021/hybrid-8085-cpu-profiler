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

### Measured Metrics Summary

| Metric | Measured Value | Analysis |
| :--- | :--- | :--- |
| **Total $T$-States** | **15** | $7 + 7 + 1 = 15$ cycles (excluding `HLT` execution) |
| **Overall CPI** | **5.00** | Total Cycles / Total Executed Instructions |
| **RISC Latency Reduction** | **28.6%** | Execution cycle savings compared to legacy CISC arithmetic |
| **Instruction Mix** | **67% CISC / 33% RISC** | 2 Immediate Loads (CISC), 1 Arithmetic (RISC) |

Application Screenshots
System Interface & Live Execution Diagnostics
Below is the profiler running the generated test sequence, highlighting the side-by-side execution trace, register states, flag indicators, and performance graphs:

<img width="1357" height="825" alt="1" src="https://github.com/user-attachments/assets/b34b30a6-1964-4562-a1e5-bc6a02368683" />
<img width="1352" height="831" alt="2" src="https://github.com/user-attachments/assets/28605c3d-8e59-4827-b6b7-8d448c950a8f" />
Image 1: Initialized / Pre-Execution State (image_b9c364.png)What it shows: The profiler right after prompt generation, before machine code execution starts.Program Counter (PC): 0x0001 (Reset baseline)Registers & Flags: All set to 0x00 / 0 because no opcodes have been fetched.Calculations:$\text{Executed Instructions} = 0$$\text{Total T-States} = 0$$\text{CPI (Cycles Per Instruction)} = \frac{0 \text{ cycles}}{0 \text{ instructions}} = \mathbf{0.00}$$\text{Latency Reduction} = \mathbf{0.0\%}$Brief Explanation: The charts display "No Data" because the pipeline telemetry engine requires active instruction fetches to calculate instruction mix and cycle burden.Image 2: Post-Execution Telemetry (1.jpeg / 2.jpg)What it shows: The system state after executing the 3-instruction sequence plus system halt:Code snippetMVI A, 0F    ; CISC Load (7 T-States)
MVI C, 05    ; CISC Load (7 T-States)
R_SUB A, C   ; RISC Subtract (1 T-State)
HLT          ; System Halt (5 T-States)
1. Register & Flag CalculationsArithmetic: Register $A = 0x0F - 0x05 = \mathbf{0x0A}$Parity Flag ($P$): $0x0A = 0000\,1010_2$ (contains two 1s $\rightarrow$ Even parity, so $P = 1$).Zero ($Z$), Sign ($S$), Carry ($CY$): Result is positive, non-zero, with no borrow $\rightarrow$ $Z=0$, $S=0$, $CY=0$.2. Execution Analytics & Metric CalculationsTotal T-States (Operational Cost):$$\text{Total Cycles} = T_{\text{MVI A}} + T_{\text{MVI C}} + T_{\text{R\_SUB}} = 7 + 7 + 1 = \mathbf{15 \text{ cycles}}$$Overall CPI:$$\text{CPI} = \frac{\text{Total Cycles}}{\text{Executed ALU Instructions}} = \frac{15}{3} = \mathbf{5.00}$$Instruction Mix Distribution (Pie Chart):$$\text{CISC \%} = \left( \frac{2 \text{ CISC instructions}}{3 \text{ Total instructions}} \right) \times 100 = 66.67\% \approx \mathbf{67\%}$$$$\text{RISC \%} = \left( \frac{1 \text{ RISC instruction}}{3 \text{ Total instructions}} \right) \times 100 = 33.33\% \approx \mathbf{33\%}$$T-State Burden (Bar Chart):CISC Cost: $7 + 7 = \mathbf{14 \text{ T-States}}$RISC Cost: $1 = \mathbf{1 \text{ T-State}}$RISC Latency Reduction:Comparing total program execution ($15$ cycles) against an equivalent all-CISC pipeline using standard multi-cycle subtraction ($7 + 7 + 7 = 21$ cycles):$$\text{Latency Reduction} = \left( \frac{21 - 15}{21} \right) \times 100 = \mathbf{28.6\%}$$Brief ExplanationThe graphs clearly demonstrate the core advantage of hybrid microarchitecture design: while multi-cycle CISC instructions (MVI) are necessary for multi-byte data setup, offloading the arithmetic operation to a single-cycle RISC micro-op (R_SUB) reduces arithmetic cycle consumption by 75% (1 cycle vs. 4 cycles) and cuts overall pipeline execution latency by 28.6%.



## Installation & Setup

### Prerequisites

1. **Python 3.8+**
2. **Ollama**: Download and install from [ollama.com](https://ollama.com).

### 1. Clone the Repository

```bash
git clone [https://github.com/arryc2021/hybrid-8085-cpu-profiler.git](https://github.com/arryc2021/hybrid-8085-cpu-profiler.git)
cd hybrid-8085-cpu-profiler
2. Install Python Dependencies
<img width="912" height="168" alt="image" src="https://github.com/user-attachments/assets/8fe1ded0-15fe-4258-a6c8-b457d0320186" />

3. Pull the Local SLM Model
Ensure Ollama is running in the background, then pull the model:
<img width="897" height="157" alt="image" src="https://github.com/user-attachments/assets/3b27a641-b963-41cb-be1a-8083ad32e7ae" />
4. Launch the profiler
<img width="963" height="182" alt="image" src="https://github.com/user-attachments/assets/41f81679-5a9b-496f-8934-ffb3725422b4" />








