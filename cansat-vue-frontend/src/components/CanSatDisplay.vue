<template>
  <div class="cansat-display">
    <h1>🛰️ Datos del CanSat (Vue.js)</h1>
    <div v-if="error" class="error">{{ error }}</div>
    <div v-if="loading" class="loading">Cargando datos...</div>
    <div v-if="!loading && !error && cansatData" class="data-grid">
      <div class="data-item">
        <span class="data-label">Payload Crudo:</span>
        <span class="data-value code">{{ cansatData.payload }}</span>
      </div>
      <div class="data-item">
        <span class="data-label">RSSI:</span>
        <span class="data-value">{{ cansatData.rssi }} dBm</span>
      </div>
      <div class="data-item">
        <span class="data-label">SNR:</span>
        <span class="data-value">{{ cansatData.snr }} dB</span>
      </div>
      <div class="data-item">
        <span class="data-label">Timestamp (Gateway):</span>
        <span class="data-value">{{ cansatData.timestamp }}</span>
      </div>
      <div class="data-item">
        <span class="data-label">Última Actualización (Frontend):</span>
        <span class="data-value">{{ lastFrontendUpdate }}</span>
      </div>
    </div>
    <button @click="fetchData" :disabled="loading">Actualizar Datos</button>
  </div>
</template>

<script>
import axios from 'axios';

// La URL de tu API Flask. Durante el desarrollo en tu PC,
// será la IP de la Pi. Para producción, si Flask sirve Vue, podría ser relativo.
// Si Flask y Vue dev server corren en la misma máquina (tu PC) pero puertos diferentes:
// const API_URL = 'http://localhost:5000/api/cansat_data';
// Si Flask está en la Pi y Vue dev server en tu PC:
const API_URL = 'http://<DIRECCION_IP_DE_TU_RASPBERRY>:5000/api/cansat_data';


export default {
  name: 'CanSatDisplay',
  data() {
    return {
      cansatData: null,
      loading: false,
      error: null,
      lastFrontendUpdate: null,
      pollingInterval: null,
    };
  },
  methods: {
    async fetchData() {
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.get(API_URL);
        this.cansatData = response.data;
        this.lastFrontendUpdate = new Date().toLocaleTimeString();
      } catch (err) {
        console.error("Error fetching CanSat data:", err);
        this.error = "No se pudieron cargar los datos. Verifica que el backend Flask y el script LoRa estén funcionando.";
        if (err.response) {
             this.error += ` (Status: ${err.response.status})`;
        } else if (err.request) {
            this.error += " (El servidor no respondió)";
        }
      } finally {
        this.loading = false;
      }
    },
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
  font-family: sans-serif;
  max-width: 600px;
  margin: 20px auto;
  padding: 20px;
  background-color: #f9f9f9;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
h1 {
  color: #0056b3;
  text-align: center;
  margin-bottom: 20px;
}
.data-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 10px;
  margin-bottom: 20px;
}
.data-item {
  background-color: #fff;
  padding: 10px;
  border: 1px solid #eee;
  border-radius: 4px;
}
.data-label {
  font-weight: bold;
  color: #333;
  display: block;
  margin-bottom: 5px;
}
.data-value {
  color: #555;
}
.data-value.code {
  font-family: monospace;
  background-color: #e8e8e8;
  padding: 2px 5px;
  border-radius: 3px;
  display: inline-block;
  word-break: break-all;
}
.error {
  color: red;
  padding: 10px;
  border: 1px solid red;
  background-color: #ffe0e0;
  border-radius: 4px;
  margin-bottom: 15px;
}
.loading {
  text-align: center;
  padding: 15px;
  color: #0056b3;
}
button {
  display: block;
  width: 100%;
  padding: 10px 15px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1em;
}
button:disabled {
  background-color: #ccc;
}
button:hover:not(:disabled) {
  background-color: #0056b3;
}
</style>