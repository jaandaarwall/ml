<script setup>
import { ref } from 'vue';
import { useMessageStore } from '@/stores/counter.js';
import { useAuthStore } from '@/stores/auth.js';
import { useRouter } from 'vue-router';

const router = useRouter();
const message_store = useMessageStore();
const auth_store = useAuthStore();

const email = ref('');  
const password = ref('');
const isLoading = ref(false);

async function login() {
    isLoading.value = true;
    
    const user = {
        email: email.value,
        password: password.value
    }

    try {
        const response = await fetch('http://127.0.0.1:5000/api/login', { 
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(user) 
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            message_store.updateErrorMessages(data.message);
            isLoading.value = false;
            return;
        }
        
        // Set credentials
        const userData = {
            email: data.user_details.email,
            roles: data.user_details.roles,
        };
        
        auth_store.setUserCred(data.user_details.auth_token, userData);
        message_store.updateErrorMessages('Login successful!');
        
        // Wait a tiny bit for store to update
        await new Promise(resolve => setTimeout(resolve, 100));
        
        // Redirect based on role
        if (data.user_details.roles.includes('admin')) {
            router.push('/admin/dashboard');
        } else if (data.user_details.roles.includes('doctor')) {
            router.push('/doctor/dashboard');
        } else if (data.user_details.roles.includes('user')) {
            router.push('/patient/dashboard');
        } else {
            router.push('/');
        }
    } catch (error) {
        message_store.updateErrorMessages('Login failed. Please try again.');
        console.error('Login error:', error);
    } finally {
        isLoading.value = false;
    }
}
</script>

<template>
    <div class="container-fluid">
        <div class="row justify-content-center mt-5">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-body">
                        <h1 class="card-title text-center mb-4">Login</h1>
                        <form @submit.prevent="login">
                            <div class="mb-3">
                                <label for="email" class="form-label">Email address</label>
                                <input type="email" class="form-control" id="email" 
                                       v-model="email" required>
                            </div>
                            <div class="mb-3">
                                <label for="password" class="form-label">Password</label>
                                <input type="password" class="form-control" id="password" 
                                       v-model="password" required>
                            </div>
                            <button type="submit" class="btn btn-primary w-100" :disabled="isLoading">
                                <span v-if="isLoading">Logging in...</span>
                                <span v-else>Login</span>
                            </button>
                        </form>
                        <div class="text-center mt-3">
                            <p>Don't have an account? <RouterLink to="/register">Register here</RouterLink></p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>