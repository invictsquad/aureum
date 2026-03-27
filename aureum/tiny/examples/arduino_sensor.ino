/**
 * Aureum Tiny - Arduino Sensor Example
 * Detecção de pragas em agricultura de precisão
 * 
 * Hardware: Arduino Nano ($2)
 * - 32 KB Flash
 * - 2 KB RAM
 * - Sensores analógicos
 * 
 * Author: Luiz Antônio De Lima Mendonça
 * Date: 2026-03-26
 */

#include "aureum_tiny.h"

// Modelo treinado para detecção de pragas (2 KB na Flash)
// Entrada: 16 sensores
// Saída: 3 classes (sem praga / praga leve / praga grave)
AUREUM_MODEL_FLASH uint8_t pest_model[12] = {
    // 16 sensores * 3 classes = 48 pesos
    // 48 / 4 = 12 bytes
    0x89, 0x12, 0x45, 0xA3, 0x67, 0x8A, 0xBC, 0xDE,
    0xF0, 0x12, 0x34, 0x56
    // Em produção, carregar modelo real
};

// Pinos dos sensores
const int SENSOR_PINS[] = {
    A0, A1, A2, A3, A4, A5, A6, A7,
    2, 3, 4, 5, 6, 7, 8, 9
};

// Buffer de leitura
int16_t sensor_readings[16];

void setup() {
    Serial.begin(9600);
    
    // Inicializa Aureum Tiny
    aureum_tiny_init();
    Serial.println("Aureum Tiny inicializado!");
    
    // Configura pinos
    for(int i = 0; i < 16; i++) {
        pinMode(SENSOR_PINS[i], INPUT);
    }
    
    // Configura atuadores
    pinMode(IRRIGATION_PIN, OUTPUT);
    pinMode(ALERT_PIN, OUTPUT);
    
    Serial.println("Sistema pronto!");
}

void loop() {
    // Lê todos os sensores
    read_sensors();
    
    // Classifica: sem praga / praga leve / praga grave
    AureumClassifyResult result;
    aureum_tiny_classify_c(
        sensor_readings,
        16,
        pest_model,
        sizeof(pest_model),
        3,   // 3 classes
        16,  // Escala completa
        &result
    );
    
    // Ação baseada no resultado
    switch(result.class_id) {
        case 0:
            Serial.println("Status: Normal");
            digitalWrite(ALERT_PIN, LOW);
            break;
            
        case 1:
            Serial.println("ALERTA: Praga leve detectada");
            Serial.print("Confiança: ");
            Serial.println(result.score);
            
            // Ativa irrigação preventiva
            activate_irrigation(5000); // 5 segundos
            digitalWrite(ALERT_PIN, HIGH);
            break;
            
        case 2:
            Serial.println("CRÍTICO: Praga grave detectada!");
            Serial.print("Confiança: ");
            Serial.println(result.score);
            
            // Ativa irrigação intensiva
            activate_irrigation(15000); // 15 segundos
            digitalWrite(ALERT_PIN, HIGH);
            
            // Envia alerta
            send_alert();
            break;
    }
    
    // Aguarda 1 minuto
    delay(60000);
}

// ─── Funções auxiliares ──────────────────────────────────────────────────────

void read_sensors() {
    for(int i = 0; i < 16; i++) {
        // Lê sensor e normaliza para int16
        int raw = analogRead(SENSOR_PINS[i]);
        sensor_readings[i] = (int16_t)(raw - 512);
    }
}

void activate_irrigation(unsigned long duration_ms) {
    digitalWrite(IRRIGATION_PIN, HIGH);
    delay(duration_ms);
    digitalWrite(IRRIGATION_PIN, LOW);
}

void send_alert() {
    // Envia alerta via LoRa, GSM, etc.
    // (código específico do projeto)
}

// Definições de pinos
#define IRRIGATION_PIN 10
#define ALERT_PIN 11
