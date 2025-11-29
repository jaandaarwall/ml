<template>
  <div class="home-container">
    <!-- Navigation Overlay -->
    <nav class="navbar navbar-expand-lg navbar-dark fixed-top py-3">
      <div class="container">
        <a class="navbar-brand fw-bold fs-3 d-flex align-items-center" href="#">
          <span class="bg-white text-primary rounded-circle d-flex align-items-center justify-content-center me-2" style="width: 40px; height: 40px;">🏥</span>
          HMS
        </a>
        <div class="d-flex gap-3">
          <RouterLink to="/login" class="btn btn-outline-light px-4 fw-bold">Login</RouterLink>
          <RouterLink to="/register" class="btn btn-light text-primary px-4 fw-bold">Register</RouterLink>
        </div>
      </div>
    </nav>

    <!-- Hero Section -->
    <header class="hero-section d-flex align-items-center text-white text-center">
      <div class="container">
        <div class="row justify-content-center">
          <div class="col-lg-8">
            <span class="badge bg-white bg-opacity-25 px-3 py-2 rounded-pill mb-4 border border-white border-opacity-50 backdrop-blur">
              ✨ Advanced Healthcare Management
            </span>
            <h1 class="display-3 fw-bold mb-4 lh-sm">
              Your Health, <br>
              <span class="text-gradient">Our Priority</span>
            </h1>
            <p class="lead mb-5 opacity-90 fs-5 w-75 mx-auto">
              Experience the future of hospital management. Seamlessly connect with doctors, manage appointments, and track your medical history all in one place.
            </p>
            <div class="d-flex gap-3 justify-content-center flex-wrap">
              <RouterLink to="/register" class="btn btn-light btn-lg px-5 py-3 fw-bold rounded-pill shadow-lg transform-hover">
                Get Started Now
              </RouterLink>
              <RouterLink to="/login" class="btn btn-outline-light btn-lg px-5 py-3 fw-bold rounded-pill backdrop-blur">
                Patient Portal
              </RouterLink>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Decorative Elements -->
      <div class="circle circle-1"></div>
      <div class="circle circle-2"></div>
      <div class="wave-bottom">
        <svg viewBox="0 0 1440 320" xmlns="http://www.w3.org/2000/svg">
          <path fill="#f8f9fa" fill-opacity="1" d="M0,96L48,112C96,128,192,160,288,160C384,160,480,128,576,112C672,96,768,96,864,112C960,128,1056,160,1152,160C1248,160,1344,128,1392,112L1440,96L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"></path>
        </svg>
      </div>
    </header>

    <!-- Features Section -->
    <section class="py-5 bg-light" style="margin-top: -2px;">
      <div class="container py-5">
        <div class="row g-4">
          <div class="col-md-4">
            <div class="card h-100 border-0 shadow-sm hover-card p-4 text-center rounded-4">
              <div class="icon-box bg-primary bg-opacity-10 text-primary mx-auto mb-4 rounded-circle d-flex align-items-center justify-content-center">
                📅
              </div>
              <h4 class="fw-bold mb-3">Easy Scheduling</h4>
              <p class="text-muted">Book appointments with top specialists in just a few clicks. Manage your schedule effortlessly.</p>
            </div>
          </div>
          <div class="col-md-4">
            <div class="card h-100 border-0 shadow-sm hover-card p-4 text-center rounded-4">
              <div class="icon-box bg-success bg-opacity-10 text-success mx-auto mb-4 rounded-circle d-flex align-items-center justify-content-center">
                👨‍⚕️
              </div>
              <h4 class="fw-bold mb-3">Expert Doctors</h4>
              <p class="text-muted">Access a network of qualified professionals across various departments like Cardiology, Neurology, and more.</p>
            </div>
          </div>
          <div class="col-md-4">
            <div class="card h-100 border-0 shadow-sm hover-card p-4 text-center rounded-4">
              <div class="icon-box bg-info bg-opacity-10 text-info mx-auto mb-4 rounded-circle d-flex align-items-center justify-content-center">
                📋
              </div>
              <h4 class="fw-bold mb-3">Digital Records</h4>
              <p class="text-muted">Keep track of your medical history, prescriptions, and reports securely in your personal dashboard.</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="bg-white py-4 border-top">
      <div class="container text-center">
        <p class="mb-0 text-muted">© 2025 Hospital Management System. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.home-container {
  overflow-x: hidden;
}

.hero-section {
  background: linear-gradient(135deg, #00a896 0%, #028073 100%);
  min-height: 85vh;
  position: relative;
  padding-top: 80px;
}

.text-gradient {
  background: linear-gradient(to right, #ffffff, #a5f3fc);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.05);
  pointer-events: none;
}
.circle-1 { width: 400px; height: 400px; top: -100px; left: -100px; }
.circle-2 { width: 600px; height: 600px; bottom: 50px; right: -150px; }

.wave-bottom {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  line-height: 0;
}

.backdrop-blur {
  backdrop-filter: blur(10px);
}

.icon-box {
  width: 80px;
  height: 80px;
  font-size: 2rem;
}

.hover-card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.hover-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 1rem 3rem rgba(0,0,0,0.1) !important;
}

.transform-hover {
  transition: transform 0.2s;
}
.transform-hover:hover {
  transform: scale(1.05);
}
</style>