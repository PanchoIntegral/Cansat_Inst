import time
import board
import busio
import digitalio
import adafruit_rfm9x
import json
import os
import signal
import sys

# Configuración de depuración
DEBUG = True
DATA_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cansat_latest_data.json")

def log_debug(message):
    if DEBUG:
        print(f"[DEBUG] {message}")

class LoRaReceiver:
    def __init__(self):
        self.rfm9x = None
        self.running = True
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        self.setup_lora()

    def signal_handler(self, signum, frame):
        log_debug(f"Señal recibida: {signum}")
        self.running = False
        sys.exit(0)

    def setup_lora(self):
        try:
            # Configuración de pines
            log_debug("Configurando pines GPIO...")
            CS = digitalio.DigitalInOut(board.D25)    # GPIO 25
            CS.direction = digitalio.Direction.OUTPUT
            RESET = digitalio.DigitalInOut(board.D24)  # GPIO 24
            RESET.direction = digitalio.Direction.OUTPUT
            log_debug("Pines GPIO configurados correctamente")
            
            # Inicialización de SPI
            spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
            log_debug("SPI inicializado")

            # Configuración del módulo RFM9x
            log_debug("Intentando inicializar RFM9x...")
            self.rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, 915.0)
            
            # Verificación del módulo
            version = self.rfm9x._read_u8(0x42)  # Registro de versión
            log_debug(f"Versión del chip RFM9x: 0x{version:02x}")
            
            # Configuración adicional del módulo
            self.rfm9x.tx_power = 23  # Potencia máxima de transmisión
            self.rfm9x.spreading_factor = 7  # Balance entre alcance y velocidad
            self.rfm9x.signal_bandwidth = 125000  # Ancho de banda estándar
            self.rfm9x.coding_rate = 5  # Tasa de codificación 4/5 para buena corrección de errores
            self.rfm9x.enable_crc = True  # Habilitar CRC para detección de errores
            
            log_debug(f"Configuración del módulo RFM9x:")
            log_debug(f"- Potencia TX: {self.rfm9x.tx_power} dBm")
            log_debug(f"- Factor de dispersión: {self.rfm9x.spreading_factor}")
            log_debug(f"- Ancho de banda: {self.rfm9x.signal_bandwidth} Hz")
            log_debug(f"- Tasa de codificación: 4/{self.rfm9x.coding_rate}")
            log_debug(f"- CRC habilitado: {self.rfm9x.enable_crc}")
            
            return True

        except Exception as e:
            print(f"Error al inicializar el módulo LoRa: {str(e)}")
            if 'spi' in locals():
                try:
                    spi_available = spi.try_lock()
                    print(f"Estado de SPI - Disponible: {spi_available}")
                    if spi_available:
                        spi.unlock()
                except:
                    pass
            print("Asegúrate de haber instalado las bibliotecas Adafruit-Blinka y adafruit-circuitpython-rfm9x,")
            print("y de que la configuración de SPI y los pines CS/RESET sean correctos.")
            return False

    def receive_data(self):
        if not self.rfm9x:
            return None

        try:
            packet = self.rfm9x.receive(timeout=1.0)
            if packet:
                data = {
                    "payload": bytes(packet).hex(),
                    "rssi": self.rfm9x.last_rssi,
                    "snr": self.rfm9x.last_snr,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }
                # Guardar datos en archivo
                with open(DATA_FILE_PATH, "w") as f:
                    json.dump(data, f)
                log_debug(f"Datos recibidos y guardados: {data}")
                return data
            return None
        except Exception as e:
            print(f"Error en la recepción: {str(e)}")
            return None

    def run(self):
        print("Inicializando Gateway LoRa...")
        if not self.rfm9x:
            if not self.setup_lora():
                return

        print("Gateway LoRa inicializado. Esperando datos...")
        while self.running:
            try:
                self.receive_data()
                time.sleep(0.1)
            except Exception as e:
                print(f"Error en el bucle principal: {str(e)}")
                time.sleep(1)  # Espera antes de reintentar

if __name__ == "__main__":
    receiver = LoRaReceiver()
    receiver.run()