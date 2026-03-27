/**
 * Aureum Tiny - ESP32 Camera Example
 * Detecção de pessoas em câmera de segurança de $5
 * 
 * Hardware: ESP32-CAM ($5)
 * - 4 MB Flash
 * - 520 KB RAM
 * - Câmera OV2640
 * 
 * Author: Luiz Antônio De Lima Mendonça
 * Date: 2026-03-26
 */

#include "aureum_tiny.h"

// Modelo treinado para detecção de pessoas (50 KB na Flash)
// Entrada: 96x96 grayscale = 9216 pixels
// Saída: 2 classes (pessoa / não-pessoa)
AUREUM_MODEL_FLASH uint8_t person_model[2304] = {
    // Pesos ternários compactados
    // 9216 pesos * 2 classes = 18432 pesos
    // 18432 / 4 = 4608 bytes, mas usando Matryoshka 50% = 2304 bytes
    0x89, 0x12, 0x45, 0xA3, // ... (modelo pré-treinado)
    // Em produção, carregar de arquivo ou gerar via Python
};

// Buffer de imagem
int16_t image_buffer[96 * 96];

void setup() {
    Serial.begin(115200);
    
    // Inicializa Aureum Tiny
    aureum_tiny_init();
    Serial.println("Aureum Tiny inicializado!");
    
    // Inicializa câmera
    init_camera();
    Serial.println("Câmera pronta!");
}

void loop() {
    // Captura frame da câmera (96x96 grayscale)
    capture_frame(image_buffer, 96, 96);
    
    // Classifica: pessoa ou não-pessoa
    AureumClassifyResult result;
    aureum_tiny_classify_c(
        image_buffer,
        96 * 96,
        person_model,
        sizeof(person_model),
        2,        // 2 classes
        96 * 48   // Matryoshka 50% (economia de energia)
    , &result);
    
    // Ação baseada no resultado
    if (result.class_id == 0) {
        Serial.println("PESSOA DETECTADA!");
        Serial.print("Confiança: ");
        Serial.println(result.score);
        
        // Envia alerta
        send_notification();
        
        // Acende LED
        digitalWrite(LED_PIN, HIGH);
        delay(1000);
        digitalWrite(LED_PIN, LOW);
    } else {
        Serial.println("Nenhuma pessoa detectada");
    }
    
    // Aguarda 100ms
    delay(100);
}

// ─── Funções auxiliares ──────────────────────────────────────────────────────

void init_camera() {
    // Configuração da câmera OV2640
    // (código específico do ESP32-CAM)
}

void capture_frame(int16_t* buffer, int width, int height) {
    // Captura frame e converte para int16 centrado em zero
    // (código específico do ESP32-CAM)
    
    // Exemplo simplificado:
    // uint8_t* frame = camera_get_frame();
    // for(int i = 0; i < width * height; i++) {
    //     buffer[i] = (int16_t)frame[i] - 128;
    // }
}

void send_notification() {
    // Envia notificação via WiFi
    // (código específico do projeto)
}
