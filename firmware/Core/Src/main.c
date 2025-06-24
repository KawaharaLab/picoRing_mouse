	/* LP Mode */

/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2025 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "usart.h"
#include "spi.h"
#include "gpio.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */

/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */
#define CS_Pin GPIO_PIN_9
#define CS_GPIO_Port GPIOA
#define WAIT_TIME 7000
/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/

/* USER CODE BEGIN PV */
volatile uint8_t interrupt_flag = 0;
uint32_t last_change_time = 0;
uint32_t current_time = 0;
/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
/* USER CODE BEGIN PFP */
void MAX5394_SetResistance(uint8_t resistance)
{
    uint8_t tx_buffer[] = { 0x00, 0x1d, 0x3a, 0x59, 0x77, 0x94, 0xb3, 0xcf, 0xea, 0xff};
    uint16_t data2 = (uint16_t)tx_buffer[resistance]; //
    data2 = data2 & 0x00FF; //

    HAL_GPIO_WritePin(CS_GPIO_Port, CS_Pin, GPIO_PIN_RESET);

	//uint8_t data2 = tx_buffer[resistance];
    HAL_SPI_Transmit(&hspi1, (uint8_t *)&data2, 1, 10);
	//HAL_SPI_Transmit(&hspi1, &data2, sizeof(data2), 10);

	HAL_GPIO_WritePin(CS_GPIO_Port, CS_Pin, GPIO_PIN_SET);
}
void MAX5394_Shutdown(void)
{
    uint16_t SD_H_WREG = 0x9000;
    uint16_t QP_OFF = 0xA000;


    HAL_GPIO_WritePin(CS_GPIO_Port, CS_Pin, GPIO_PIN_RESET);
    HAL_SPI_Transmit(&hspi1, (uint8_t *)&SD_H_WREG, sizeof(SD_H_WREG), HAL_MAX_DELAY);
    HAL_GPIO_WritePin(CS_GPIO_Port, CS_Pin, GPIO_PIN_SET);

    HAL_GPIO_WritePin(CS_GPIO_Port, CS_Pin, GPIO_PIN_RESET);
    HAL_SPI_Transmit(&hspi1, (uint8_t *)&QP_OFF, sizeof(QP_OFF), HAL_MAX_DELAY);
    HAL_GPIO_WritePin(CS_GPIO_Port, CS_Pin, GPIO_PIN_SET);
}

void MAX5394_Reset(void)
{
    uint16_t reset_sequence = 0xC000; //


    HAL_GPIO_WritePin(CS_GPIO_Port, CS_Pin, GPIO_PIN_RESET);
    HAL_SPI_Transmit(&hspi1, (uint8_t *)&reset_sequence, sizeof(reset_sequence), HAL_MAX_DELAY);
    HAL_GPIO_WritePin(CS_GPIO_Port, CS_Pin, GPIO_PIN_SET);
}

void Enter_STOP_Mode(void)
{
    HAL_PWR_EnterSTOPMode(PWR_LOWPOWERREGULATOR_ON, PWR_STOPENTRY_WFI);
}

//void EXTI4_15_IRQHandler(void)
//{
//	HAL_GPIO_EXTI_IRQHandler(GPIO_PIN_14);
//
//}

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{
  /* USER CODE BEGIN 1 */

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  //MX_LPUART1_UART_Init();
  MX_SPI1_Init();

  /* USER CODE BEGIN 2 */
  //__HAL_RCC_PWR_CLK_ENABLE();


  uint8_t counter = 3;

  uint8_t left_counter = 0;
  uint8_t right_counter = 0;
  uint8_t up_counter = 0;
  uint8_t down_counter = 0;
  uint8_t zero_counter = 0;
  uint8_t is_button_pressed = 0;
  uint8_t step = 0;

  GPIO_PinState left_state_prev = GPIO_PIN_RESET;
  GPIO_PinState right_state_prev = GPIO_PIN_RESET;
  GPIO_PinState up_state_prev = GPIO_PIN_RESET;
  GPIO_PinState down_state_prev = GPIO_PIN_RESET;

  HAL_Delay(2000);
  MAX5394_Shutdown();
  HAL_Delay(2000);
  //HAL_SuspendTick();
  //HAL_PWR_EnterSTOPMode(PWR_LOWPOWERREGULATOR_ON, PWR_STOPENTRY_WFI);
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
    /* USER CODE END WHILE */
	  if (interrupt_flag == 1) {
		  MAX5394_Reset();
		  MAX5394_SetResistance(9);
		  HAL_Delay(200);
		  MAX5394_SetResistance(0);
		  interrupt_flag = 2;
	  }
	  if (interrupt_flag == 2) {
		  //MAX5394_Reset();
		  //MAX5394_SetResistance();

	      current_time = HAL_GetTick();
		  GPIO_PinState left_state_now = HAL_GPIO_ReadPin(GPIOB,GPIO_PIN_7);
		  GPIO_PinState right_state_now = HAL_GPIO_ReadPin(GPIOB,GPIO_PIN_6);;
		  GPIO_PinState up_state_now = HAL_GPIO_ReadPin(GPIOB,GPIO_PIN_1);
		  GPIO_PinState down_state_now = HAL_GPIO_ReadPin(GPIOC,GPIO_PIN_15);
//		  GPIO_PinState button_state_now = HAL_GPIO_ReadPin(GPIOC,GPIO_PIN_14);

	      if (up_state_now == up_state_prev &&
	          down_state_now == down_state_prev &&
	          left_state_now == left_state_prev &&
              right_state_now == right_state_prev) {
	    	  if (current_time - last_change_time >= WAIT_TIME) {
	    		  interrupt_flag = 0;
	    		  MAX5394_Shutdown();
	              HAL_PWR_EnterSTOPMode(PWR_LOWPOWERREGULATOR_ON, PWR_STOPENTRY_WFI);
	    	  }
	       } else {
	        	  // update scroll & button state
	        	  if (left_state_now != left_state_prev){
	        		  left_counter++;
	        	  } else if (right_state_now != right_state_prev){
	        		  right_counter++;
	        	  } else if (up_state_now != up_state_prev){
	        		  up_counter++;
	        	  } else if (down_state_now != down_state_prev){
	        		  down_counter++;
//	        	  } else if (button_state_now == GPIO_PIN_RESET) {
//	        		  is_button_pressed = 1;
	        	  } else {
	        			zero_counter++;
	        	  }

	        	  // Clear all counters if any wrong direction is triggered
	        	  if (left_counter > 0 && (right_counter > 0 || up_counter > 0 || down_counter > 0)) {
	        		  left_counter = right_counter = up_counter = down_counter = 0;
	        	  } else if (right_counter > 0 && (left_counter > 0 || up_counter > 0 || down_counter > 0)) {
	        		  left_counter = right_counter = up_counter = down_counter = 0;
	        	  } else if (up_counter > 0 && (left_counter > 0 || right_counter > 0 || down_counter > 0)) {
	        		  left_counter = right_counter = up_counter = down_counter = 0;
	        	  } else if (down_counter > 0 && (left_counter > 0 || right_counter > 0 || up_counter > 0)) {
	        		  left_counter = right_counter = up_counter = down_counter = 0;
	        	  }

	        	  if (left_counter >= counter) {
	        		  step = 2;
	        		  left_counter = right_counter = up_counter = down_counter = 0;
	        	  } else if (right_counter >= counter) {
	        		  step = 4;
	        		  left_counter = right_counter = up_counter = down_counter = 0;
	        	  } else if (up_counter >= counter) {
	        		  step = 6;
	        		  left_counter = right_counter = up_counter = down_counter = 0;
	        	  } else if (down_counter >= counter) {
	        		  step = 8;
	        		  left_counter = right_counter = up_counter = down_counter = 0;
	        	  } else if (zero_counter >= 20){
	        		  step = 0;
	        		  left_counter = right_counter = up_counter = down_counter = 0;
	        	  } else if (is_button_pressed) {
	        		  step = 9;
	        		  is_button_pressed = 0;
	        		  left_counter = right_counter = up_counter = down_counter = 0;
	        	  }

	        	  MAX5394_SetResistance(step);
	        	  //HAL_Delay(200);
	        	  MAX5394_SetResistance(0);
	        	  // Update previous states
	        	  left_state_prev = left_state_now;
	        	  right_state_prev = right_state_now;
	        	  up_state_prev = up_state_now;
	        	  down_state_prev = down_state_now;
	              last_change_time = current_time;
	              HAL_Delay(10);
	          }
	  } else {
	      HAL_PWR_EnterSTOPMode(PWR_LOWPOWERREGULATOR_ON, PWR_STOPENTRY_WFI);
	  }
    /* USER CODE BEGIN 3 */
  }
  /* USER CODE END 3 */
}

void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};
  RCC_PeriphCLKInitTypeDef PeriphClkInit = {0};

  /** Configure the main internal regulator output voltage
  */
  __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE1);

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_MSI;
  RCC_OscInitStruct.MSIState = RCC_MSI_ON;
  RCC_OscInitStruct.MSICalibrationValue = 0;
  RCC_OscInitStruct.MSIClockRange = RCC_MSIRANGE_3;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_NONE;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_MSI;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV1;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_0) != HAL_OK)
  {
    Error_Handler();
  }
  PeriphClkInit.PeriphClockSelection = RCC_PERIPHCLK_LPUART1;
  PeriphClkInit.Lpuart1ClockSelection = RCC_LPUART1CLKSOURCE_SYSCLK;
  if (HAL_RCCEx_PeriphCLKConfig(&PeriphClkInit) != HAL_OK)
  {
    Error_Handler();
  }
}

/* USER CODE BEGIN 4 */
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin)
{
// 确认是否是pin 14的中断
  if (GPIO_Pin == GPIO_PIN_14)
  //if (__HAL_GPIO_EXTI_GET_IT(GPIO_PIN_14) != RESET)
  {
	 //HAL_ResumeTick();
	 interrupt_flag = 1;
	 //MAX5394_Reset();
	 //MAX5394_SetResistance(9);
	 //SystemClock_Config();
     // 执行MAX5394_SetResistance函数5秒
//        for(int i = 0; i < 5; i++)
//        {
//        	AD5160_SetResistance(9); // 根据需要调整函数参数
//            HAL_Delay(500); // 延时0.5秒
//            AD5160_SetResistance(2);
//            HAL_Delay(500); // 延时0.5秒
//        }
	 //MAX5394_SetResistance(9); // 根据需要调整函数参数
//	 MAX5394_Reset();
//	 MAX5394_SetResistance(4);
//	 MAX5394_Shutdown();
     //HAL_Delay(5000); //
     //MAX5394_SetResistance(2);
     //HAL_Delay(2000); //
     //MAX5394_SetResistance(0);
     //__HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_14);
     //HAL_PWR_EnterSTOPMode(PWR_LOWPOWERREGULATOR_ON, PWR_STOPENTRY_WFI);
     // 可以在这里再次配置MCU进入STOP模式，或者返回主循环自动进入
  }
}
/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */

