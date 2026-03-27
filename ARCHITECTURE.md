# 🏗️ Aureum Architecture - Technical Details

## Overview

Aureum is a hybrid programming language that combines:
- **Python frontend** (parsing and transpilation)
- **Rust backend** (high-performance execution)
- **Advanced techniques** (BitNet b1.58 + Matryoshka)

## Compilation Flow

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐      ┌──────────┐
│ .aur code   │  →   │ Lark Parser  │  →   │ AST         │  →   │ Rust     │
│ (Python-    │      │ (grammar.    │      │ (Tree)      │      │ (native  │
│  style)     │      │  lark)       │      │             │      │  code)   │
└─────────────┘      └──────────────┘      └─────────────┘      └──────────┘
                                                                       ↓
                                                                  ┌──────────┐
                                                                  │ Binary   │
                                                                  │ (x86_64/ │
                                                                  │  ARM)    │
                                                                  └──────────┘
```

## Main Components

### 1. Frontend (Python + Lark)

#### grammar.lark
Defines the language syntax using EBNF:

```ebnf
start: statement+

func_def: "def" NAME "(" params? ")" ":" _NL _INDENT statement+ _DEDENT

tensor_expr: "tensor" "(" "shape" "=" "[" shape_dims "]" "," "type" "=" type ")"

slice_expr: NAME "[" "::" NUMBER "]"  # Matryoshka operator
```

**Features:**
- Python-style indentation (via `AureumIndenter`)
- Native type support: `bit1.58`, `int16`, `int32`, `float32`
- Special `[::scale]` operator for Matryoshka

#### aureum_compiler.py
Transpiler that converts AST → Rust:

```python
class AureumTranspiler:
    def compile(self, source_code: str) -> str:
        tree = self.parser.parse(source_code)  # Lark parsing
        self._visit(tree)                       # AST traversal
        return "\n".join(self.rust_code)        # Rust code
```

**Visitor Pattern:**
- `_visit_func_def()`: Generates Rust functions
- `_visit_assignment()`: Detects tensors and operations
- `_process_bitnet_inference()`: Optimizes BitNet multiplications
- `_process_tensor()`: Allocates efficient memory

### 2. Backend (Rust)

#### src/lib.rs
Optimized inference kernel:

```rust
pub fn bitnet_infer(
    input: &[i32],           // Input (int16 as i32)
    packed_weights: &[u8],   // Packed weights (2 bits each)
    scale: usize             // Matryoshka limit
) -> i64 {
    let limit = scale.min(input.len());
    let mut accumulator: i64 = 0;
    
    for i in 0..limit {
        let w = get_weight(packed_weights, i);
        match w {
             1 => accumulator += input[i] as i64,  // Add
            -1 => accumulator -= input[i] as i64,  // Subtract
             _ => {}                                // Zero: skip
        }
    }
    
    accumulator
}
```

**Helper Functions:**

1. `decode_ternary(bits: u8) -> i32`
   - Decodes 2 bits → {-1, 0, 1}
   - Mapping: `00=-1, 01=0, 10=1`

2. `get_weight(packed: &[u8], i: usize) -> i32`
   - Extracts weight at index `i`
   - Each byte = 4 weights

3. `pack_ternary(weights: &[i8]) -> Vec<u8>`
   - Packs i8 array → 2-bit bytes
   - Used to prepare weights before inference

## Implemented Optimizations

### 1. BitNet b1.58 - Instruction Level

#### Problem: FP32 Multiplication
```asm
; Traditional multiplication (x86_64)
mulss xmm0, xmm1    ; ~5 cycles, complex pipeline
```

#### Solution: Integer Operations
```asm
; BitNet b1.58 (x86_64)
add   rax, rbx      ; weight = 1:  ~1 cycle
sub   rax, rbx      ; weight = -1: ~1 cycle
nop                 ; weight = 0:  0 cycles
```

**Gain:** 5x faster per operation

### 2. Memory Packing

#### Bit Layout
```
Byte: 0b10_01_00_10
      │  │  │  └─ Weight 0: 10 = +1
      │  │  └──── Weight 1: 00 = -1
      │  └─────── Weight 2: 01 =  0
      └────────── Weight 3: 10 = +1
```

#### Efficient Access
```rust
#[inline(always)]
fn get_weight(packed: &[u8], i: usize) -> i32 {
    let byte_idx = i / 4;              // Which byte?
    let bit_offset = (i % 4) * 2;      // Which position in byte?
    let bits = (packed[byte_idx] >> bit_offset) & 0b11;
    decode_ternary(bits)
}
```

**Gain:** 16x less memory, better cache utilization

### 3. Matryoshka - Control Flow

#### Implementation
```rust
let limit = scale.min(input.len());  // Dynamically limit
for i in 0..limit {                  // Short loop
    // Processes only 'limit' elements
}
```

#### Usage Example
```aureum
# Processes only 512 of 2048 elements (25%)
result = input * weights[::512]
```

**Gain:** 4x fewer iterations = 4x faster

### 4. Compiler Optimizations

#### Cargo.toml
```toml
[profile.release]
opt-level = 3        # -O3: aggressive optimization
lto = true           # Link-Time Optimization
codegen-units = 1    # Better cross-crate inlining
```

#### Inlining
```rust
#[inline(always)]  // Force inline (eliminates call overhead)
fn decode_ternary(bits: u8) -> i32 { ... }
```

**Gain:** Eliminates function call overhead

## Performance Analysis

### Computational Complexity

#### Traditional Operation (FP32)
```
Time = N × (T_load + T_mul + T_add)
     = N × (3 + 5 + 1) cycles
     = 9N cycles
```

#### BitNet b1.58
```
Time = N × (T_load + T_branch + T_add_or_sub)
     = N × (3 + 0.5 + 1) cycles  (branch prediction)
     = 4.5N cycles
```

**Theoretical speedup:** 2x

#### BitNet b1.58 + Matryoshka (50%)
```
Time = (N/2) × 4.5 cycles
     = 2.25N cycles
```

**Theoretical speedup:** 4x

### Memory Usage

| Type      | Bits/Weight | 1B Parameters | L1 Cache (32KB) |
|-----------|-------------|---------------|-----------------|
| FP32      | 32          | 4 GB          | 8K weights      |
| FP16      | 16          | 2 GB          | 16K weights     |
| INT8      | 8           | 1 GB          | 32K weights     |
| bit1.58   | 2           | 250 MB        | 128K weights    |

**Gain:** 16x more weights in cache = fewer cache misses

### Memory Bandwidth

```
FP32:     4 GB/s × 1B weights = 4 GB/s
bit1.58:  4 GB/s × 1B weights = 250 MB/s
```

**Gain:** 16x less pressure on memory controller

## Tests and Validation

### Test Suite (backend/src/lib.rs)

1. **test_pack_and_infer_full_scale**
   - Validates packing + full inference
   - Input: `[10, 20, 30, 40]`, Weights: `[1, -1, 0, 1]`
   - Expected: `10 - 20 + 0 + 40 = 30`

2. **test_matryoshka_scale**
   - Validates Matryoshka operator
   - Same input, but `scale=2`
   - Expected: `10 - 20 = -10` (ignores last 2)

3. **test_zero_weights_no_accumulation**
   - Validates zero weight optimization
   - Weights: `[0, 0, 0, 0]`
   - Expected: `0` (no operations executed)

4. **test_decode_ternary_values**
   - Validates bit decoding
   - `00 → -1, 01 → 0, 10 → 1`

### Run Tests
```bash
cd backend
cargo test --release
```

## Extensibility

### Adding New Types

1. Update `grammar.lark`:
```ebnf
type: "bit1.58" | "int16" | "int4" -> type_int4
```

2. Update `aureum_compiler.py`:
```python
type_map = {
    'type_int4': ('Vec<i8>', f'Vec::with_capacity({total_size})'),
}
```

3. Implement kernel in `lib.rs`:
```rust
pub fn int4_infer(input: &[i32], weights: &[i8]) -> i64 { ... }
```

### Adding Operators

1. Grammar:
```ebnf
expr: expr "**" term -> pow
```

2. Visitor:
```python
def _visit_pow(self, node: Tree):
    # Generate Rust code for exponentiation
```

## Technical Roadmap

### Short Term
- [ ] Multidimensional tensor support
- [ ] Element-wise operations (+, -, *, /)
- [ ] Activation functions (ReLU, Sigmoid)

### Medium Term
- [ ] SIMD (AVX2 for x86, NEON for ARM)
- [ ] Parallelization with Rayon
- [ ] Python binding (PyO3)

### Long Term
- [ ] GPU offloading (CUDA/ROCm)
- [ ] Mixed quantization (bit1.58 + int8)
- [ ] JIT compilation

## References

- **BitNet b1.58:** [arXiv:2402.17764](https://arxiv.org/abs/2402.17764)
- **Matryoshka Representations:** [arXiv:2205.13147](https://arxiv.org/abs/2205.13147)
- **Lark Parser:** https://github.com/lark-parser/lark
- **Rust Performance Book:** https://nnethercote.github.io/perf-book/
