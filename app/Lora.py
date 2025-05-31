import time
import board
import busio
import digitalio
import adafruit_rfm9x
import json
import os

# Configuración de depuración
DEBUG = True
DATA_FILE_PATH = "/tmp/cansat_latest_data.json"

def log_debug(message):
    if DEBUG:
        print(f"[DEBUG] {message}")

class LoRaReceiver:
    def __init__(self):
        self.rfm9x = None
        self.setup_lora()

    def setup_lora(self):
        try:
            # Configuración de pines
            CS = digitalio.DigitalInOut(board.D25)    # GPIO 25
            RESET = digitalio.DigitalInOut(board.D24)  # GPIO 24
            
            # Inicialización de SPI
            spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
            log_debug("SPI inicializado")

            # Configuración del módulo RFM9x
            self.rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, 915.0, debug=True)
            log_debug("Módulo RFM9x inicializado correctamente")
            
            # Configuración adicional del módulo
            self.rfm9x.tx_power = 23
            log_debug(f"Potencia de transmisión configurada a {self.rfm9x.tx_power} dBm")
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
        while True:
            self.receive_data()
            time.sleep(0.1)

if __name__ == "__main__":
    receiver = LoRaReceiver()
    receiver.run()