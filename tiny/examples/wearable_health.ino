/**
 * Aureum Tiny - Wearable Health Example
 * Detecção de arritmia cardíaca em tempo real
 * 
 * Hardware: nRF52 ($3)
 * - 1 MB Flash
 * - 256 KB RAM
 * - Bluetooth LE
 * - Sensor ECG
 * 
 * Author: Luiz Antônio De Lima Mendonça
 * Date: 2026-03-26
 */

#include "aureum_tiny.h"

// Modelo treinado para detecção de arritmia (10 KB na Flash)
// Entrada: 128 amostras de ECG
// Saída: 4 classes (normal / taquicardia / bradicardia / fibrilação)
AUREUM_MODEL_FLASH uint8_t heart_model[128] = {
    // 128 amostras * 4 classes = 512 pesos
    // 512 / 4 = 128 bytes
    0x89, 0x12, 0x45, // ... (modelo pré-treinado)
};

// Buffer de ECG
int16_t ecg_buffer[128];
int ecg_index = 0;

// Histórico de detecções
uint8_t last_detections[10];
int detection_index = 0;

void setup() {
    Serial.begin(115200);
    
    // Inicializa Aureum Tiny
    aureum_tiny_init();
    Serial.println("Aureum Tiny inicializado!");
    
    // Inicializa sensor ECG
    init_ecg_sensor();
    
    // Inicializa Bluetooth
    init_bluetooth();
    
    Serial.println("Monitor cardíaco pronto!");
}

void loop() {
    // Lê amostra de ECG (250 Hz)
    int16_t sample = read_ecg_sample();
    ecg_buffer[ecg_index++] = sample;
    
    // Quando buffer está cheio, classifica
    if(ecg_index >= 128) {
        ecg_index = 0;
        
        // Classifica ritmo cardíaco
        AureumClassifyResult result;
        aureum_tiny_classify_c(
            ecg_buffer,
            128,
            heart_model,
            sizeof(heart_model),
            4,    // 4 classes
            128,  // Escala completa
            &result
        );
        
        // Armazena detecção
        last_detections[detection_index++] = result.class_id;
        if(detection_index >= 10) detection_index = 0;
        
        // Ação baseada no resultado
        handle_heart_status(result);
    }
    
    // Aguarda próxima amostra (4ms para 250 Hz)
    delay(4);
}

// ─── Funções auxiliares ──────────────────────────────────────────────────────

void init_ecg_sensor() {
    // Inicializa sensor ECG
    // (código específico do hardware)
}

int16_t read_ecg_sample() {
    // Lê amostra do sensor ECG
    // (código específico do hardware)
    return analogRead(ECG_PIN) - 512;
}

void init_bluetooth() {
    // Inicializa Bluetooth LE
    // (código específico do nRF52)
}

void handle_heart_status(AureumClassifyResult result) {
    const char* status_names[] = {
        "Normal",
        "Taquicardia",
        "Bradicardia",
        "Fibrilação"
    };
    
    Serial.print("Status cardíaco: ");
    Serial.println(status_names[result.class_id]);
    Serial.print("Confiança: ");
    Serial.println(result.score);
    
    // Se detectou problema
    if(result.class_id != 0) {
        // Verifica se é consistente (3+ detecções seguidas)
        int count = 0;
        for(int i = 0; i < 10; i++) {
            if(last_detections[i] == result.class_id) {
                count++;
            }
        }
        
        if(count >= 3) {
            Serial.println("ALERTA: Problema cardíaco detectado!");
            
            // Vibra
            vibrate(1000);
            
            // Envia alerta via Bluetooth
            send_bluetooth_alert(result.class_id, result.score);
            
            // Acende LED vermelho
            digitalWrite(LED_RED, HIGH);
        }
    } else {
        // Normal: LED verde
        digitalWrite(LED_GREEN, HIGH);
        digitalWrite(LED_RED, LOW);
    }
}

void vibrate(unsigned long duration_ms) {
    digitalWrite(VIBRATION_PIN, HIGH);
    delay(duration_ms);
    digitalWrite(VIBRATION_PIN, LOW);
}

void send_bluetooth_alert(uint8_t status, int32_t confidence) {
    // Envia alerta via Bluetooth LE
    // (código específico do nRF52)
}

// Definições de pinos
#define ECG_PIN A0
#define LED_GREEN 2
#define LED_RED 3
#define VIBRATION_PIN 4
