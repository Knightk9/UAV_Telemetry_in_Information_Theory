/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.h
  * @brief          : Header for main.c file.
  ******************************************************************************
  */
/* USER CODE END Header */

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __MAIN_H
#define __MAIN_H

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "stm32f4xx_hal.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#define MAX_UNIQUE_SYMBOLS 254
#define MAX_STREAM_BYTES   128

typedef struct __attribute__((packed)) {
    uint32_t frame_id;
    uint32_t delayMax;
    uint32_t delayMin;
    float source_entropy;
    float entropy_after_source;
    float compression_ratio;
    uint8_t alphabet_size;
    int16_t symbols[MAX_UNIQUE_SYMBOLS];
    uint8_t bit_lengths[MAX_UNIQUE_SYMBOLS];
    uint16_t bit_lens[3];
    uint8_t encoded_data[3][MAX_STREAM_BYTES];
} DataPacket_t;
/* USER CODE END Includes */

/* Exported types ------------------------------------------------------------*/
/* USER CODE BEGIN ET */

/* USER CODE END ET */

/* Exported constants --------------------------------------------------------*/
/* USER CODE BEGIN EC */

/* USER CODE END EC */

/* Exported macro ------------------------------------------------------------*/
/* USER CODE BEGIN EM */

/* USER CODE END EM */

/* Exported functions prototypes ---------------------------------------------*/
void Error_Handler(void);

/* USER CODE BEGIN EFP */

/* USER CODE END EFP */

/* Private defines -----------------------------------------------------------*/

/* USER CODE BEGIN Private defines */
// LCD
#define LCD_RS_PIN GPIO_PIN_8
#define LCD_RS_GPIO_PORT GPIOA
#define LCD_E_PIN GPIO_PIN_9
#define LCD_E_GPIO_PORT GPIOA
#define LCD_D4_PIN GPIO_PIN_12
#define LCD_D4_GPIO_PORT GPIOB
#define LCD_D5_PIN GPIO_PIN_13
#define LCD_D5_GPIO_PORT GPIOB
#define LCD_D6_PIN GPIO_PIN_14
#define LCD_D6_GPIO_PORT GPIOB
#define LCD_D7_PIN GPIO_PIN_15
#define LCD_D7_GPIO_PORT GPIOB

// NRF
#define NRF_IRQ_PIN GPIO_PIN_1
#define NRF_IRQ_GPIO_PORT GPIOA
#define NRF_CE_PIN GPIO_PIN_3
#define NRF_CE_GPIO_PORT GPIOA
#define NRF_CSN_PIN GPIO_PIN_4
#define NRF_CSN_GPIO_PORT GPIOA
/* USER CODE END Private defines */

#ifdef __cplusplus
}
#endif

#endif /* __MAIN_H */
