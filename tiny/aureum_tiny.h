/**
 * Aureum Tiny Runtime - C API
 * Ultra-lightweight AI inference for microcontrollers
 * 
 * Features:
 * - < 10 KB code size
 * - < 2 KB RAM usage
 * - Zero heap allocation
 * - Integer-only arithmetic
 * 
 * Author: Luiz Antônio De Lima Mendonça
 * Location: Resende, RJ, Brazil
 * Instagram: @luizinvict
 * Date: 2026-03-26
 */

#ifndef AUREUM_TINY_H
#define AUREUM_TINY_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

// ─── Types ────────────────────────────────────────────────────────────────────

/**
 * Resultado de classificação
 */
typedef struct {
    uint8_t class_id;  ///< Classe predita (0 a 255)
    int32_t score;     ///< Score da classe
} AureumClassifyResult;

/**
 * Resultado de detecção
 */
typedef struct {
    int16_t position;   ///< Posição do padrão detectado (-1 se não detectado)
    int32_t confidence; ///< Confiança da detecção
    bool detected;      ///< Flag de detecção
} AureumDetectResult;

// ─── Core Functions ───────────────────────────────────────────────────────────

/**
 * Inicializa runtime Aureum Tiny
 * 
 * Deve ser chamado uma vez no início do programa.
 */
void aureum_tiny_init(void);

/**
 * Inferência BitNet básica
 * 
 * Calcula dot product entre input e weights usando apenas
 * adições e subtrações (zero multiplicações FP).
 * 
 * @param input Vetor de entrada (int16)
 * @param input_len Tamanho do vetor de entrada
 * @param weights Pesos ternários compactados (2 bits cada)
 * @param weights_len Tamanho do buffer de pesos
 * @param output Buffer de saída (int32)
 * @param output_len Tamanho do buffer de saída
 * @param scale Escala Matryoshka (número de elementos a processar)
 * 
 * @example
 * int16_t input[4] = {10, 20, -5, 8};
 * uint8_t weights[1] = {0b10010001}; // [1, 0, -1, 1]
 * int32_t output[1];
 * aureum_tiny_infer_c(input, 4, weights, 1, output, 1, 4);
 * // output[0] = 23
 */
void aureum_tiny_infer_c(
    const int16_t* input,
    size_t input_len,
    const uint8_t* weights,
    size_t weights_len,
    int32_t* output,
    size_t output_len,
    size_t scale
);

/**
 * Classificação multi-classe
 * 
 * Classifica input em uma das num_classes classes.
 * Retorna a classe com maior score.
 * 
 * @param input Vetor de entrada
 * @param input_len Tamanho do vetor de entrada
 * @param weights Pesos de todas as classes concatenados
 * @param weights_len Tamanho do buffer de pesos
 * @param num_classes Número de classes (máximo 255)
 * @param scale Escala Matryoshka
 * @param result Ponteiro para resultado
 * 
 * @example
 * int16_t input[64];
 * read_sensor(input, 64);
 * 
 * uint8_t model_weights[512]; // Modelo pré-treinado
 * AureumClassifyResult result;
 * 
 * aureum_tiny_classify_c(input, 64, model_weights, 512, 4, 64, &result);
 * 
 * switch(result.class_id) {
 *     case 0: printf("Normal\n"); break;
 *     case 1: printf("Anomalia detectada!\n"); break;
 *     case 2: printf("Alerta\n"); break;
 *     case 3: printf("Crítico\n"); break;
 * }
 */
void aureum_tiny_classify_c(
    const int16_t* input,
    size_t input_len,
    const uint8_t* weights,
    size_t weights_len,
    uint8_t num_classes,
    size_t scale,
    AureumClassifyResult* result
);

/**
 * Detecção de padrão em sequência
 * 
 * Usa sliding window para encontrar padrão na sequência.
 * 
 * @param sequence Sequência de entrada
 * @param seq_len Tamanho da sequência
 * @param pattern Pesos ternários do padrão
 * @param pattern_len Tamanho do padrão
 * @param threshold Score mínimo para detecção positiva
 * @param result Ponteiro para resultado
 * 
 * @example
 * int16_t audio_buffer[1024];
 * read_microphone(audio_buffer, 1024);
 * 
 * uint8_t wake_word_pattern[32]; // Padrão de "wake word"
 * AureumDetectResult result;
 * 
 * aureum_tiny_detect_c(audio_buffer, 1024, wake_word_pattern, 32, 1000, &result);
 * 
 * if(result.detected) {
 *     printf("Wake word detectado na posição %d!\n", result.position);
 *     activate_assistant();
 * }
 */
void aureum_tiny_detect_c(
    const int16_t* sequence,
    size_t seq_len,
    const uint8_t* pattern,
    size_t pattern_len,
    int32_t threshold,
    AureumDetectResult* result
);

// ─── Helper Macros ────────────────────────────────────────────────────────────

/**
 * Calcula tamanho necessário de buffer de pesos
 * 
 * @param num_weights Número de pesos ternários
 * @return Tamanho em bytes (4 pesos por byte)
 */
#define AUREUM_WEIGHTS_SIZE(num_weights) (((num_weights) + 3) / 4)

/**
 * Declara modelo na Flash (PROGMEM para Arduino)
 */
#ifdef ARDUINO
#define AUREUM_MODEL_FLASH const PROGMEM
#else
#define AUREUM_MODEL_FLASH const
#endif

#ifdef __cplusplus
}
#endif

#endif // AUREUM_TINY_H
