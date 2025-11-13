import { defineStore } from 'pinia'

export const useMessageStore = defineStore('message', {
  state: () => ({
    errorMessages: null
  }),
  
  actions: {
    updateErrorMessages(message) {
      this.errorMessages = message
      setTimeout(() => {
        this.errorMessages = null
      }, 5000)
    }
  }
})