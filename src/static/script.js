// Global State Management
class AppState {
    constructor() {
        this.user = null;
        this.token = localStorage.getItem('token');
        this.isLoggedIn = false;
        this.notifications = [];
        this.init();
    }

    init() {
        if (this.token) {
            this.validateToken();
        }
        this.setupEventListeners();
        this.hideLoadingScreen();
    }

    async validateToken() {
        try {
            const response = await fetch('/api/profile', {
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.setUser(data.profile);
            } else {
                this.logout();
            }
        } catch (error) {
            console.error('Token validation failed:', error);
            this.logout();
        }
    }

    setUser(user) {
        this.user = user;
        this.isLoggedIn = true;
        this.updateUI();
        this.loadNotifications();
    }

    logout() {
        this.user = null;
        this.token = null;
        this.isLoggedIn = false;
        localStorage.removeItem('token');
        this.updateUI();
        this.showToast('Você foi desconectado', 'info');
    }

    updateUI() {
        const navbar = document.getElementById('navbar');
        const userNavbar = document.getElementById('user-navbar');
        
        if (this.isLoggedIn) {
            navbar.classList.add('hidden');
            userNavbar.classList.remove('hidden');
            this.updateUserInfo();
        } else {
            navbar.classList.remove('hidden');
            userNavbar.classList.add('hidden');
        }
    }

    updateUserInfo() {
        if (!this.user) return;
        
        const userName = document.getElementById('user-name');
        const userAvatarImg = document.getElementById('user-avatar-img');
        
        if (userName) {
            userName.textContent = this.user.full_name || this.user.username;
        }
        
        if (userAvatarImg && this.user.profile_picture) {
            userAvatarImg.src = `/${this.user.profile_picture}`;
        }
    }

    async loadNotifications() {
        if (!this.isLoggedIn) return;

        try {
            const response = await fetch('/api/profile/notifications?unread_only=true', {
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.updateNotificationBadge(data.unread_count);
            }
        } catch (error) {
            console.error('Failed to load notifications:', error);
        }
    }

    updateNotificationBadge(count) {
        const badge = document.getElementById('notification-badge');
        if (badge) {
            if (count > 0) {
                badge.textContent = count > 99 ? '99+' : count;
                badge.classList.remove('hidden');
            } else {
                badge.classList.add('hidden');
            }
        }
    }

    hideLoadingScreen() {
        setTimeout(() => {
            const loadingScreen = document.getElementById('loading-screen');
            if (loadingScreen) {
                loadingScreen.classList.add('hidden');
            }
        }, 1500);
    }

    setupEventListeners() {
        // Navigation
        this.setupNavigation();
        
        // Modals
        this.setupModals();
        
        // Forms
        this.setupForms();
        
        // Scroll effects
        this.setupScrollEffects();
        
        // Stats animation
        this.setupStatsAnimation();
        
        // City selection
        this.setupCitySelection();
        
        // Contact form
        this.setupContactForm();
    }

    setupNavigation() {
        // Mobile menu toggle
        const navToggle = document.getElementById('nav-toggle');
        const navMenu = document.getElementById('nav-menu');
        
        if (navToggle && navMenu) {
            navToggle.addEventListener('click', () => {
                navMenu.classList.toggle('active');
            });
        }

        // Smooth scrolling for navigation links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(anchor.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                    
                    // Close mobile menu if open
                    if (navMenu) {
                        navMenu.classList.remove('active');
                    }
                }
            });
        });

        // Logout button
        const logoutBtn = document.getElementById('logout-btn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => {
                this.logout();
            });
        }
    }

    setupModals() {
        // Modal triggers
        const loginBtns = document.querySelectorAll('#login-btn, #hero-login-btn');
        const registerBtns = document.querySelectorAll('#register-btn, #hero-register-btn');
        
        loginBtns.forEach(btn => {
            btn.addEventListener('click', () => this.openModal('login-modal'));
        });
        
        registerBtns.forEach(btn => {
            btn.addEventListener('click', () => this.openModal('register-modal'));
        });

        // Modal close buttons
        document.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const modalId = btn.getAttribute('data-modal');
                this.closeModal(modalId);
            });
        });

        // Modal overlay close
        document.querySelectorAll('.modal-overlay').forEach(overlay => {
            overlay.addEventListener('click', (e) => {
                const modal = overlay.closest('.modal');
                if (modal) {
                    this.closeModal(modal.id);
                }
            });
        });

        // Switch between login and register
        const switchToRegister = document.getElementById('switch-to-register');
        const switchToLogin = document.getElementById('switch-to-login');
        
        if (switchToRegister) {
            switchToRegister.addEventListener('click', (e) => {
                e.preventDefault();
                this.closeModal('login-modal');
                this.openModal('register-modal');
            });
        }
        
        if (switchToLogin) {
            switchToLogin.addEventListener('click', (e) => {
                e.preventDefault();
                this.closeModal('register-modal');
                this.openModal('login-modal');
            });
        }

        // Password toggle
        document.querySelectorAll('.password-toggle').forEach(btn => {
            btn.addEventListener('click', () => {
                const targetId = btn.getAttribute('data-target');
                const input = document.getElementById(targetId);
                const icon = btn.querySelector('i');
                
                if (input.type === 'password') {
                    input.type = 'text';
                    icon.className = 'bi bi-eye-slash';
                } else {
                    input.type = 'password';
                    icon.className = 'bi bi-eye';
                }
            });
        });
    }

    setupForms() {
        // Login form
        const loginForm = document.getElementById('login-form');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => this.handleLogin(e));
        }

        // Register form
        const registerForm = document.getElementById('register-form');
        if (registerForm) {
            registerForm.addEventListener('submit', (e) => this.handleRegister(e));
            this.setupFormValidation(registerForm);
        }
    }

    setupFormValidation(form) {
        // Real-time validation
        const usernameInput = form.querySelector('#register-username');
        const emailInput = form.querySelector('#register-email');
        const cpfInput = form.querySelector('#register-cpf');
        const passwordInput = form.querySelector('#register-password');
        const confirmPasswordInput = form.querySelector('#register-confirm-password');

        if (usernameInput) {
            usernameInput.addEventListener('blur', () => this.validateUsername(usernameInput.value));
            usernameInput.addEventListener('input', this.debounce(() => this.validateUsername(usernameInput.value), 500));
        }

        if (emailInput) {
            emailInput.addEventListener('blur', () => this.validateEmail(emailInput.value));
            emailInput.addEventListener('input', this.debounce(() => this.validateEmail(emailInput.value), 500));
        }

        if (cpfInput) {
            cpfInput.addEventListener('input', (e) => {
                e.target.value = this.formatCPF(e.target.value);
                this.validateCPF(e.target.value);
            });
        }

        if (confirmPasswordInput) {
            confirmPasswordInput.addEventListener('input', () => {
                this.validatePasswordMatch(passwordInput.value, confirmPasswordInput.value);
            });
        }
    }

    setupScrollEffects() {
        // Navbar scroll effect
        const navbar = document.getElementById('navbar');
        
        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });

        // Intersection Observer for animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, observerOptions);

        // Observe elements for animation
        document.querySelectorAll('.step-item, .feature-card, .city-card').forEach(el => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(30px)';
            el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            observer.observe(el);
        });
    }

    setupStatsAnimation() {
        const stats = document.querySelectorAll('.stat-number');
        let animated = false;

        const animateStats = () => {
            if (animated) return;
            animated = true;

            stats.forEach(stat => {
                const target = parseInt(stat.getAttribute('data-count'));
                const duration = 2000;
                const step = target / (duration / 16);
                let current = 0;

                const timer = setInterval(() => {
                    current += step;
                    if (current >= target) {
                        current = target;
                        clearInterval(timer);
                    }
                    stat.textContent = Math.floor(current).toLocaleString();
                }, 16);
            });
        };

        const statsObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateStats();
                }
            });
        }, { threshold: 0.5 });

        const heroStats = document.querySelector('.hero-stats');
        if (heroStats) {
            statsObserver.observe(heroStats);
        }
    }

    setupCitySelection() {
        document.querySelectorAll('[data-city]').forEach(btn => {
            btn.addEventListener('click', () => {
                const city = btn.getAttribute('data-city');
                this.selectCity(city);
            });
        });
    }

    setupContactForm() {
        const contactForm = document.getElementById('contact-form');
        if (contactForm) {
            contactForm.addEventListener('submit', (e) => this.handleContactForm(e));
        }
    }

    // Modal methods
    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
        }
    }

    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('active');
            document.body.style.overflow = '';
        }
    }

    // Form handlers
    async handleLogin(e) {
        e.preventDefault();
        
        const form = e.target;
        const formData = new FormData(form);
        const loginField = formData.get('login-field') || document.getElementById('login-field').value;
        const password = formData.get('login-password') || document.getElementById('login-password').value;

        if (!loginField || !password) {
            this.showToast('Por favor, preencha todos os campos', 'error');
            return;
        }

        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Entrando...';
        submitBtn.disabled = true;

        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    login_field: loginField,
                    password: password
                })
            });

            const data = await response.json();

            if (response.ok) {
                this.token = data.access_token;
                localStorage.setItem('token', this.token);
                this.setUser(data.user);
                this.closeModal('login-modal');
                this.showToast('Login realizado com sucesso!', 'success');
                form.reset();
            } else {
                this.showToast(data.message || 'Erro ao fazer login', 'error');
            }
        } catch (error) {
            console.error('Login error:', error);
            this.showToast('Erro de conexão. Tente novamente.', 'error');
        } finally {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    }

    async handleRegister(e) {
        e.preventDefault();
        
        const form = e.target;
        const formData = new FormData(form);
        
        const userData = {
            full_name: formData.get('register-full-name') || document.getElementById('register-full-name').value,
            username: formData.get('register-username') || document.getElementById('register-username').value,
            email: formData.get('register-email') || document.getElementById('register-email').value,
            cpf: formData.get('register-cpf') || document.getElementById('register-cpf').value,
            phone: formData.get('register-phone') || document.getElementById('register-phone').value,
            city: formData.get('register-city') || document.getElementById('register-city').value,
            role: formData.get('register-role') || document.getElementById('register-role').value,
            password: formData.get('register-password') || document.getElementById('register-password').value,
            confirm_password: formData.get('register-confirm-password') || document.getElementById('register-confirm-password').value
        };

        // Validation
        if (!this.validateRegisterForm(userData)) {
            return;
        }

        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Criando conta...';
        submitBtn.disabled = true;

        try {
            const response = await fetch('/api/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(userData)
            });

            const data = await response.json();

            if (response.ok) {
                this.showToast('Conta criada com sucesso! Faça login para continuar.', 'success');
                this.closeModal('register-modal');
                this.openModal('login-modal');
                form.reset();
            } else {
                this.showToast(data.message || 'Erro ao criar conta', 'error');
            }
        } catch (error) {
            console.error('Register error:', error);
            this.showToast('Erro de conexão. Tente novamente.', 'error');
        } finally {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    }

    async handleContactForm(e) {
        e.preventDefault();
        
        const form = e.target;
        const name = document.getElementById('contact-name').value;
        const email = document.getElementById('contact-email').value;
        const message = document.getElementById('contact-message').value;

        if (!name || !email || !message) {
            this.showToast('Por favor, preencha todos os campos', 'error');
            return;
        }

        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Enviando...';
        submitBtn.disabled = true;

        // Simulate form submission (replace with actual endpoint)
        setTimeout(() => {
            this.showToast('Mensagem enviada com sucesso! Entraremos em contato em breve.', 'success');
            form.reset();
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }, 2000);
    }

    // Validation methods
    validateRegisterForm(userData) {
        const errors = [];

        if (!userData.full_name || userData.full_name.length < 2) {
            errors.push('Nome completo deve ter pelo menos 2 caracteres');
        }

        if (!userData.username || userData.username.length < 3) {
            errors.push('Nome de usuário deve ter pelo menos 3 caracteres');
        }

        if (!this.isValidEmail(userData.email)) {
            errors.push('Email inválido');
        }

        if (!this.isValidCPF(userData.cpf.replace(/\D/g, ''))) {
            errors.push('CPF inválido');
        }

        if (!userData.city) {
            errors.push('Selecione uma cidade');
        }

        if (!userData.role) {
            errors.push('Selecione o tipo de usuário');
        }

        if (!userData.password || userData.password.length < 6) {
            errors.push('Senha deve ter pelo menos 6 caracteres');
        }

        if (userData.password !== userData.confirm_password) {
            errors.push('Senhas não conferem');
        }

        if (errors.length > 0) {
            this.showToast(errors[0], 'error');
            return false;
        }

        return true;
    }

    async validateUsername(username) {
        const feedback = document.getElementById('username-feedback');
        if (!feedback) return;

        if (!username || username.length < 3) {
            this.setFieldFeedback(feedback, 'Nome de usuário deve ter pelo menos 3 caracteres', 'error');
            return;
        }

        try {
            const response = await fetch(`/api/auth/check-username?username=${encodeURIComponent(username)}`);
            const data = await response.json();

            if (data.available) {
                this.setFieldFeedback(feedback, 'Nome de usuário disponível', 'success');
            } else {
                this.setFieldFeedback(feedback, 'Nome de usuário já está em uso', 'error');
            }
        } catch (error) {
            this.setFieldFeedback(feedback, '', '');
        }
    }

    async validateEmail(email) {
        const feedback = document.getElementById('email-feedback');
        if (!feedback) return;

        if (!this.isValidEmail(email)) {
            this.setFieldFeedback(feedback, 'Email inválido', 'error');
            return;
        }

        try {
            const response = await fetch(`/api/auth/check-email?email=${encodeURIComponent(email)}`);
            const data = await response.json();

            if (data.available) {
                this.setFieldFeedback(feedback, 'Email disponível', 'success');
            } else {
                this.setFieldFeedback(feedback, 'Email já está em uso', 'error');
            }
        } catch (error) {
            this.setFieldFeedback(feedback, '', '');
        }
    }

    validateCPF(cpf) {
        const feedback = document.getElementById('cpf-feedback');
        if (!feedback) return;

        const cleanCPF = cpf.replace(/\D/g, '');
        
        if (this.isValidCPF(cleanCPF)) {
            this.setFieldFeedback(feedback, 'CPF válido', 'success');
        } else {
            this.setFieldFeedback(feedback, 'CPF inválido', 'error');
        }
    }

    validatePasswordMatch(password, confirmPassword) {
        const confirmInput = document.getElementById('register-confirm-password');
        if (!confirmInput) return;

        if (password === confirmPassword && password.length > 0) {
            confirmInput.style.borderColor = 'var(--success-color)';
        } else if (confirmPassword.length > 0) {
            confirmInput.style.borderColor = 'var(--error-color)';
        } else {
            confirmInput.style.borderColor = 'var(--border-color)';
        }
    }

    setFieldFeedback(element, message, type) {
        element.textContent = message;
        element.className = `field-feedback ${type}`;
    }

    // Utility methods
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    isValidCPF(cpf) {
        if (cpf.length !== 11 || /^(\d)\1{10}$/.test(cpf)) {
            return false;
        }

        let sum = 0;
        for (let i = 0; i < 9; i++) {
            sum += parseInt(cpf.charAt(i)) * (10 - i);
        }
        let remainder = (sum * 10) % 11;
        if (remainder === 10 || remainder === 11) remainder = 0;
        if (remainder !== parseInt(cpf.charAt(9))) return false;

        sum = 0;
        for (let i = 0; i < 10; i++) {
            sum += parseInt(cpf.charAt(i)) * (11 - i);
        }
        remainder = (sum * 10) % 11;
        if (remainder === 10 || remainder === 11) remainder = 0;
        return remainder === parseInt(cpf.charAt(10));
    }

    formatCPF(value) {
        const cpf = value.replace(/\D/g, '');
        return cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    selectCity(city) {
        // Store selected city
        localStorage.setItem('selectedCity', city);
        
        // Show city selection feedback
        this.showToast(`Cidade selecionada: ${city}`, 'success');
        
        // In a real implementation, this would redirect to the city-specific subdomain
        // For now, we'll just show a message
        setTimeout(() => {
            this.showToast(`Redirecionando para deuruim${city}...`, 'info');
        }, 1000);
    }

    // Toast notification system
    showToast(message, type = 'info', duration = 5000) {
        const container = document.getElementById('toast-container');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const toastId = Date.now();
        toast.innerHTML = `
            <div class="toast-header">
                <span class="toast-title">${this.getToastTitle(type)}</span>
                <button class="toast-close" onclick="app.closeToast(${toastId})">
                    <i class="bi bi-x"></i>
                </button>
            </div>
            <div class="toast-message">${message}</div>
        `;
        
        toast.setAttribute('data-toast-id', toastId);
        container.appendChild(toast);

        // Show toast
        setTimeout(() => {
            toast.classList.add('show');
        }, 100);

        // Auto remove
        setTimeout(() => {
            this.closeToast(toastId);
        }, duration);
    }

    closeToast(toastId) {
        const toast = document.querySelector(`[data-toast-id="${toastId}"]`);
        if (toast) {
            toast.classList.remove('show');
            setTimeout(() => {
                toast.remove();
            }, 300);
        }
    }

    getToastTitle(type) {
        const titles = {
            success: 'Sucesso',
            error: 'Erro',
            warning: 'Atenção',
            info: 'Informação'
        };
        return titles[type] || 'Notificação';
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new AppState();
});

// Service Worker registration (for PWA capabilities)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then((registration) => {
                console.log('SW registered: ', registration);
            })
            .catch((registrationError) => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}

