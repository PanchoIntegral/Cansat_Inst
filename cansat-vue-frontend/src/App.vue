<template>
  <div id="app">
    <CanSatDisplay />
  </div>
</template>

<script>
import CanSatDisplay from './components/CanSatDisplay.vue';

export default {
  name: 'App',
  components: {
    CanSatDisplay,
  },
};
</script>

<style>
/* Estilos globales si los necesitas */
body {
  margin: 0;
  background-color: #e9ecef; /* Un fondo general para la página */
}
#app {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
</style>