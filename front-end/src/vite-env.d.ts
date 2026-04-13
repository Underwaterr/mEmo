/// <reference types="vite/client" />

// tell TypeScript how to interpret `.vue` files when importing them
// we define components very broadly here as a fallback
// specific component types will be defined more narrowly within the components themselves
declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  // DefineComponent<Props, Data, etc>
  // our component's props can be any object, data can be any object, and anything else for the rest
  const component: DefineComponent<{}, {}, any>
  export default component
}
