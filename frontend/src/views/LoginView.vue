<script setup>
import {ref} from 'vue';
import { useMessageStore } from '@/stores/counter.js';
import { useAuthStore } from '@/stores/auth.js';
import { useRouter } from 'vue-router';

const router = useRouter();
const message_store = useMessageStore();
const auth_store = useAuthStore();

const email = ref('');  
const password = ref('');

async function login(){
    const user = {
        email: email.value,
        password: password.value
    }

    const response = await fetch('http://127.0.0.1:5000/api/login',{ 
        method: 'POST',
        headers:{
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(user) 
    })
    
    if (!response.ok){
        const errordata = await response.json();
        message_store.updateErrorMessages(errordata.message);
    }
    else {
        const data = await response.json()
        message_store.updateErrorMessages(data.message);
        
        const user = {
            email: data.user_details.email,
            roles: data.user_details.roles,
        }
        auth_store.setUserCred(data.user_details.auth_token, user)
        
        // Redirect based on role
        if (auth_store.isAdmin) {
            router.push('/admin/dashboard')
        } else if (auth_store.isDoctor) {
            router.push('/doctor/dashboard')
        } else {
            router.push('/patient/dashboard')
        }
    }
}

</script>


<template>
    <div class="container-fluid">
        <div class="row justify-content-center mt-3">
            <div class="col-6  align-items-center">
                <h1>Login</h1>
                <form @submit.prevent = "login">
                    <div class="mb-3">
                        <label for="exampleInputEmail1" class="form-label">Email address</label>
                        <input type="email" class="form-control" id="exampleInputEmail1" aria-describedby="emailHelp" v-model="email">
                    </div>
                    <div class="mb-3">
                        <label for="exampleInputPassword1" class="form-label">Password</label>
                        <input type="password" class="form-control" id="exampleInputPassword1" v-model="password">
                    </div>
                    <button type="submit" class="btn btn-primary">Submit</button>
                </form>
            </div>
        </div>
    </div>
</template>