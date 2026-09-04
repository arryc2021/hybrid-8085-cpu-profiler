import tkinter as tk
from tkinter import ttk, messagebox
import threading
import ollama

# Matplotlib integration for industrial UI dashboard
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


class HybridCPU8085:
    """Core CPU supporting standard 8085 CISC and custom 1-cycle RISC extensions."""
    def __init__(self):
        self.registers = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0, 'H': 0, 'L': 0}
        self.PC = 0x0000
        self.SP = 0xFFFF
        self.flags = {'Z': 0, 'S': 0, 'P': 0, 'CY': 0}
        self.memory = bytearray(65536)
        self.cycles = 0
        self.cisc_count = 0
        self.risc_count = 0
        self.is_halted = False
        self.execution_log = []

    def reset(self):
        for reg in self.registers:
            self.registers[reg] = 0
        self.PC = 0x0000
        self.SP = 0xFFFF
        for flag in self.flags:
            self.flags[flag] = 0
        self.cycles = 0
        self.cisc_count = 0
        self.risc_count = 0
        self.is_halted = False
        self.execution_log.clear()

    def update_flags(self, result, carry=None):
        res_8bit = result & 0xFF
        self.flags['Z'] = 1 if res_8bit == 0 else 0
        self.flags['S'] = 1 if (res_8bit & 0x80) != 0 else 0
        self.flags['P'] = 1 if bin(res_8bit).count('1') % 2 == 0 else 0
        if carry is not None:
            self.flags['CY'] = carry

    def step(self):
        if self.is_halted or self.PC >= 65536:
            return False

        current_pc = self.PC
        opcode = self.memory[self.PC]
        self.PC += 1

        # CISC Instructions
        if opcode == 0x3E:   # MVI A, d8
            val = self.memory[self.PC]
            self.registers['A'] = val
            self.PC += 1
            self.cycles += 7
            self.cisc_count += 1
            self.execution_log.append({
                "pc": f"0x{current_pc:04X}",
                "cisc": f"MVI A, {val:02X}",
                "cisc_cycles": 7,
                "risc": "-",
                "risc_cycles": "-",
                "desc": f"Loaded 0x{val:02X} into A"
            })
        elif opcode == 0x06: # MVI B, d8
            val = self.memory[self.PC]
            self.registers['B'] = val
            self.PC += 1
            self.cycles += 7
            self.cisc_count += 1
            self.execution_log.append({
                "pc": f"0x{current_pc:04X}",
                "cisc": f"MVI B, {val:02X}",
                "cisc_cycles": 7,
                "risc": "-",
                "risc_cycles": "-",
                "desc": f"Loaded 0x{val:02X} into B"
            })
        elif opcode == 0x0E: # MVI C, d8
            val = self.memory[self.PC]
            self.registers['C'] = val
            self.PC += 1
            self.cycles += 7
            self.cisc_count += 1
            self.execution_log.append({
                "pc": f"0x{current_pc:04X}",
                "cisc": f"MVI C, {val:02X}",
                "cisc_cycles": 7,
                "risc": "-",
                "risc_cycles": "-",
                "desc": f"Loaded 0x{val:02X} into C"
            })
        elif opcode == 0x3A: # LDA addr
            low = self.memory[self.PC]
            high = self.memory[self.PC + 1]
            self.PC += 2
            addr = (high << 8) | low
            self.registers['A'] = self.memory[addr]
            self.cycles += 13
            self.cisc_count += 1
            self.execution_log.append({
                "pc": f"0x{current_pc:04X}",
                "cisc": f"LDA {addr:04X}",
                "cisc_cycles": 13,
                "risc": "-",
                "risc_cycles": "-",
                "desc": f"Read RAM[0x{addr:04X}] -> A"
            })

        # RISC Extensions
        elif opcode == 0xE0: # R_ADD A, B
            res = self.registers['A'] + self.registers['B']
            self.registers['A'] = res & 0xFF
            self.update_flags(self.registers['A'], carry=1 if res > 255 else 0)
            self.cycles += 1
            self.risc_count += 1
            self.execution_log.append({
                "pc": f"0x{current_pc:04X}",
                "cisc": "-",
                "cisc_cycles": "-",
                "risc": "R_ADD A, B",
                "risc_cycles": 1,
                "desc": f"Fast Add: A = 0x{self.registers['A']:02X}"
            })
        elif opcode == 0xE1: # R_SUB A, C
            res = self.registers['A'] - self.registers['C']
            self.registers['A'] = res & 0xFF
            self.update_flags(self.registers['A'], carry=1 if res < 0 else 0)
            self.cycles += 1
            self.risc_count += 1
            self.execution_log.append({
                "pc": f"0x{current_pc:04X}",
                "cisc": "-",
                "cisc_cycles": "-",
                "risc": "R_SUB A, C",
                "risc_cycles": 1,
                "desc": f"Fast Sub: A = 0x{self.registers['A']:02X}"
            })
        elif opcode == 0xE3: # R_AND A, B
            self.registers['A'] &= self.registers['B']
            self.update_flags(self.registers['A'], carry=0)
            self.cycles += 1
            self.risc_count += 1
            self.execution_log.append({
                "pc": f"0x{current_pc:04X}",
                "cisc": "-",
                "cisc_cycles": "-",
                "risc": "R_AND A, B",
                "risc_cycles": 1,
                "desc": f"Fast AND: A = 0x{self.registers['A']:02X}"
            })
        elif opcode == 0xE5: # R_XOR A, B
            self.registers['A'] ^= self.registers['B']
            self.update_flags(self.registers['A'], carry=0)
            self.cycles += 1
            self.risc_count += 1
            self.execution_log.append({
                "pc": f"0x{current_pc:04X}",
                "cisc": "-",
                "cisc_cycles": "-",
                "risc": "R_XOR A, B",
                "risc_cycles": 1,
                "desc": f"Fast XOR: A = 0x{self.registers['A']:02X}"
            })
        elif opcode == 0x76: # HLT
            self.is_halted = True
            self.execution_log.append({
                "pc": f"0x{current_pc:04X}",
                "cisc": "HLT",
                "cisc_cycles": 5,
                "risc": "-",
                "risc_cycles": "-",
                "desc": "System Halt"
            })
            return False
        else:
            messagebox.showerror("Execution Error", f"Unknown Opcode: 0x{opcode:02X} at PC: 0x{self.PC-1:04X}")
            self.is_halted = True
            return False
        return True


class Assembler:
    OPCODES = {
        "MVI A": 0x3E, "MVI B": 0x06, "MVI C": 0x0E, "LDA": 0x3A,
        "R_ADD A, B": 0xE0, "R_SUB A, C": 0xE1, "R_AND A, B": 0xE3, "R_XOR A, B": 0xE5,
        "HLT": 0x76
    }

    @staticmethod
    def assemble(source_code):
        bytes_out = []
        lines = source_code.strip().split('\n')
        for line_num, line in enumerate(lines, 1):
            line = line.split(';')[0].strip()
            if not line:
                continue
            if line.startswith("MVI"):
                parts = line.split(',')
                reg_key = parts[0].strip()
                val = int(parts[1].strip(), 16)
                bytes_out.extend([Assembler.OPCODES[reg_key], val & 0xFF])
            elif line.startswith("LDA"):
                parts = line.split()
                addr = int(parts[1].strip(), 16)
                bytes_out.extend([Assembler.OPCODES["LDA"], addr & 0xFF, (addr >> 8) & 0xFF])
            elif line in Assembler.OPCODES:
                bytes_out.append(Assembler.OPCODES[line])
            else:
                raise ValueError(f"Unknown instruction on line {line_num}: '{line}'")
        return bytes_out


class GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Industrial Hybrid 8085 Microarchitecture Profiler & Simulator")
        self.root.geometry("1380x820")
        self.root.configure(bg="#121212")

        self.cpu = HybridCPU8085()
        self.build_ui()
        self.sync_ui()

    def build_ui(self):
        # Action Toolbar
        toolbar = tk.Frame(self.root, bg="#1E1E1E", pady=8, padx=10)
        toolbar.pack(fill=tk.X)

        tk.Button(toolbar, text="Assemble & Load", command=self.load, bg="#2E7D32", fg="white", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=4)
        tk.Button(toolbar, text="Single Step", command=self.step, bg="#1565C0", fg="white", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=4)
        tk.Button(toolbar, text="Run Pipeline", command=self.run, bg="#C62828", fg="white", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=4)
        tk.Button(toolbar, text="Reset CPU", command=self.reset, bg="#424242", fg="white", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=4)

        # Main Layout
        layout = tk.Frame(self.root, bg="#121212")
        layout.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Column 1
        left_col = tk.Frame(layout, bg="#121212")
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        editor_frame = tk.LabelFrame(left_col, text="Assembly Source Code", bg="#1E1E1E", fg="#00E676", font=("Segoe UI", 10, "bold"))
        editor_frame.pack(fill=tk.BOTH, expand=True)

        sample_program = (
            "MVI A, 0A      ; CISC: Load A with 0x0A (7 Cycles)\n"
            "MVI B, 05      ; CISC: Load B with 0x05 (7 Cycles)\n"
            "R_ADD A, B     ; RISC: Fast Register Add (1 Cycle)\n"
            "HLT            ; Halt Execution\n"
        )
        self.text_editor = tk.Text(editor_frame, bg="#000000", fg="#A5D6A7", insertbackground="white", font=("Consolas", 10), height=8)
        self.text_editor.insert(tk.END, sample_program)
        self.text_editor.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        side_by_side_frame = tk.LabelFrame(left_col, text="Side-by-Side CISC vs. RISC Execution Profiler", bg="#1E1E1E", fg="#00E676", font=("Segoe UI", 10, "bold"))
        side_by_side_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#121212", foreground="white", fieldbackground="#121212", rowheight=22)
        style.configure("Treeview.Heading", background="#2D2D2D", foreground="#00E676", font=("Segoe UI", 9, "bold"))

        columns = ("PC", "CISC_INST", "CISC_CYC", "RISC_INST", "RISC_CYC", "EFFECT")
        self.trace_table = ttk.Treeview(side_by_side_frame, columns=columns, show="headings", height=8)

        self.trace_table.heading("PC", text="PC")
        self.trace_table.heading("CISC_INST", text="CISC Instruction")
        self.trace_table.heading("CISC_CYC", text="CISC T-States")
        self.trace_table.heading("RISC_INST", text="RISC Instruction")
        self.trace_table.heading("RISC_CYC", text="RISC T-States")
        self.trace_table.heading("EFFECT", text="Pipeline Effect")

        self.trace_table.column("PC", width=60, anchor="center")
        self.trace_table.column("CISC_INST", width=120, anchor="w")
        self.trace_table.column("CISC_CYC", width=80, anchor="center")
        self.trace_table.column("RISC_INST", width=120, anchor="w")
        self.trace_table.column("RISC_CYC", width=80, anchor="center")
        self.trace_table.column("EFFECT", width=160, anchor="w")

        self.trace_table.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        gemma_frame = tk.LabelFrame(left_col, text="Gemma AI Compiler", bg="#1E1E1E", fg="#BB86FC", font=("Segoe UI", 10, "bold"))
        gemma_frame.pack(fill=tk.X, pady=(5, 0))

        self.ai_prompt = tk.Entry(gemma_frame, bg="#2D2D2D", fg="white", font=("Segoe UI", 10), insertbackground="white")
        self.ai_prompt.insert(0, "Write a program to load 0x0F into A and 0x05 into C, then subtract using RISC.")
        self.ai_prompt.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)

        self.btn_ai = tk.Button(gemma_frame, text="Generate & Run", command=self.ask_gemma, bg="#7B1FA2", fg="white", font=("Segoe UI", 9, "bold"))
        self.btn_ai.pack(side=tk.RIGHT, padx=5, pady=5)

        # Column 2
        mid_col = tk.Frame(layout, bg="#121212")
        mid_col.pack(side=tk.LEFT, fill=tk.Y, padx=5)

        reg_box = tk.LabelFrame(mid_col, text="Register State", bg="#1E1E1E", fg="#00E676", font=("Segoe UI", 10, "bold"), width=180)
        reg_box.pack(fill=tk.X, pady=(0, 5))

        self.reg_views = {}
        for r in ['A', 'B', 'C', 'D', 'E', 'H', 'L', 'PC', 'SP']:
            row = tk.Frame(reg_box, bg="#1E1E1E")
            row.pack(fill=tk.X, padx=8, pady=2)
            tk.Label(row, text=f"{r}:", bg="#1E1E1E", fg="#B0BEC5", font=("Consolas", 10), width=4, anchor="w").pack(side=tk.LEFT)
            val_lbl = tk.Label(row, text="0x00", bg="#1E1E1E", fg="#FFD54F", font=("Consolas", 10, "bold"))
            val_lbl.pack(side=tk.RIGHT)
            self.reg_views[r] = val_lbl

        flags_box = tk.LabelFrame(mid_col, text="Flag Registers", bg="#1E1E1E", fg="#00E676", font=("Segoe UI", 10, "bold"))
        flags_box.pack(fill=tk.X, pady=5)

        self.flag_views = {}
        for f in ['Z', 'S', 'P', 'CY']:
            row = tk.Frame(flags_box, bg="#1E1E1E")
            row.pack(fill=tk.X, padx=8, pady=2)
            tk.Label(row, text=f"{f}:", bg="#1E1E1E", fg="#B0BEC5", font=("Consolas", 10), width=4, anchor="w").pack(side=tk.LEFT)
            val_lbl = tk.Label(row, text="0", bg="#1E1E1E", fg="#FF5252", font=("Consolas", 10, "bold"))
            val_lbl.pack(side=tk.RIGHT)
            self.flag_views[f] = val_lbl

        # Column 3
        right_col = tk.Frame(layout, bg="#121212")
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        metrics_frame = tk.LabelFrame(right_col, text="Performance & Metrics", bg="#1E1E1E", fg="#00E676", font=("Segoe UI", 10, "bold"))
        metrics_frame.pack(fill=tk.X, pady=(0, 5))

        self.lbl_cycles = tk.Label(metrics_frame, text="Total T-States: 0", bg="#1E1E1E", fg="white", font=("Segoe UI", 9), anchor="w")
        self.lbl_cycles.pack(fill=tk.X, padx=8, pady=2)

        self.lbl_cpi = tk.Label(metrics_frame, text="Overall CPI: 0.00", bg="#1E1E1E", fg="#81D4FA", font=("Segoe UI", 9, "bold"), anchor="w")
        self.lbl_cpi.pack(fill=tk.X, padx=8, pady=2)

        self.lbl_risc_efficiency = tk.Label(metrics_frame, text="RISC Latency Reduction: 0.0%", bg="#1E1E1E", fg="#69F0AE", font=("Segoe UI", 9, "bold"), anchor="w")
        self.lbl_risc_efficiency.pack(fill=tk.X, padx=8, pady=2)

        chart_frame = tk.LabelFrame(right_col, text="Execution Analytics", bg="#1E1E1E", fg="#00E676", font=("Segoe UI", 10, "bold"))
        chart_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(5, 3), facecolor='#1E1E1E')
        self.fig.tight_layout(pad=2.0)
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def ask_gemma(self):
        prompt_text = self.ai_prompt.get().strip()
        if not prompt_text:
            return

        self.btn_ai.config(state=tk.DISABLED, text="Compiling...")

        def fetch_ai_response():
            system_instruction = (
                "You are an expert assembly generator for a custom 8085 CPU.\n"
                "Output ONLY valid assembly code with actual 2-digit HEX values (e.g. 0F, 05, 00).\n"
                "NEVER output words like 'hex' or placeholders.\n\n"
                "Allowed Ops:\n"
                "MVI A, [hex]\n"
                "MVI B, [hex]\n"
                "MVI C, [hex]\n"
                "R_ADD A, B\n"
                "R_SUB A, C\n"
                "R_AND A, B\n"
                "R_XOR A, B\n"
                "HLT\n\n"
                "Example Prompt: Load 0F into A and 05 into C then subtract using RISC\n"
                "Example Output:\n"
                "MVI A, 0F\n"
                "MVI C, 05\n"
                "R_SUB A, C\n"
                "HLT"
            )
            try:
                response = ollama.chat(
                    model='gemma3:1b',
                    messages=[
                        {'role': 'system', 'content': system_instruction},
                        {'role': 'user', 'content': prompt_text}
                    ],
                    options={'num_predict': 96, 'temperature': 0.1},
                    keep_alive=-1
                )
                
                if hasattr(response, 'message'):
                    generated_code = response.message.content.strip()
                else:
                    generated_code = response['message']['content'].strip()
                
                self.root.after(0, self.auto_load_and_run, generated_code)
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda: messagebox.showerror("Ollama Error", f"Could not connect: {error_msg}"))
            finally:
                self.root.after(0, lambda: self.btn_ai.config(state=tk.NORMAL, text="Generate & Run"))

        threading.Thread(target=fetch_ai_response, daemon=True).start()

    def auto_load_and_run(self, new_code):
        clean_lines = [line for line in new_code.split('\n') if not line.strip().startswith("```")]
        self.text_editor.delete("1.0", tk.END)
        self.text_editor.insert(tk.END, "\n".join(clean_lines))
        
        # Auto-assemble and run to populate graphs
        try:
            self.load()
            self.run()
        except Exception:
            pass

    def sync_ui(self):
        # Update Registers
        for reg, lbl in self.reg_views.items():
            val = self.cpu.registers.get(reg, getattr(self.cpu, reg, 0))
            fmt = f"0x{val:04X}" if reg in ['PC', 'SP'] else f"0x{val:02X}"
            lbl.config(text=fmt)

        # Update Flags
        for flag, lbl in self.flag_views.items():
            lbl.config(text=str(self.cpu.flags[flag]))

        # Update Table Log
        for row in self.trace_table.get_children():
            self.trace_table.delete(row)
            
        for entry in self.cpu.execution_log:
            self.trace_table.insert("", tk.END, values=(
                entry["pc"],
                entry["cisc"],
                entry["cisc_cycles"],
                entry["risc"],
                entry["risc_cycles"],
                entry["desc"]
            ))

        # Metrics
        total_inst = self.cpu.cisc_count + self.cpu.risc_count
        cpi = (self.cpu.cycles / total_inst) if total_inst > 0 else 0.0
        cisc_equivalent_cycles = total_inst * 7
        speedup = ((cisc_equivalent_cycles - self.cpu.cycles) / cisc_equivalent_cycles * 100) if cisc_equivalent_cycles > 0 else 0.0

        self.lbl_cycles.config(text=f"Total T-States: {self.cpu.cycles}")
        self.lbl_cpi.config(text=f"Overall CPI (Cycles/Inst): {cpi:.2f}")
        self.lbl_risc_efficiency.config(text=f"RISC Latency Reduction: {speedup:.1f}%")

        # Update Matplotlib Charts
        self.ax1.clear()
        self.ax2.clear()
        self.ax1.set_facecolor('#121212')
        self.ax2.set_facecolor('#121212')

        labels = ['CISC', 'RISC']
        counts = [self.cpu.cisc_count, self.cpu.risc_count]
        colors = ['#FF9800', '#4CAF50']
        
        if sum(counts) > 0:
            self.ax1.pie(counts, labels=labels, colors=colors, autopct='%1.0f%%', textprops={'color': 'w', 'fontsize': 8})
            self.ax1.set_title("Instruction Mix", color='white', fontsize=9, fontweight='bold')
        else:
            self.ax1.text(0.5, 0.5, "No Data", color='gray', ha='center', va='center')
            self.ax1.axis('off')

        cisc_cycles = self.cpu.cisc_count * 7
        risc_cycles = self.cpu.risc_count * 1
        
        bars = self.ax2.bar(['CISC Cost', 'RISC Cost'], [cisc_cycles, risc_cycles], color=['#FF9800', '#4CAF50'])
        self.ax2.set_title("T-State Burden", color='white', fontsize=9, fontweight='bold')
        self.ax2.tick_params(colors='white', labelsize=8)
        
        # Add labels on top of bars
        for bar in bars:
            yval = bar.get_height()
            if yval > 0:
                self.ax2.text(bar.get_x() + bar.get_width()/2, yval + 0.1, f'{int(yval)}', ha='center', va='bottom', color='white', fontsize=8)

        self.fig.tight_layout(pad=1.5)
        self.canvas.draw()

    def load(self):
        self.cpu.reset()
        src = self.text_editor.get("1.0", tk.END)
        try:
            bytecode = Assembler.assemble(src)
            for idx, b in enumerate(bytecode):
                self.cpu.memory[idx] = b
            self.sync_ui()
        except Exception as e:
            messagebox.showerror("Assembler Error", str(e))

    def step(self):
        if not self.cpu.is_halted:
            self.cpu.step()
            self.sync_ui()

    def run(self):
        guard = 0
        while not self.cpu.is_halted and guard < 5000:
            if not self.cpu.step():
                break
            guard += 1
        self.sync_ui()

    def reset(self):
        self.cpu.reset()
        self.sync_ui()


if __name__ == "__main__":
    app_window = tk.Tk()
    SimulatorApp = GUI(app_window)
    app_window.mainloop()