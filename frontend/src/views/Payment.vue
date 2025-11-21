<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <div class="card shadow-lg">
          <div class="card-header bg-primary text-white">
            <h5 class="mb-0">💳 Payment</h5>
          </div>

          <div class="card-body">
            <div v-if="loading" class="text-center py-5">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>

            <div v-else-if="error" class="alert alert-danger">
              {{ error }}
            </div>

            <div v-else-if="paymentData">
              <div class="mb-4">
                <h6 class="text-muted mb-3">Payment Details</h6>
                
                <div class="row mb-2">
                  <div class="col-6"><strong>Payment ID:</strong></div>
                  <div class="col-6">#{{ paymentData.id }}</div>
                </div>

                <div class="row mb-2">
                  <div class="col-6"><strong>Amount:</strong></div>
                  <div class="col-6">
                    <span class="text-success fw-bold">₹{{ paymentData.amount }}</span>
                  </div>
                </div>

                <div class="row mb-3">
                  <div class="col-6"><strong>Status:</strong></div>
                  <div class="col-6">
                    <span v-if="paymentData.status === 'Pending'" class="badge badge-warning">
                      {{ paymentData.status }}
                    </span>
                    <span v-else-if="paymentData.status === 'Success'" class="badge badge-success">
                      {{ paymentData.status }}
                    </span>
                    <span v-else class="badge badge-danger">
                      {{ paymentData.status }}
                    </span>
                  </div>
                </div>

                <hr>

                <h6 class="text-muted mb-3">Card Details</h6>

                <div class="mb-3">
                  <label class="form-label">Card Number</label>
                  <input 
                    type="text" 
                    class="form-control"
                    placeholder="1234 5678 9012 3456"
                    v-model="cardData.cardNumber"
                    maxlength="19"
                    @input="formatCardNumber"
                  >
                </div>

                <div class="row">
                  <div class="col-md-6 mb-3">
                    <label class="form-label">Expiry Date</label>
                    <input 
                      type="text" 
                      class="form-control"
                      placeholder="MM/YY"
                      v-model="cardData.expiry"
                      maxlength="5"
                      @input="formatExpiry"
                    >
                  </div>

                  <div class="col-md-6 mb-3">
                    <label class="form-label">CVV</label>
                    <input 
                      type="password" 
                      class="form-control"
                      placeholder="123"
                      v-model="cardData.cvv"
                      maxlength="3"
                    >
                  </div>
                </div>

                <div class="mb-3">
                  <label class="form-label">Cardholder Name</label>
                  <input 
                    type="text" 
                    class="form-control"
                    placeholder="Name on card"
                    v-model="cardData.cardholderName"
                  >
                </div>

                <div class="form-check mb-3">
                  <input 
                    class="form-check-input" 
                    type="checkbox" 
                    id="agreePayment"
                    v-model="agreeToPayment"
                  >
                  <label class="form-check-label" for="agreePayment">
                    I authorize this payment of ₹{{ paymentData.amount }}
                  </label>
                </div>

                <button 
                  @click="processPayment" 
                  class="btn btn-success w-100 py-2 fw-bold"
                  :disabled="processing || !agreeToPayment"
                >
                  <span v-if="!processing">Pay ₹{{ paymentData.amount }}</span>
                  <span v-else>
                    <span class="spinner-border spinner-border-sm me-2" role="status"></span>
                    Processing...
                  </span>
                </button>

                <p class="text-muted text-center mt-3 small">
                  This is a demo payment gateway
                </p>
              </div>

              <div v-if="paymentSuccess" class="alert alert-success mt-3">
                ✓ Payment successful! Redirecting...
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { paymentAPI } from '../services/api'

const route = useRoute()
const router = useRouter()

const paymentId = route.params.paymentId
const loading = ref(true)
const error = ref('')
const paymentData = ref(null)
const processing = ref(false)
const paymentSuccess = ref(false)
const agreeToPayment = ref(false)

const cardData = ref({
  cardNumber: '',
  expiry: '',
  cvv: '',
  cardholderName: ''
})

const formatCardNumber = (e) => {
  let value = cardData.value.cardNumber.replace(/\s/g, '')
  let formattedValue = value.match(/.{1,4}/g)?.join(' ') || value
  cardData.value.cardNumber = formattedValue
}

const formatExpiry = (e) => {
  let value = cardData.value.expiry.replace(/\D/g, '')
  if (value.length >= 2) {
    value = value.slice(0, 2) + '/' + value.slice(2, 4)
  }
  cardData.value.expiry = value
}

const processPayment = async () => {
  if (!cardData.value.cardNumber || !cardData.value.expiry || !cardData.value.cvv || !cardData.value.cardholderName) {
    error.value = 'Please fill in all card details'
    return
  }

  processing.value = true
  error.value = ''

  try {
    const response = await paymentAPI.processPayment(paymentId)
    paymentSuccess.value = true
    paymentData.value.status = 'Success'

    setTimeout(() => {
      router.push('/patient/appointments')
    }, 2000)
  } catch (err) {
    error.value = err.message || 'Payment processing failed'
  } finally {
    processing.value = false
  }
}

onMounted(() => {
  // Simulate fetching payment data
  paymentData.value = {
    id: paymentId,
    amount: 300,
    status: 'Pending'
  }
  loading.value = false
})
</script>

<style scoped>
.badge-warning {
  background-color: #ffc107 !important;
  color: #000 !important;
}

.badge-success {
  background-color: #28a745 !important;
}

.badge-danger {
  background-color: #dc3545 !important;
}
</style>