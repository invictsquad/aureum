#![no_std]
#![allow(dead_code)]

/// Aureum Tiny Runtime
/// Ultra-lightweight AI inference engine for microcontrollers
/// 
/// Features:
/// - no_std: Runs without standard library
/// - < 10 KB code size
/// - < 2 KB RAM usage
/// - Zero heap allocation
/// - Integer-only arithmetic
/// - BitNet b1.58 ternary weights
///
/// Author: Luiz Antônio De Lima Mendonça
/// Location: Resende, RJ, Brazil
/// Instagram: @luizinvict
/// Date: 2026-03-26

// ─── Core Types ───────────────────────────────────────────────────────────────

/// Resultado de classificação
#[repr(C)]
#[derive(Debug, Clone, Copy)]
pub struct ClassifyResult {
    pub class_id: u8,
    pub score: i32,
}

/// Resultado de detecção
#[repr(C)]
#[derive(Debug, Clone, Copy)]
pub struct DetectResult {
    pub position: i16,
    pub confidence: i32,
    pub detected: bool,
}

// ─── Core Engine ──────────────────────────────────────────────────────────────

/// Decodifica 2 bits para valor ternário: 00=0, 01=1, 10=-1
#[inline(always)]
fn decode_ternary(bits: u8) -> i8 {
    match bits & 0b11 {
        0b00 =>  0,
        0b01 =>  1,
        0b10 => -1,
        _    =>  0,
    }
}

/// Extrai peso ternário do buffer compactado
#[inline(always)]
fn get_weight(packed: &[u8], index: usize) -> i8 {
    let byte_idx = index / 4;
    let bit_offset = (index % 4) * 2;
    
    if byte_idx >= packed.len() {
        return 0;
    }
    
    let bits = (packed[byte_idx] >> bit_offset) & 0b11;
    decode_ternary(bits)
}

/// Inferência BitNet básica
///
/// Calcula dot product entre input e weights usando apenas
/// adições e subtrações (zero multiplicações FP).
///
/// # Parâmetros
/// - `input`: Vetor de entrada (int16)
/// - `weights`: Pesos ternários compactados (2 bits cada)
/// - `output`: Buffer de saída (int32)
/// - `scale`: Escala Matryoshka (número de elementos a processar)
///
/// # Exemplo
/// ```no_run
/// let input = [10i16, 20, -5, 8];
/// let weights = [0b10010001u8]; // [1, 0, -1, 1]
/// let mut output = [0i32; 1];
/// aureum_tiny_infer(&input, &weights, &mut output, 4);
/// // output[0] = 10*1 + 20*0 + (-5)*(-1) + 8*1 = 23
/// ```
pub fn aureum_tiny_infer(
    input: &[i16],
    weights: &[u8],
    output: &mut [i32],
    scale: usize
) {
    let n = input.len().min(scale);
    
    for i in 0..output.len() {
        let mut acc: i32 = 0;
        
        for j in 0..n {
            let weight_idx = i * n + j;
            let weight = get_weight(weights, weight_idx);
            
            // Apenas adição/subtração (zero multiplicação FP)
            acc += input[j] as i32 * weight as i32;
        }
        
        output[i] = acc;
    }
}

/// Classificação multi-classe
///
/// Classifica input em uma das num_classes classes.
/// Retorna a classe com maior score.
///
/// # Parâmetros
/// - `input`: Vetor de entrada
/// - `weights`: Pesos de todas as classes concatenados
/// - `num_classes`: Número de classes (máximo 255)
/// - `scale`: Escala Matryoshka
///
/// # Retorno
/// ClassifyResult com classe predita e score
pub fn aureum_tiny_classify(
    input: &[i16],
    weights: &[u8],
    num_classes: u8,
    scale: usize
) -> ClassifyResult {
    let input_len = input.len().min(scale);
    let mut best_class = 0u8;
    let mut best_score = i32::MIN;
    
    for class in 0..num_classes {
        let mut acc: i32 = 0;
        
        for j in 0..input_len {
            let weight_idx = (class as usize) * input_len + j;
            let weight = get_weight(weights, weight_idx);
            acc += input[j] as i32 * weight as i32;
        }
        
        if acc > best_score {
            best_score = acc;
            best_class = class;
        }
    }
    
    ClassifyResult {
        class_id: best_class,
        score: best_score,
    }
}

/// Detecção de padrão em sequência
///
/// Usa sliding window para encontrar padrão na sequência.
///
/// # Parâmetros
/// - `sequence`: Sequência de entrada
/// - `pattern`: Pesos ternários do padrão
/// - `threshold`: Score mínimo para detecção positiva
///
/// # Retorno
/// DetectResult com posição e confiança
pub fn aureum_tiny_detect(
    sequence: &[i16],
    pattern: &[u8],
    threshold: i32
) -> DetectResult {
    let pattern_len = (pattern.len() * 4).min(sequence.len());
    
    if sequence.len() < pattern_len {
        return DetectResult {
            position: -1,
            confidence: 0,
            detected: false,
        };
    }
    
    let mut best_pos = -1i16;
    let mut best_score = i32::MIN;
    
    // Sliding window
    let num_windows = sequence.len() - pattern_len + 1;
    for pos in 0..num_windows {
        let mut acc: i32 = 0;
        
        for j in 0..pattern_len {
            let weight = get_weight(pattern, j);
            acc += sequence[pos + j] as i32 * weight as i32;
        }
        
        if acc > best_score {
            best_score = acc;
            best_pos = pos as i16;
        }
    }
    
    DetectResult {
        position: best_pos,
        confidence: best_score,
        detected: best_score >= threshold,
    }
}

// ─── FFI para C ───────────────────────────────────────────────────────────────

/// Inicializa runtime (placeholder para futuras features)
#[no_mangle]
pub extern "C" fn aureum_tiny_init() {
    // Nada a fazer por enquanto
    // Futuro: inicializar hardware-specific features
}

/// Inferência básica (FFI)
#[no_mangle]
pub extern "C" fn aureum_tiny_infer_c(
    input: *const i16,
    input_len: usize,
    weights: *const u8,
    weights_len: usize,
    output: *mut i32,
    output_len: usize,
    scale: usize
) {
    if input.is_null() || weights.is_null() || output.is_null() {
        return;
    }
    
    unsafe {
        let input_slice = core::slice::from_raw_parts(input, input_len);
        let weights_slice = core::slice::from_raw_parts(weights, weights_len);
        let output_slice = core::slice::from_raw_parts_mut(output, output_len);
        
        aureum_tiny_infer(input_slice, weights_slice, output_slice, scale);
    }
}

/// Classificação (FFI)
#[no_mangle]
pub extern "C" fn aureum_tiny_classify_c(
    input: *const i16,
    input_len: usize,
    weights: *const u8,
    weights_len: usize,
    num_classes: u8,
    scale: usize,
    result: *mut ClassifyResult
) {
    if input.is_null() || weights.is_null() || result.is_null() {
        return;
    }
    
    unsafe {
        let input_slice = core::slice::from_raw_parts(input, input_len);
        let weights_slice = core::slice::from_raw_parts(weights, weights_len);
        
        let res = aureum_tiny_classify(input_slice, weights_slice, num_classes, scale);
        *result = res;
    }
}

/// Detecção (FFI)
#[no_mangle]
pub extern "C" fn aureum_tiny_detect_c(
    sequence: *const i16,
    seq_len: usize,
    pattern: *const u8,
    pattern_len: usize,
    threshold: i32,
    result: *mut DetectResult
) {
    if sequence.is_null() || pattern.is_null() || result.is_null() {
        return;
    }
    
    unsafe {
        let seq_slice = core::slice::from_raw_parts(sequence, seq_len);
        let pattern_slice = core::slice::from_raw_parts(pattern, pattern_len);
        
        let res = aureum_tiny_detect(seq_slice, pattern_slice, threshold);
        *result = res;
    }
}

// ─── Panic Handler (required for no_std) ─────────────────────────────────────

#[cfg(not(test))]
#[panic_handler]
fn panic(_info: &core::panic::PanicInfo) -> ! {
    loop {}
}

// ─── Testes ───────────────────────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_decode_ternary() {
        assert_eq!(decode_ternary(0b00),  0);
        assert_eq!(decode_ternary(0b01),  1);
        assert_eq!(decode_ternary(0b10), -1);
        assert_eq!(decode_ternary(0b11),  0);
    }
    
    #[test]
    fn test_get_weight() {
        // Byte 0b00010001 contém 4 pesos em ordem LSB first:
        // bits 0-1 (0b01) = 1
        // bits 2-3 (0b00) = 0
        // bits 4-5 (0b00) = 0
        // bits 6-7 (0b00) = 0
        let packed = [0b00000001u8]; // [1, 0, 0, 0]
        assert_eq!(get_weight(&packed, 0),  1);
        assert_eq!(get_weight(&packed, 1),  0);
        assert_eq!(get_weight(&packed, 2),  0);
        assert_eq!(get_weight(&packed, 3),  0);
    }
    
    #[test]
    fn test_infer_basic() {
        let input = [10i16, 20, -5, 8];
        // Pesos: [1, 0, -1, 1]
        // 0b01 = 1, 0b00 = 0, 0b10 = -1, 0b01 = 1
        // Byte: 0b01100001
        let weights = [0b01100001u8];
        let mut output = [0i32; 1];
        
        aureum_tiny_infer(&input, &weights, &mut output, 4);
        
        // 10*1 + 20*0 + (-5)*(-1) + 8*1 = 10 + 0 + 5 + 8 = 23
        assert_eq!(output[0], 23);
    }
    
    #[test]
    fn test_classify() {
        // 3 classes, 4 features
        let input = [10i16, 20, -5, 8];
        let weights = [
            0b01100001u8, // classe 0: [1, 0, -1, 1] = 23
            0b00010100u8, // classe 1: [0, 1,  1, 0] = 15
            0b01000001u8, // classe 2: [1, 0,  0, 1] = 18
        ];
        
        let result = aureum_tiny_classify(&input, &weights, 3, 4);
        
        assert_eq!(result.class_id, 0); // Classe 0 tem maior score
        assert_eq!(result.score, 23);
    }
    
    #[test]
    fn test_detect() {
        let sequence = [5i16, 3, 10, -8, 7, 1, 2];
        // Padrão: [1, -1, 1] = 0b01, 0b10, 0b01 = 0b01100101
        let pattern = [0b01100101u8];
        
        let result = aureum_tiny_detect(&sequence, &pattern, 0);
        
        assert!(result.detected);
        // Melhor match deve estar em alguma posição
        assert!(result.position >= 0);
    }
    
    #[test]
    fn test_matryoshka() {
        let input = [10i16, 20, 30, 40];
        let weights = [0b01100001u8]; // [1, 0, -1, 1]
        let mut output = [0i32; 1];
        
        // Escala 50% (processa apenas 2 elementos)
        aureum_tiny_infer(&input, &weights, &mut output, 2);
        
        // 10*1 + 20*0 = 10
        assert_eq!(output[0], 10);
    }
}
