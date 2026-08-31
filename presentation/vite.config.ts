import { defineConfig } from 'vite'

// The project lives on a WSL /mnt/c drvfs mount, which emits no inotify events.
// Without polling, edits never reach the browser and HMR silently serves stale modules.
export default defineConfig({
  server: {
    watch: {
      usePolling: true,
      interval: 300,
    },
  },
})
