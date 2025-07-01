// Profile page functionality
class ProfileManager {
    constructor() {
        this.currentTab = 'complaints';
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.animateStats();
        this.loadUserData();
    }

    setupEventListeners() {
        // Tab switching
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.switchTab(btn.getAttribute('data-tab'));
            });
        });

        // Edit profile button
        const editProfileBtn = document.getElementById('edit-profile-btn');
        if (editProfileBtn) {
            editProfileBtn.addEventListener('click', () => {
                app.openModal('edit-profile-modal');
            });
        }

        // Change avatar button
        const changeAvatarBtn = document.getElementById('change-avatar-btn');
        const avatarUpload = document.getElementById('avatar-upload');
        if (changeAvatarBtn && avatarUpload) {
            changeAvatarBtn.addEventListener('click', () => {
                avatarUpload.click();
            });
            
            avatarUpload.addEventListener('change', (e) => {
                this.handleAvatarChange(e.target.files[0]);
            });
        }

        // Change cover button
        const changeCoverBtn = document.getElementById('change-cover-btn');
        const coverUpload = document.getElementById('cover-upload');
        if (changeCoverBtn && coverUpload) {
            changeCoverBtn.addEventListener('click', () => {
                coverUpload.click();
            });
            
            coverUpload.addEventListener('change', (e) => {
                this.handleCoverChange(e.target.files[0]);
            });
        }

        // Share profile button
        const shareProfileBtn = document.getElementById('share-profile-btn');
        if (shareProfileBtn) {
            shareProfileBtn.addEventListener('click', () => {
                this.shareProfile();
            });
        }

        // Edit profile form
        const editProfileForm = document.getElementById('edit-profile-form');
        if (editProfileForm) {
            editProfileForm.addEventListener('submit', (e) => {
                this.handleProfileUpdate(e);
            });
        }

        // Change password button
        const changePasswordBtn = document.getElementById('change-password-btn');
        if (changePasswordBtn) {
            changePasswordBtn.addEventListener('click', () => {
                app.openModal('change-password-modal');
            });
        }

        // Change password form
        const changePasswordForm = document.getElementById('change-password-form');
        if (changePasswordForm) {
            changePasswordForm.addEventListener('submit', (e) => {
                this.handlePasswordChange(e);
            });
        }

        // Password strength indicator
        const newPasswordInput = document.getElementById('new-password');
        if (newPasswordInput) {
            newPasswordInput.addEventListener('input', (e) => {
                this.updatePasswordStrength(e.target.value);
            });
        }

        // Export data button
        const exportDataBtn = document.getElementById('export-data-btn');
        if (exportDataBtn) {
            exportDataBtn.addEventListener('click', () => {
                this.exportUserData();
            });
        }

        // Delete account button
        const deleteAccountBtn = document.getElementById('delete-account-btn');
        if (deleteAccountBtn) {
            deleteAccountBtn.addEventListener('click', () => {
                this.confirmDeleteAccount();
            });
        }

        // Filter changes
        const statusFilter = document.getElementById('status-filter');
        const categoryFilter = document.getElementById('category-filter');
        
        if (statusFilter) {
            statusFilter.addEventListener('change', () => {
                this.filterComplaints();
            });
        }
        
        if (categoryFilter) {
            categoryFilter.addEventListener('change', () => {
                this.filterComplaints();
            });
        }
    }

    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Update tab content
        document.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`).classList.add('active');

        this.currentTab = tabName;

        // Load tab-specific data
        this.loadTabData(tabName);
    }

    async loadTabData(tabName) {
        switch (tabName) {
            case 'complaints':
                await this.loadUserComplaints();
                break;
            case 'activity':
                await this.loadUserActivity();
                break;
            case 'favorites':
                await this.loadUserFavorites();
                break;
            case 'settings':
                // Settings are already loaded
                break;
        }
    }

    async loadUserComplaints() {
        try {
            // In a real implementation, this would fetch from API
            console.log('Loading user complaints...');
            
            // Simulate loading
            const complaintsList = document.getElementById('user-complaints-list');
            if (complaintsList) {
                // Add loading state
                complaintsList.style.opacity = '0.5';
                
                setTimeout(() => {
                    complaintsList.style.opacity = '1';
                }, 500);
            }
        } catch (error) {
            console.error('Error loading complaints:', error);
        }
    }

    async loadUserActivity() {
        try {
            console.log('Loading user activity...');
        } catch (error) {
            console.error('Error loading activity:', error);
        }
    }

    async loadUserFavorites() {
        try {
            console.log('Loading user favorites...');
        } catch (error) {
            console.error('Error loading favorites:', error);
        }
    }

    filterComplaints() {
        const statusFilter = document.getElementById('status-filter').value;
        const categoryFilter = document.getElementById('category-filter').value;
        const complaints = document.querySelectorAll('.complaint-item');

        complaints.forEach(complaint => {
            let show = true;

            // Filter by status
            if (statusFilter !== 'all') {
                const status = complaint.querySelector('.complaint-status');
                const hasStatus = status.classList.contains(`status-${statusFilter}`);
                if (!hasStatus) show = false;
            }

            // Filter by category (would need category data attribute)
            if (categoryFilter !== 'all') {
                // In a real implementation, complaints would have category data
                // For now, we'll show all
            }

            complaint.style.display = show ? 'flex' : 'none';
        });
    }

    handleAvatarChange(file) {
        if (!file) return;

        if (!file.type.startsWith('image/')) {
            app.showToast('Por favor, selecione uma imagem válida', 'error');
            return;
        }

        if (file.size > 5 * 1024 * 1024) { // 5MB
            app.showToast('Imagem muito grande. Máximo 5MB', 'error');
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            const avatarImg = document.getElementById('avatar-img');
            const navAvatarImg = document.getElementById('user-avatar-img');
            
            if (avatarImg) avatarImg.src = e.target.result;
            if (navAvatarImg) navAvatarImg.src = e.target.result;
            
            app.showToast('Foto de perfil atualizada!', 'success');
            
            // In a real implementation, upload to server
            this.uploadAvatar(file);
        };
        reader.readAsDataURL(file);
    }

    handleCoverChange(file) {
        if (!file) return;

        if (!file.type.startsWith('image/')) {
            app.showToast('Por favor, selecione uma imagem válida', 'error');
            return;
        }

        if (file.size > 10 * 1024 * 1024) { // 10MB
            app.showToast('Imagem muito grande. Máximo 10MB', 'error');
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            const coverImage = document.getElementById('cover-image');
            if (coverImage) {
                coverImage.style.backgroundImage = `url(${e.target.result})`;
                coverImage.style.backgroundSize = 'cover';
                coverImage.style.backgroundPosition = 'center';
            }
            
            app.showToast('Foto de capa atualizada!', 'success');
            
            // In a real implementation, upload to server
            this.uploadCover(file);
        };
        reader.readAsDataURL(file);
    }

    async uploadAvatar(file) {
        try {
            // Simulate upload
            console.log('Uploading avatar:', file.name);
        } catch (error) {
            console.error('Error uploading avatar:', error);
            app.showToast('Erro ao fazer upload da foto', 'error');
        }
    }

    async uploadCover(file) {
        try {
            // Simulate upload
            console.log('Uploading cover:', file.name);
        } catch (error) {
            console.error('Error uploading cover:', error);
            app.showToast('Erro ao fazer upload da capa', 'error');
        }
    }

    shareProfile() {
        const profileUrl = `${window.location.origin}/profile/${app.currentUser?.username || 'joao_silva'}`;
        
        if (navigator.share) {
            navigator.share({
                title: 'Perfil no deuruimcidadao',
                text: 'Confira meu perfil no deuruimcidadao!',
                url: profileUrl
            });
        } else {
            // Fallback: copy to clipboard
            navigator.clipboard.writeText(profileUrl).then(() => {
                app.showToast('Link do perfil copiado!', 'success');
            }).catch(() => {
                app.showToast('Erro ao copiar link', 'error');
            });
        }
    }

    async handleProfileUpdate(e) {
        e.preventDefault();
        
        const form = e.target;
        const formData = new FormData(form);
        const submitBtn = form.querySelector('button[type="submit"]');
        
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Salvando...';
        submitBtn.disabled = true;

        try {
            const profileData = {
                full_name: formData.get('full_name'),
                username: formData.get('username'),
                email: formData.get('email'),
                phone: formData.get('phone'),
                bio: formData.get('bio'),
                city: formData.get('city'),
                neighborhood: formData.get('neighborhood')
            };

            // Simulate API call
            await this.updateProfile(profileData);
            
            // Update UI
            this.updateProfileUI(profileData);
            
            app.showToast('Perfil atualizado com sucesso!', 'success');
            app.closeModal('edit-profile-modal');
            
        } catch (error) {
            console.error('Error updating profile:', error);
            app.showToast('Erro ao atualizar perfil', 'error');
        } finally {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    }

    async updateProfile(profileData) {
        // Simulate API call
        return new Promise((resolve) => {
            setTimeout(() => {
                console.log('Profile updated:', profileData);
                resolve({ success: true });
            }, 1500);
        });
    }

    updateProfileUI(profileData) {
        // Update profile name
        const profileName = document.getElementById('profile-name');
        if (profileName) {
            profileName.textContent = profileData.full_name;
        }

        // Update profile username
        const profileUsername = document.getElementById('profile-username');
        if (profileUsername) {
            profileUsername.textContent = `@${profileData.username}`;
        }

        // Update profile bio
        const profileBio = document.getElementById('profile-bio');
        if (profileBio) {
            profileBio.textContent = profileData.bio;
        }

        // Update navigation name
        const navUserName = document.getElementById('user-name');
        if (navUserName) {
            navUserName.textContent = profileData.full_name.split(' ')[0];
        }
    }

    async handlePasswordChange(e) {
        e.preventDefault();
        
        const form = e.target;
        const formData = new FormData(form);
        const submitBtn = form.querySelector('button[type="submit"]');
        
        const currentPassword = formData.get('current_password');
        const newPassword = formData.get('new_password');
        const confirmPassword = formData.get('confirm_password');

        // Validate passwords
        if (newPassword !== confirmPassword) {
            app.showToast('As senhas não coincidem', 'error');
            return;
        }

        if (newPassword.length < 6) {
            app.showToast('A nova senha deve ter pelo menos 6 caracteres', 'error');
            return;
        }

        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Alterando...';
        submitBtn.disabled = true;

        try {
            await this.changePassword(currentPassword, newPassword);
            
            app.showToast('Senha alterada com sucesso!', 'success');
            app.closeModal('change-password-modal');
            form.reset();
            
        } catch (error) {
            console.error('Error changing password:', error);
            app.showToast('Erro ao alterar senha', 'error');
        } finally {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    }

    async changePassword(currentPassword, newPassword) {
        // Simulate API call
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                // Simulate validation
                if (currentPassword === 'wrongpassword') {
                    reject(new Error('Senha atual incorreta'));
                } else {
                    console.log('Password changed successfully');
                    resolve({ success: true });
                }
            }, 1500);
        });
    }

    updatePasswordStrength(password) {
        const strengthIndicator = document.getElementById('password-strength');
        if (!strengthIndicator) return;

        let strength = 0;
        let feedback = [];

        if (password.length >= 8) strength++;
        else feedback.push('Pelo menos 8 caracteres');

        if (/[a-z]/.test(password)) strength++;
        else feedback.push('Letra minúscula');

        if (/[A-Z]/.test(password)) strength++;
        else feedback.push('Letra maiúscula');

        if (/[0-9]/.test(password)) strength++;
        else feedback.push('Número');

        if (/[^A-Za-z0-9]/.test(password)) strength++;
        else feedback.push('Caractere especial');

        const levels = ['Muito fraca', 'Fraca', 'Regular', 'Boa', 'Muito forte'];
        const colors = ['#ef4444', '#f97316', '#eab308', '#22c55e', '#16a34a'];

        strengthIndicator.innerHTML = `
            <div class="strength-bar">
                <div class="strength-fill" style="width: ${(strength / 5) * 100}%; background-color: ${colors[strength - 1] || '#ef4444'}"></div>
            </div>
            <div class="strength-text" style="color: ${colors[strength - 1] || '#ef4444'}">
                ${levels[strength - 1] || 'Muito fraca'}
            </div>
            ${feedback.length > 0 ? `<div class="strength-feedback">Adicione: ${feedback.join(', ')}</div>` : ''}
        `;
    }

    exportUserData() {
        // Simulate data export
        const userData = {
            profile: {
                name: 'João Silva Santos',
                username: 'joao_silva',
                email: 'joao.silva@email.com',
                city: 'Cuiabá - MT'
            },
            complaints: [
                { title: 'Buraco na Rua das Palmeiras', status: 'resolved', date: '2024-01-15' },
                { title: 'Iluminação deficiente na Praça Central', status: 'pending', date: '2024-01-20' }
            ],
            stats: {
                totalComplaints: 24,
                resolvedComplaints: 18,
                votesReceived: 156,
                points: 1250
            }
        };

        const dataStr = JSON.stringify(userData, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = 'meus-dados-deuruimcidadao.json';
        link.click();
        
        URL.revokeObjectURL(url);
        app.showToast('Dados exportados com sucesso!', 'success');
    }

    confirmDeleteAccount() {
        const confirmed = confirm(
            'Tem certeza que deseja excluir sua conta?\n\n' +
            'Esta ação é irreversível e todos os seus dados serão perdidos permanentemente.'
        );

        if (confirmed) {
            const doubleConfirm = prompt(
                'Para confirmar, digite "EXCLUIR" (em maiúsculas):'
            );

            if (doubleConfirm === 'EXCLUIR') {
                this.deleteAccount();
            } else {
                app.showToast('Exclusão cancelada', 'info');
            }
        }
    }

    async deleteAccount() {
        try {
            // Simulate API call
            app.showToast('Processando exclusão da conta...', 'info');
            
            setTimeout(() => {
                app.showToast('Conta excluída com sucesso', 'success');
                // Redirect to home page
                setTimeout(() => {
                    window.location.href = 'index.html';
                }, 2000);
            }, 3000);
            
        } catch (error) {
            console.error('Error deleting account:', error);
            app.showToast('Erro ao excluir conta', 'error');
        }
    }

    animateStats() {
        const stats = document.querySelectorAll('.stat-number');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const stat = entry.target;
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
                        stat.textContent = Math.floor(current);
                    }, 16);
                    
                    observer.unobserve(stat);
                }
            });
        }, { threshold: 0.5 });

        stats.forEach(stat => observer.observe(stat));
    }

    async loadUserData() {
        try {
            // In a real implementation, this would fetch user data from API
            console.log('Loading user data...');
        } catch (error) {
            console.error('Error loading user data:', error);
        }
    }
}

// Initialize profile manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.profileManager = new ProfileManager();
});

// CSS for profile-specific styles
const profileStyles = `
/* Profile Styles */
.profile-main {
    padding-top: 90px;
    min-height: 100vh;
    background: var(--bg-primary);
}

.profile-header {
    margin-bottom: 2rem;
}

.profile-cover {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-lg);
    overflow: hidden;
}

.cover-image {
    height: 200px;
    background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
}

.change-cover-btn {
    background: rgba(0, 0, 0, 0.7);
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: var(--border-radius);
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    transition: var(--transition);
}

.change-cover-btn:hover {
    background: rgba(0, 0, 0, 0.8);
}

.profile-info {
    padding: 2rem;
    display: flex;
    gap: 2rem;
    align-items: flex-start;
}

.profile-avatar-container {
    position: relative;
    margin-top: -60px;
}

.profile-avatar {
    position: relative;
    width: 120px;
    height: 120px;
    border-radius: 50%;
    border: 4px solid var(--bg-card);
    overflow: hidden;
    background: var(--bg-tertiary);
}

.profile-avatar img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.change-avatar-btn {
    position: absolute;
    bottom: 8px;
    right: 8px;
    width: 32px;
    height: 32px;
    background: var(--primary-color);
    color: white;
    border: none;
    border-radius: 50%;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: var(--transition);
}

.change-avatar-btn:hover {
    background: var(--primary-dark);
}

.profile-details {
    flex: 1;
}

.profile-details h1 {
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
}

.profile-details p:first-of-type {
    color: var(--text-secondary);
    margin-bottom: 1rem;
}

.profile-badges {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1rem;
    flex-wrap: wrap;
}

.badge {
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 500;
}

.badge-primary {
    background: var(--primary-light);
    color: var(--primary-color);
}

.badge-success {
    background: rgba(16, 185, 129, 0.1);
    color: var(--success-color);
}

.badge-info {
    background: rgba(6, 182, 212, 0.1);
    color: var(--accent-color);
}

.profile-actions {
    display: flex;
    gap: 1rem;
    flex-direction: column;
}

.profile-stats {
    display: flex;
    gap: 2rem;
    margin-bottom: 3rem;
    padding: 2rem;
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-lg);
    justify-content: space-around;
}

.stat-item {
    text-align: center;
}

.stat-item .stat-number {
    font-size: 2rem;
    font-weight: 700;
    color: var(--primary-color);
    margin-bottom: 0.25rem;
}

.stat-item .stat-label {
    color: var(--text-secondary);
    font-size: 0.875rem;
}

.profile-content {
    display: grid;
    grid-template-columns: 300px 1fr;
    gap: 2rem;
}

.profile-sidebar {
    display: flex;
    flex-direction: column;
    gap: 2rem;
}

.sidebar-section {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-lg);
    padding: 1.5rem;
}

.sidebar-section h3 {
    font-size: 1.125rem;
    font-weight: 600;
    margin-bottom: 1rem;
}

.achievements-grid {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.achievement-item {
    display: flex;
    gap: 0.75rem;
    padding: 0.75rem;
    border-radius: var(--border-radius);
    transition: var(--transition);
}

.achievement-item.earned {
    background: var(--primary-light);
}

.achievement-item:not(.earned) {
    opacity: 0.5;
    background: var(--bg-tertiary);
}

.achievement-icon {
    font-size: 1.5rem;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    background: var(--bg-primary);
}

.achievement-name {
    font-weight: 500;
    font-size: 0.875rem;
    margin-bottom: 0.25rem;
}

.achievement-desc {
    font-size: 0.75rem;
    color: var(--text-muted);
}

.activity-summary {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.summary-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.summary-item i {
    color: var(--primary-color);
    width: 20px;
}

.summary-content {
    display: flex;
    flex-direction: column;
}

.summary-label {
    font-size: 0.75rem;
    color: var(--text-muted);
}

.summary-value {
    font-weight: 500;
    font-size: 0.875rem;
}

.contact-info {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.contact-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-size: 0.875rem;
}

.contact-item i {
    color: var(--primary-color);
    width: 20px;
}

.profile-main-content {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-lg);
    overflow: hidden;
}

.profile-tabs {
    display: flex;
    border-bottom: 1px solid var(--border-color);
}

.tab-btn {
    flex: 1;
    padding: 1rem 1.5rem;
    background: transparent;
    border: none;
    color: var(--text-secondary);
    cursor: pointer;
    transition: var(--transition);
    display: flex;
    align-items: center;
    gap: 0.5rem;
    justify-content: center;
}

.tab-btn:hover,
.tab-btn.active {
    background: var(--primary-light);
    color: var(--primary-color);
}

.tab-content {
    padding: 2rem;
}

.tab-pane {
    display: none;
}

.tab-pane.active {
    display: block;
}

.complaints-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
}

.complaints-filters {
    display: flex;
    gap: 1rem;
}

.filter-select {
    padding: 8px 12px;
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    background: var(--bg-primary);
    color: var(--text-primary);
}

.complaints-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.complaint-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1.5rem;
    background: var(--bg-tertiary);
    border-radius: var(--border-radius);
    transition: var(--transition);
}

.complaint-item:hover {
    background: var(--bg-primary);
}

.complaint-status {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.status-resolved {
    background: rgba(16, 185, 129, 0.1);
    color: var(--success-color);
}

.status-pending {
    background: rgba(245, 158, 11, 0.1);
    color: var(--warning-color);
}

.status-responded {
    background: rgba(6, 182, 212, 0.1);
    color: var(--accent-color);
}

.complaint-content {
    flex: 1;
}

.complaint-content h4 {
    font-weight: 600;
    margin-bottom: 0.5rem;
}

.complaint-content p {
    color: var(--text-secondary);
    margin-bottom: 0.75rem;
}

.complaint-meta {
    display: flex;
    gap: 1rem;
    font-size: 0.875rem;
    color: var(--text-muted);
}

.meta-item {
    display: flex;
    align-items: center;
    gap: 0.25rem;
}

.complaint-actions {
    display: flex;
    gap: 0.5rem;
}

.activity-timeline {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.timeline-item {
    display: flex;
    gap: 1rem;
}

.timeline-icon {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: var(--primary-light);
    color: var(--primary-color);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.timeline-icon.success {
    background: rgba(16, 185, 129, 0.1);
    color: var(--success-color);
}

.timeline-icon.warning {
    background: rgba(245, 158, 11, 0.1);
    color: var(--warning-color);
}

.timeline-content h4 {
    font-weight: 600;
    margin-bottom: 0.5rem;
}

.timeline-content p {
    color: var(--text-secondary);
    margin-bottom: 0.5rem;
}

.timeline-time {
    font-size: 0.875rem;
    color: var(--text-muted);
}

.empty-state {
    text-align: center;
    color: var(--text-muted);
    padding: 3rem;
}

.empty-state i {
    font-size: 3rem;
    margin-bottom: 1rem;
    display: block;
}

.settings-sections {
    display: flex;
    flex-direction: column;
    gap: 2rem;
}

.settings-section h4 {
    font-weight: 600;
    margin-bottom: 1rem;
}

.setting-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 0;
    border-bottom: 1px solid var(--border-color);
}

.setting-item:last-child {
    border-bottom: none;
}

.setting-info {
    display: flex;
    flex-direction: column;
}

.setting-label {
    font-weight: 500;
    margin-bottom: 0.25rem;
}

.setting-desc {
    font-size: 0.875rem;
    color: var(--text-secondary);
}

.toggle-switch {
    position: relative;
    width: 50px;
    height: 24px;
    cursor: pointer;
}

.toggle-switch input {
    opacity: 0;
    width: 0;
    height: 0;
}

.toggle-slider {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: var(--bg-tertiary);
    border-radius: 24px;
    transition: var(--transition);
}

.toggle-slider:before {
    position: absolute;
    content: "";
    height: 18px;
    width: 18px;
    left: 3px;
    bottom: 3px;
    background: white;
    border-radius: 50%;
    transition: var(--transition);
}

input:checked + .toggle-slider {
    background: var(--primary-color);
}

input:checked + .toggle-slider:before {
    transform: translateX(26px);
}

.setting-actions {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
}

.password-strength {
    margin-top: 0.5rem;
}

.strength-bar {
    height: 4px;
    background: var(--bg-tertiary);
    border-radius: 2px;
    overflow: hidden;
    margin-bottom: 0.5rem;
}

.strength-fill {
    height: 100%;
    transition: var(--transition);
}

.strength-text {
    font-size: 0.875rem;
    font-weight: 500;
}

.strength-feedback {
    font-size: 0.75rem;
    color: var(--text-muted);
    margin-top: 0.25rem;
}

/* Responsive */
@media (max-width: 1024px) {
    .profile-content {
        grid-template-columns: 1fr;
    }
    
    .profile-sidebar {
        order: 2;
    }
}

@media (max-width: 768px) {
    .profile-info {
        flex-direction: column;
        text-align: center;
    }
    
    .profile-stats {
        flex-direction: column;
        gap: 1rem;
    }
    
    .profile-tabs {
        flex-direction: column;
    }
    
    .complaints-header {
        flex-direction: column;
        gap: 1rem;
        align-items: stretch;
    }
    
    .complaints-filters {
        flex-direction: column;
    }
    
    .complaint-item {
        flex-direction: column;
        align-items: flex-start;
    }
    
    .setting-item {
        flex-direction: column;
        align-items: flex-start;
        gap: 1rem;
    }
    
    .setting-actions {
        flex-direction: column;
    }
}
`;

// Inject profile styles
const styleSheet = document.createElement('style');
styleSheet.textContent = profileStyles;
document.head.appendChild(styleSheet);

