<template>
  <div class="cansat-display">
    <div class="mission-header">
      <h1>
        <span class="mission-icon">🛰️</span>
        CANSAT MISSION CONTROL
        <div class="mission-status" :class="{ 'status-active': !error }">
          {{ error ? 'OFFLINE' : 'ACTIVE' }}
        </div>
      </h1>
    </div>
    
    <div v-if="error" class="error">
      <span class="error-icon">⚠️</span>
      {{ error }}
    </div>
    
    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      ESTABLISHING COMMUNICATION LINK...
    </div>
    
    <div v-if="!loading && !error && cansatData" class="data-container">
      <div class="mission-time">
        MISSION TIME: {{ getMissionTime() }}
      </div>
      
      <div class="data-grid">
        <div class="data-item telemetry">
          <span class="data-label">PAYLOAD DATA</span>
          <span class="data-value code">{{ cansatData.payload }}</span>
        </div>
        
        <div class="data-item signal">
          <span class="data-label">SIGNAL STRENGTH (RSSI)</span>
          <div class="signal-meter">
            <div class="signal-bar" :style="{ width: getRSSIPercentage() + '%' }"></div>
          </div>
          <span class="data-value">{{ cansatData.rssi }} dBm</span>
        </div>
        
        <div class="data-item quality">
          <span class="data-label">SIGNAL QUALITY (SNR)</span>
          <div class="quality-indicator" :class="getSNRClass()">
            <span class="data-value">{{ cansatData.snr }} dB</span>
          </div>
        </div>
        
        <div class="data-item timestamp">
          <span class="data-label">GATEWAY TIMESTAMP</span>
          <span class="data-value">{{ formatTimestamp(cansatData.timestamp) }}</span>
        </div>
        
        <div class="data-item update">
          <span class="data-label">LAST TELEMETRY UPDATE</span>
          <span class="data-value">{{ formatTimestamp(lastFrontendUpdate) }}</span>
        </div>
      </div>
      
      <button @click="fetchData" :disabled="loading">
        <span class="button-icon">📡</span>
        REQUEST TELEMETRY UPDATE
      </button>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
// La URL de tu API Flask. Durante el desarrollo en tu PC,
// será la IP de la Pi. Para producción, si Flask sirve Vue, podría ser relativo.
// Si Flask y Vue dev server corren en la misma máquina (tu PC) pero puertos diferentes:
// const API_URL = 'http://localhost:5000/api/cansat_data';
// Si Flask está en la Pi y Vue dev server en tu PC:
const API_URL = 'http://192.168.1.132/api/cansat_data';


export default {
  name: 'CanSatDisplay',
  data() {
    return {
      cansatData: null,
      loading: false,
      error: null,
      lastFrontendUpdate: null,
      pollingInterval: null,
      missionStartTime: new Date(),
    };
  },
  methods: {
    async fetchData() {
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.get(API_URL);
        this.cansatData = response.data;
        this.lastFrontendUpdate = new Date().toLocaleString();
      } catch (err) {
        console.error("Error fetching CanSat data:", err);
        this.error = "ERROR DE COMUNICACIÓN: Verificar estado del sistema de telemetría.";
        if (err.response) {
             this.error += ` (CÓDIGO: ${err.response.status})`;
        } else if (err.request) {
            this.error += " (SIN RESPUESTA DEL SERVIDOR)";
        }
      } finally {
        this.loading = false;
      }
    },
    getMissionTime() {
      const now = new Date();
      const diff = now - this.missionStartTime;
      const hours = Math.floor(diff / 3600000);
      const minutes = Math.floor((diff % 3600000) / 60000);
      const seconds = Math.floor((diff % 60000) / 1000);
      return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    },
    getRSSIPercentage() {
      if (!this.cansatData) return 0;
      // Convert RSSI to percentage (typical RSSI range: -120 to -30 dBm)
      const rssi = this.cansatData.rssi;
      const minRSSI = -120;
      const maxRSSI = -30;
      const percentage = ((rssi - minRSSI) / (maxRSSI - minRSSI)) * 100;
      return Math.min(Math.max(percentage, 0), 100);
    },
    getSNRClass() {
      if (!this.cansatData) return 'quality-poor';
      const snr = this.cansatData.snr;
      if (snr > 10) return 'quality-excellent';
      if (snr > 5) return 'quality-good';
      if (snr > 0) return 'quality-fair';
      return 'quality-poor';
    },
    formatTimestamp(timestamp) {
      if (!timestamp) return 'NO DATA';
      return timestamp.replace(' ', ' | ');
    }
  },
  mounted() {
    this.fetchData(); // Cargar datos al montar el componente
    // Actualizar datos cada 10 segundos
    this.pollingInterval = setInterval(this.fetchData, 10000);
  },
  beforeUnmount() {
    // Limpiar el intervalo cuando el componente se destruya
    clearInterval(this.pollingInterval);
  }
};
</script>

<style scoped>
.cansat-display {
  font-family: 'Space Mono', 'Roboto Mono', monospace;
  max-width: 800px;
  margin: 20px auto;
  padding: 25px;
  background-color: #1a1d21;
  border: 2px solid #30363d;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.2);
  color: #e6edf3;
  position: relative;
  overflow: hidden;
}

.cansat-display::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(90deg, #00ff9d, #00b8ff, #7000ff);
  animation: rainbow 5s linear infinite;
}

@keyframes rainbow {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

h1 {
  color: #00b8ff;
  text-align: center;
  margin-bottom: 30px;
  font-size: 2em;
  text-transform: uppercase;
  letter-spacing: 2px;
  text-shadow: 0 0 10px rgba(0,184,255,0.3);
}

.mission-header {
  margin-bottom: 30px;
  position: relative;
}

.mission-icon {
  font-size: 1.5em;
  margin-right: 10px;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.mission-status {
  font-size: 0.4em;
  padding: 5px 10px;
  border-radius: 20px;
  background: #2d333b;
  display: inline-block;
  margin-top: 10px;
}

.status-active {
  background: linear-gradient(45deg, #00ff9d, #00b8ff);
  color: #1a1d21;
  animation: pulse 2s infinite;
}

.mission-time {
  text-align: center;
  font-size: 1.2em;
  color: #00ff9d;
  margin-bottom: 20px;
  font-family: 'Fira Code', monospace;
  letter-spacing: 2px;
}

.data-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 25px;
}

.data-item {
  background-color: #22272e;
  padding: 15px;
  border: 1px solid #383f47;
  border-radius: 8px;
  position: relative;
  transition: all 0.3s ease;
}

.data-item::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 4px;
  height: 100%;
  background: #00b8ff;
  border-radius: 0 8px 8px 0;
  opacity: 0.7;
}

.data-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,184,255,0.1);
}

.data-label {
  font-weight: bold;
  color: #00ff9d;
  display: block;
  margin-bottom: 8px;
  font-size: 0.9em;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.data-value {
  color: #e6edf3;
  font-size: 1.1em;
}

.data-value.code {
  font-family: 'Fira Code', monospace;
  background-color: #2d333b;
  padding: 8px 12px;
  border-radius: 6px;
  display: inline-block;
  word-break: break-all;
  border: 1px solid #444c56;
}

.error {
  color: #ff4646;
  padding: 15px;
  border: 1px solid #ff4646;
  background-color: rgba(255,70,70,0.1);
  border-radius: 8px;
  margin-bottom: 20px;
  font-family: 'Fira Code', monospace;
}

.error-icon {
  margin-right: 10px;
  font-size: 1.2em;
}

.loading {
  text-align: center;
  padding: 20px;
  color: #00b8ff;
  font-size: 1.2em;
  animation: pulse 1.5s infinite;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  margin: 0 auto 15px;
  border: 4px solid #2d333b;
  border-top: 4px solid #00b8ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

button {
  display: block;
  width: 100%;
  padding: 15px;
  background: linear-gradient(45deg, #00b8ff, #7000ff);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1.1em;
  font-family: 'Space Mono', monospace;
  text-transform: uppercase;
  letter-spacing: 2px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
  transition: 0.5s;
}

button:hover::before {
  left: 100%;
}

button:disabled {
  background: #2d333b;
  cursor: not-allowed;
}

button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0,184,255,0.3);
}

.signal-meter {
  height: 8px;
  background: #2d333b;
  border-radius: 4px;
  margin: 10px 0;
  overflow: hidden;
}

.signal-bar {
  height: 100%;
  background: linear-gradient(90deg, #ff4646 0%, #ffb946 50%, #00ff9d 100%);
  transition: width 0.3s ease;
}

.quality-indicator {
  padding: 8px;
  border-radius: 6px;
  text-align: center;
  margin-top: 10px;
  transition: all 0.3s ease;
}

.quality-excellent {
  background: rgba(0, 255, 157, 0.2);
  border: 1px solid #00ff9d;
}

.quality-good {
  background: rgba(0, 184, 255, 0.2);
  border: 1px solid #00b8ff;
}

.quality-fair {
  background: rgba(255, 185, 70, 0.2);
  border: 1px solid #ffb946;
}

.quality-poor {
  background: rgba(255, 70, 70, 0.2);
  border: 1px solid #ff4646;
}

.data-container {
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.telemetry {
  grid-column: span 2;
}

@media (max-width: 768px) {
  .data-grid {
    grid-template-columns: 1fr;
  }
  
  .telemetry {
    grid-column: span 1;
  }
  
  .cansat-display {
    margin: 10px;
    padding: 15px;
  }
}
</style>