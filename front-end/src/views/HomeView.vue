<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<template lang="pug">
  h1 mEmo
  nav
    RouterLink(to="/login") Login
    | &nbsp;
    RouterLink(to="/protected") Protected
    | &nbsp;
    RouterLink(to="/gibberish") Invalid Page
</template>
