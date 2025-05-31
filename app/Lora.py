
import board # Necesitas la biblioteca Adafruit-Blinka
import busio
import digitalio
import adafruit_rfm9x # Biblioteca para el módulo LoRa RFM9x
import time
import json
import os

# --- Configuración del Módulo LoRa (¡AJUSTA ESTO A TU HARDWARE!) ---
CS_PIN = board.CE1    # Pin Chip Select de SPI. Puede ser CE0 o CE1 (D8 o D7 en Blinka)
RESET_PIN = board.D25 # Pin que estés usando para el RESET del módulo LoRa
# SPI PINS (normalmente estos son fijos para el SPI0 de la Raspberry Pi)
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

# Configura los pines CS y RESET como salidas digitales
CS = digitalio.DigitalInOut(CS_PIN)
RESET = digitalio.DigitalInOut(RESET_PIN)

# Frecuencia de Radio (¡ASEGÚRATE QUE COINCIDA CON TU CANSAT!)
# Ejemplos: 433.0, 868.0, 915.0 MHz
RADIO_FREQ_MHZ = 915.0


DATA_FILE_PATH = "/tmp/cansat_latest_data.json"

print("Inicializando Gateway LoRa...")

try:
    # Inicializa el módulo RFM9x
    rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)

    # Opcional: Configura la potencia de transmisión si es necesario (aunque aquí es gateway)
    # rfm9x.tx_power = 23 # Máxima potencia para algunos módulos

    # Opcional: Configurar parámetros como spreading factor, bandwidth, coding rate si es necesario
    # rfm9x.spreading_factor = 7 # Ejemplo
    # rfm9x.signal_bandwidth = 125000 # Ejemplo: 125kHz
    # rfm9x.coding_rate = 5 # Ejemplo: 4/5

    print(f"Gateway LoRa escuchando en {RADIO_FREQ_MHZ} MHz...")
    print(f"Los datos recibidos se guardarán en: {DATA_FILE_PATH}")

except Exception as e:
    print(f"Error al inicializar el módulo LoRa: {e}")
    print("Asegúrate de haber instalado las bibliotecas Adafruit-Blinka y adafruit-circuitpython-rfm9x,")
    print("y de que la configuración de SPI y los pines CS/RESET sean correctos.")
    exit()


try:
    while True:
        # Espera a recibir un paquete. El timeout es opcional pero recomendado.
        # Un timeout más largo consume menos CPU si no hay paquetes frecuentes.
        packet = rfm9x.receive(timeout=10.0)  # Espera un paquete por hasta 10 segundos

        if packet is None:
            # No se recibió nada durante el timeout
            # print("Esperando paquete...") # Descomenta para ver actividad
            pass
        else:
            # Paquete recibido
            rssi = rfm9x.last_rssi  # Radio Signal Strength Indicator
            snr = rfm9x.last_snr    # Signal to Noise Ratio (disponible en algunos módulos/bibliotecas)

            print(f"¡Paquete Recibido! RSSI: {rssi} dB, SNR: {snr} dB")

            try:
                # Intenta decodificar el paquete como texto ASCII
                # Tu CanSat debe enviar los datos en un formato que puedas parsear.
                # Ej: "temp:25.5,pres:1012,alt:120.3" o un JSON como '{"temp":25.5, "pres":1012, "alt":120.3}'
                payload_text = str(packet, "ascii")
                print(f"Payload (texto): {payload_text}")
            except UnicodeDecodeError:
                payload_text = "Error: No se pudo decodificar el payload a ASCII."
                print(f"Payload (bytes): {packet}") # Muestra los bytes crudos si no es ASCII
            except Exception as e:
                payload_text = f"Error al procesar payload: {e}"
                print(f"Payload (bytes): {packet}")

            # Prepara los datos para guardar en formato JSON
            latest_data = {
                "payload": payload_text,
                "rssi": rssi,
                "snr": snr,
                "timestamp_gw": time.strftime("%Y-%m-%d %H:%M:%S %Z"), # Timestamp del gateway
                "raw_packet": packet.hex() if packet else None # Opcional: paquete crudo en hexadecimal
            }

            # Guarda los datos en el archivo JSON
            try:
                with open(DATA_FILE_PATH, "w") as f:
                    json.dump(latest_data, f, indent=4)
                print(f"Datos guardados en {DATA_FILE_PATH}")
            except Exception as e:
                print(f"ERROR al escribir datos en archivo: {e}")

except KeyboardInterrupt:
    print("\nCerrando receptor LoRa por interrupción del teclado.")
except Exception as e:
    print(f"ERROR crítico en el bucle principal del receptor LoRa: {e}")
finally:
    # Opcional: acciones de limpieza si fueran necesarias
    print("Receptor LoRa detenido.")