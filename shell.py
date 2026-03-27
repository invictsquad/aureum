#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aureum Interactive Shell (REPL)
Interactive REPL with hybrid execution: Python Parser + Rust Kernel via FFI

Author: Luiz Antônio De Lima Mendonça
Location: Resende, RJ, Brazil
Instagram: @luizinvict
Date: 2026-03-25
"""

import sys
import io
from pathlib import Path
from typing import Dict, Any, Optional
import psutil
import os

# Fix encoding on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Adiciona frontend ao path
sys.path.insert(0, str(Path(__file__).parent / "frontend"))

from aureum_compiler import AureumTranspiler
from aureum_ffi import get_kernel


class Tensor:
    """Represents a tensor in the REPL"""
    
    def __init__(self, shape: list, dtype: str, name: str):
        self.shape = shape
        self.dtype = dtype
        self.name = name
        self.size = shape[0] if shape else 0
        self.data = None
        self.packed_data = None
        
        # Calculate memory usage
        if dtype == "bit1.58":
            self.memory_bytes = (self.size + 3) // 4  # 2 bits per weight
            self.is_bitnet = True
        elif dtype == "int16":
            self.memory_bytes = self.size * 2
            self.is_bitnet = False
        elif dtype == "int32":
            self.memory_bytes = self.size * 4
            self.is_bitnet = False
        elif dtype == "float32":
            self.memory_bytes = self.size * 4
            self.is_bitnet = False
        else:
            self.memory_bytes = self.size * 4
            self.is_bitnet = False
    
    def __repr__(self):
        return f"Tensor(shape={self.shape}, dtype={self.dtype}, memory={self.format_bytes(self.memory_bytes)})"
    
    @staticmethod
    def format_bytes(bytes_val):
        """Formats bytes into human-readable units"""
        if bytes_val >= 1_000_000_000:
            return f"{bytes_val / 1_000_000_000:.2f} GB"
        elif bytes_val >= 1_000_000:
            return f"{bytes_val / 1_000_000:.2f} MB"
        elif bytes_val >= 1_000:
            return f"{bytes_val / 1_000:.2f} KB"
        else:
            return f"{bytes_val} B"


class AureumShell:
    """Interactive shell for Aureum with hybrid execution"""
    
    def __init__(self):
        self.grammar_path = Path(__file__).parent / "frontend" / "grammar.lark"
        self.transpiler = AureumTranspiler(str(self.grammar_path))
        
        # Load Rust kernel via FFI
        try:
            self.kernel = get_kernel()
            self.kernel_loaded = True
            print("✅ Rust kernel loaded via FFI")
        except Exception as e:
            print(f"⚠️  Rust kernel not available: {e}")
            print("   Compile with: cd backend && cargo build --release")
            self.kernel_loaded = False
        
        # REPL state
        self.variables: Dict[str, Any] = {}
        self.tensors: Dict[str, Tensor] = {}
        self.global_scale = None  # Global Matryoshka scale
        self.history = []
        
        # Current process for memory monitoring
        self.process = psutil.Process(os.getpid())
        self.initial_memory = self.process.memory_info().rss
    
    def print_banner(self):
        """Prints welcome banner"""
        print("\n" + "="*70)
        print("  🌟 Aureum Interactive Shell v1.0 (REPL)")
        print("  High-Performance AI Language")
        print("  Hybrid Execution: Python Parser + Rust Kernel (FFI)")
        print("="*70)
        print("\nAuthor: Luiz Antônio De Lima Mendonça")
        print("Location: Resende, RJ, Brazil")
        print("Instagram: @luizinvict\n")
        print("Special commands:")
        print("  .help       - Show help")
        print("  .examples   - Show code examples")
        print("  .scale N    - Set global Matryoshka scale")
        print("  .vars       - List variables and tensors")
        print("  .memory     - Show memory usage")
        print("  .clear      - Clear variables")
        print("  .exit       - Exit the shell")
        print("\nTip: Declare tensors and run BitNet operations in real time!")
        print("="*70 + "\n")
    
    def print_help(self):
        """Prints help"""
        print("\n" + "="*70)
        print("  HELP - Aureum REPL")
        print("="*70 + "\n")
        print("BASIC SYNTAX:")
        print("-" * 70)
        print("""
# Declare tensor
input = tensor(shape=[1024], type=int16)
weights = tensor(shape=[1024], type=bit1.58)

# Run BitNet inference
result = input * weights[::512]

# Supported types:
  - bit1.58   (ternary weights: -1, 0, 1) ⚡ 2 bits/weight
  - int16     (16-bit integers)
  - int32     (32-bit integers)
  - float32   (floating point)

# Matryoshka operator:
  tensor[::scale]  # Processes only 'scale' elements
  
# Global scale:
  .scale 512        # Sets default scale for all operations
""")
        print("="*70 + "\n")
    
    def print_examples(self):
        """Prints examples"""
        print("\n" + "="*70)
        print("  EXAMPLES - Aureum REPL")
        print("="*70 + "\n")
        
        print("1. Declare tensors and check memory usage:")
        print("-" * 70)
        print(">>> input = tensor(shape=[1024], type=int16)")
        print(">>> weights = tensor(shape=[1024], type=bit1.58)")
        print()
        
        print("2. Run BitNet inference:")
        print("-" * 70)
        print(">>> result = input * weights[::1024]")
        print()
        
        print("3. Use global Matryoshka scale:")
        print("-" * 70)
        print(">>> .scale 512")
        print(">>> result = input * weights  # Uses scale 512 automatically")
        print()
        
        print("="*70 + "\n")
    
    def show_memory_usage(self):
        """Shows current memory usage"""
        current_memory = self.process.memory_info().rss
        used_memory = current_memory - self.initial_memory
        
        print(f"\n💾 Memory Usage:")
        print(f"   Process: {Tensor.format_bytes(current_memory)}")
        print(f"   Used by REPL: {Tensor.format_bytes(used_memory)}")
        
        if self.tensors:
            total_tensor_memory = sum(t.memory_bytes for t in self.tensors.values())
            print(f"   Allocated tensors: {Tensor.format_bytes(total_tensor_memory)}")
            
            # Calculate savings vs FP32
            total_elements = sum(t.size for t in self.tensors.values())
            fp32_memory = total_elements * 4
            if total_tensor_memory > 0:
                savings = (1 - total_tensor_memory / fp32_memory) * 100
                print(f"   Savings vs FP32: {savings:.1f}% ({Tensor.format_bytes(fp32_memory - total_tensor_memory)} saved)")
        print()
    
    def list_variables(self):
        """Lists variables and tensors"""
        if not self.tensors and not self.variables:
            print("\n(no variables defined)\n")
            return
        
        print("\n📊 Variables and Tensors:")
        print("-" * 70)
        
        if self.tensors:
            print("\nTensors:")
            for name, tensor in self.tensors.items():
                print(f"  {name:15} = {tensor}")
        
        if self.variables:
            print("\nOther variables:")
            for name, value in self.variables.items():
                if name not in self.tensors:
                    print(f"  {name:15} = {value}")
        
        print()
    
    def parse_tensor_declaration(self, line: str) -> Optional[Tensor]:
        """Parses tensor declaration"""
        try:
            # Grammar expects newline-terminated statements; accept single-line input too.
            normalized_line = line if line.endswith("\n") else f"{line}\n"
            tree = self.transpiler.parser.parse(normalized_line)
            
            for node in tree.iter_subtrees():
                if node.data == 'assignment':
                    var_name = node.children[0].value
                    
                    for child in node.iter_subtrees():
                        if child.data == 'tensor_expr':
                            shape_node = child.children[0]
                            type_node = child.children[1]
                            
                            shape = [int(c.value) for c in shape_node.children]
                            
                            type_map = {
                                'type_bit158': 'bit1.58',
                                'type_int16': 'int16',
                                'type_int32': 'int32',
                                'type_float32': 'float32',
                            }
                            dtype = type_map.get(type_node.data, 'unknown')
                            
                            return Tensor(shape, dtype, var_name)
            
            return None
            
        except Exception as e:
            return None
    
    def execute_tensor_declaration(self, tensor: Tensor):
        """Executes tensor declaration"""
        self.tensors[tensor.name] = tensor
        
        print(f"✅ Tensor '{tensor.name}' created:")
        print(f"   Shape: {tensor.shape}")
        print(f"   Type: {tensor.dtype}")
        print(f"   Memory: {tensor.format_bytes(tensor.memory_bytes)}", end="")
        
        if tensor.dtype == "bit1.58":
            fp32_memory = tensor.size * 4
            savings = (1 - tensor.memory_bytes / fp32_memory) * 100
            print(f" (vs FP32: {tensor.format_bytes(fp32_memory)}, {savings:.1f}% savings) ⚡")
        else:
            print()
        
        self.show_memory_usage()
    
    def process_command(self, line: str) -> bool:
        """Processes special commands"""
        line = line.strip()
        
        if line == ".help":
            self.print_help()
            return True
        
        elif line == ".examples":
            self.print_examples()
            return True
        
        elif line.startswith(".scale"):
            parts = line.split()
            if len(parts) == 2:
                try:
                    scale = int(parts[1])
                    self.global_scale = scale
                    print(f"✅ Global Matryoshka scale set: {scale}")
                except ValueError:
                    print("❌ Invalid scale. Use: .scale <number>")
            else:
                if self.global_scale:
                    print(f"Current scale: {self.global_scale}")
                else:
                    print("Global scale not set")
            return True
        
        elif line == ".vars":
            self.list_variables()
            return True
        
        elif line == ".memory":
            self.show_memory_usage()
            return True
        
        elif line == ".clear":
            self.variables.clear()
            self.tensors.clear()
            self.global_scale = None
            print("✅ Variables cleared")
            return True
        
        elif line == ".exit":
            print("\n👋 Goodbye!\n")
            sys.exit(0)
        
        return False
    
    def execute_line(self, line: str):
        """Executes a line of code"""
        line = line.strip()
        
        if not line:
            return
        
        if line.startswith("."):
            self.process_command(line)
            return
        
        tensor = self.parse_tensor_declaration(line)
        if tensor:
            self.execute_tensor_declaration(tensor)
            return
        
        print("⚠️  Unrecognized command. Use .help for help.")
    
    def run(self):
        """Main REPL loop"""
        self.print_banner()
        
        while True:
            try:
                prompt = ">>> "
                line = input(prompt)
                
                if line.strip():
                    self.history.append(line)
                
                self.execute_line(line)
                
            except KeyboardInterrupt:
                print("\n\n(Use .exit to quit)\n")
                continue
            
            except EOFError:
                print("\n\n👋 Goodbye!\n")
                break
            
            except Exception as e:
                print(f"❌ Error: {e}")


def main():
    """Main function"""
    shell = AureumShell()
    shell.run()


if __name__ == "__main__":
    main()
