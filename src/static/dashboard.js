// Dashboard specific functionality
class DashboardManager {
    constructor() {
        this.selectedLocation = null;
        this.uploadedImages = [];
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadDashboardData();
        this.animateStats();
    }

    setupEventListeners() {
        // Quick actions
        document.querySelectorAll('.action-card').forEach(card => {
            card.addEventListener('click', () => {
                const action = card.getAttribute('data-action');
                this.handleQuickAction(action);
            });
        });

        // New complaint button
        const newComplaintBtn = document.getElementById('new-complaint-btn');
        if (newComplaintBtn) {
            newComplaintBtn.addEventListener('click', () => {
                app.openModal('new-complaint-modal');
            });
        }

        // Filter tabs
        document.querySelectorAll('.filter-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                this.handleFilterChange(tab);
            });
        });

        // Vote buttons
        document.querySelectorAll('.vote-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.handleVote(btn);
            });
        });

        // New complaint form
        const complaintForm = document.getElementById('new-complaint-form');
        if (complaintForm) {
            complaintForm.addEventListener('submit', (e) => this.handleComplaintSubmission(e));
        }

        // Image upload
        this.setupImageUpload();

        // Map placeholder click
        const mapContainer = document.getElementById('complaint-map');
        if (mapContainer) {
            mapContainer.addEventListener('click', () => {
                this.openMapSelector();
            });
        }
    }

    handleQuickAction(action) {
        switch (action) {
            case 'new-complaint':
                app.openModal('new-complaint-modal');
                break;
            case 'view-complaints':
                window.location.href = 'complaints.html';
                break;
            case 'my-complaints':
                window.location.href = 'complaints.html?filter=mine';
                break;
            case 'map-view':
                window.location.href = 'map.html';
                break;
        }
    }

    handleFilterChange(activeTab) {
        // Remove active class from all tabs
        document.querySelectorAll('.filter-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        
        // Add active class to clicked tab
        activeTab.classList.add('active');
        
        // Filter complaints based on selection
        const filter = activeTab.getAttribute('data-filter');
        this.filterComplaints(filter);
    }

    filterComplaints(filter) {
        const complaints = document.querySelectorAll('.complaint-card');
        
        complaints.forEach(complaint => {
            let show = true;
            
            switch (filter) {
                case 'trending':
                    // Show complaints with high vote count
                    const voteCount = parseInt(complaint.querySelector('.vote-count').textContent);
                    show = voteCount > 20;
                    break;
                case 'urgent':
                    // Show urgent complaints
                    show = complaint.querySelector('.priority-high') !== null;
                    break;
                case 'all':
                default:
                    show = true;
                    break;
            }
            
            complaint.style.display = show ? 'block' : 'none';
        });
    }

    handleVote(button) {
        const isVoted = button.getAttribute('data-voted') === 'true';
        const voteCountElement = button.querySelector('.vote-count');
        const iconElement = button.querySelector('i');
        let currentCount = parseInt(voteCountElement.textContent);

        if (isVoted) {
            // Remove vote
            button.setAttribute('data-voted', 'false');
            iconElement.className = 'bi bi-heart';
            button.classList.remove('voted');
            voteCountElement.textContent = currentCount - 1;
            app.showToast('Voto removido', 'info');
        } else {
            // Add vote
            button.setAttribute('data-voted', 'true');
            iconElement.className = 'bi bi-heart-fill';
            button.classList.add('voted');
            voteCountElement.textContent = currentCount + 1;
            app.showToast('Voto adicionado!', 'success');
        }

        // In a real app, this would make an API call
        this.submitVote(button.closest('.complaint-card'), !isVoted);
    }

    async submitVote(complaintCard, isVoting) {
        // Simulate API call
        try {
            // const complaintId = complaintCard.getAttribute('data-complaint-id');
            // const response = await fetch(`/api/complaints/${complaintId}/vote`, {
            //     method: isVoting ? 'POST' : 'DELETE',
            //     headers: {
            //         'Authorization': `Bearer ${app.token}`,
            //         'Content-Type': 'application/json'
            //     }
            // });
            
            console.log('Vote submitted:', isVoting);
        } catch (error) {
            console.error('Error submitting vote:', error);
            app.showToast('Erro ao votar. Tente novamente.', 'error');
        }
    }

    setupImageUpload() {
        const uploadArea = document.getElementById('image-upload-area');
        const fileInput = document.getElementById('complaint-images');
        const previewGrid = document.getElementById('image-preview-grid');

        if (!uploadArea || !fileInput) return;

        // Click to upload
        uploadArea.addEventListener('click', (e) => {
            if (e.target.closest('.image-preview')) return;
            fileInput.click();
        });

        // Drag and drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('drag-over');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('drag-over');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
            
            const files = Array.from(e.dataTransfer.files);
            this.handleImageFiles(files);
        });

        // File input change
        fileInput.addEventListener('change', (e) => {
            const files = Array.from(e.target.files);
            this.handleImageFiles(files);
        });
    }

    handleImageFiles(files) {
        const maxFiles = 5;
        const maxSize = 10 * 1024 * 1024; // 10MB
        
        if (this.uploadedImages.length + files.length > maxFiles) {
            app.showToast(`Máximo ${maxFiles} imagens permitidas`, 'warning');
            return;
        }

        files.forEach(file => {
            if (!file.type.startsWith('image/')) {
                app.showToast('Apenas imagens são permitidas', 'error');
                return;
            }

            if (file.size > maxSize) {
                app.showToast('Imagem muito grande. Máximo 10MB', 'error');
                return;
            }

            this.addImagePreview(file);
        });
    }

    addImagePreview(file) {
        const previewGrid = document.getElementById('image-preview-grid');
        const reader = new FileReader();

        reader.onload = (e) => {
            const imageId = Date.now() + Math.random();
            const imageData = {
                id: imageId,
                file: file,
                url: e.target.result
            };

            this.uploadedImages.push(imageData);

            const previewElement = document.createElement('div');
            previewElement.className = 'image-preview';
            previewElement.setAttribute('data-image-id', imageId);
            previewElement.innerHTML = `
                <img src="${e.target.result}" alt="Preview">
                <button type="button" class="remove-image" onclick="dashboard.removeImage(${imageId})">
                    <i class="bi bi-x"></i>
                </button>
                <div class="image-info">
                    <span class="image-name">${file.name}</span>
                    <span class="image-size">${this.formatFileSize(file.size)}</span>
                </div>
            `;

            previewGrid.appendChild(previewElement);
            
            // Hide upload placeholder if images are present
            const placeholder = document.querySelector('.upload-placeholder');
            if (placeholder && this.uploadedImages.length > 0) {
                placeholder.style.display = 'none';
            }
        };

        reader.readAsDataURL(file);
    }

    removeImage(imageId) {
        // Remove from array
        this.uploadedImages = this.uploadedImages.filter(img => img.id !== imageId);
        
        // Remove from DOM
        const previewElement = document.querySelector(`[data-image-id="${imageId}"]`);
        if (previewElement) {
            previewElement.remove();
        }

        // Show placeholder if no images
        const placeholder = document.querySelector('.upload-placeholder');
        if (placeholder && this.uploadedImages.length === 0) {
            placeholder.style.display = 'block';
        }
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    openMapSelector() {
        // In a real implementation, this would open a map modal
        app.showToast('Funcionalidade de mapa será implementada em breve', 'info');
        
        // Simulate location selection
        setTimeout(() => {
            this.selectedLocation = {
                lat: -15.6014,
                lng: -56.0979,
                address: 'Centro, Cuiabá - MT'
            };
            
            const mapContainer = document.getElementById('complaint-map');
            mapContainer.innerHTML = `
                <div class="map-selected">
                    <i class="bi bi-geo-alt-fill"></i>
                    <div class="location-info">
                        <strong>Localização Selecionada</strong>
                        <p>${this.selectedLocation.address}</p>
                    </div>
                    <button type="button" class="btn btn-small btn-outline" onclick="dashboard.openMapSelector()">
                        Alterar
                    </button>
                </div>
            `;
            
            app.showToast('Localização selecionada!', 'success');
        }, 1000);
    }

    async handleComplaintSubmission(e) {
        e.preventDefault();
        
        const form = e.target;
        const formData = new FormData(form);
        
        // Validate required fields
        const title = formData.get('title');
        const category = formData.get('category');
        const description = formData.get('description');
        
        if (!title || !category || !description) {
            app.showToast('Por favor, preencha todos os campos obrigatórios', 'error');
            return;
        }

        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Enviando...';
        submitBtn.disabled = true;

        try {
            // Prepare complaint data
            const complaintData = {
                title: title,
                category: category,
                description: description,
                address: formData.get('address'),
                priority: formData.get('priority') || 'normal',
                location: this.selectedLocation,
                images: this.uploadedImages
            };

            // Simulate API call
            await this.submitComplaint(complaintData);
            
            app.showToast('Reclamação enviada com sucesso!', 'success');
            app.closeModal('new-complaint-modal');
            form.reset();
            this.resetForm();
            
            // Refresh dashboard data
            this.loadDashboardData();
            
        } catch (error) {
            console.error('Error submitting complaint:', error);
            app.showToast('Erro ao enviar reclamação. Tente novamente.', 'error');
        } finally {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    }

    async submitComplaint(complaintData) {
        // In a real implementation, this would make an API call
        return new Promise((resolve) => {
            setTimeout(() => {
                console.log('Complaint submitted:', complaintData);
                resolve({ success: true });
            }, 2000);
        });
    }

    resetForm() {
        // Clear uploaded images
        this.uploadedImages = [];
        this.selectedLocation = null;
        
        // Reset image preview
        const previewGrid = document.getElementById('image-preview-grid');
        if (previewGrid) {
            previewGrid.innerHTML = '';
        }
        
        // Show upload placeholder
        const placeholder = document.querySelector('.upload-placeholder');
        if (placeholder) {
            placeholder.style.display = 'block';
        }
        
        // Reset map
        const mapContainer = document.getElementById('complaint-map');
        if (mapContainer) {
            mapContainer.innerHTML = `
                <div class="map-placeholder">
                    <i class="bi bi-geo-alt"></i>
                    <p>Mapa será carregado aqui</p>
                    <small>Clique para selecionar a localização exata</small>
                </div>
            `;
        }
    }

    async loadDashboardData() {
        try {
            // In a real implementation, this would fetch data from the API
            // const response = await fetch('/api/dashboard', {
            //     headers: {
            //         'Authorization': `Bearer ${app.token}`,
            //         'Content-Type': 'application/json'
            //     }
            // });
            
            // Simulate loading data
            console.log('Loading dashboard data...');
            
        } catch (error) {
            console.error('Error loading dashboard data:', error);
        }
    }

    animateStats() {
        const stats = document.querySelectorAll('.stat-number');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const stat = entry.target;
                    const target = parseInt(stat.getAttribute('data-count'));
                    const duration = 1500;
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
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new DashboardManager();
});

// CSS for dashboard-specific styles
const dashboardStyles = `
/* Dashboard Styles */
.dashboard-main {
    padding-top: 90px;
    min-height: 100vh;
    background: var(--bg-primary);
}

.dashboard-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 3rem;
    padding: 2rem 0;
}

.header-content h1 {
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
}

.header-content p {
    color: var(--text-secondary);
    font-size: 1.125rem;
}

/* Stats Grid */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    margin-bottom: 3rem;
}

.stat-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-lg);
    padding: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    transition: var(--transition);
}

.stat-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
}

.stat-icon {
    width: 60px;
    height: 60px;
    background: var(--primary-light);
    border-radius: var(--border-radius);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    color: var(--primary-color);
}

.stat-icon.success {
    background: rgba(16, 185, 129, 0.1);
    color: var(--success-color);
}

.stat-icon.warning {
    background: rgba(245, 158, 11, 0.1);
    color: var(--warning-color);
}

.stat-icon.info {
    background: rgba(6, 182, 212, 0.1);
    color: var(--accent-color);
}

.stat-number {
    font-size: 2rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 0.25rem;
}

.stat-label {
    color: var(--text-secondary);
    font-size: 0.875rem;
}

/* Quick Actions */
.quick-actions {
    margin-bottom: 3rem;
}

.quick-actions h2 {
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: 1.5rem;
}

.actions-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
}

.action-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-lg);
    padding: 1.5rem;
    text-align: center;
    cursor: pointer;
    transition: var(--transition);
}

.action-card:hover {
    transform: translateY(-5px);
    box-shadow: var(--shadow-lg);
    border-color: var(--primary-color);
}

.action-icon {
    width: 80px;
    height: 80px;
    background: var(--gradient-primary);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 1rem;
    font-size: 2rem;
    color: white;
}

.action-card h3 {
    font-size: 1.125rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
}

.action-card p {
    color: var(--text-secondary);
    font-size: 0.875rem;
}

/* Recent Activity */
.recent-activity {
    margin-bottom: 3rem;
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
}

.section-header h2 {
    font-size: 1.5rem;
    font-weight: 600;
}

.view-all-link {
    color: var(--primary-color);
    text-decoration: none;
    font-weight: 500;
}

.view-all-link:hover {
    text-decoration: underline;
}

.activity-list {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-lg);
    overflow: hidden;
}

.activity-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem 1.5rem;
    border-bottom: 1px solid var(--border-color);
    transition: var(--transition);
}

.activity-item:last-child {
    border-bottom: none;
}

.activity-item:hover {
    background: var(--bg-tertiary);
}

.activity-icon {
    width: 40px;
    height: 40px;
    background: var(--primary-light);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--primary-color);
    flex-shrink: 0;
}

.activity-icon.success {
    background: rgba(16, 185, 129, 0.1);
    color: var(--success-color);
}

.activity-icon.warning {
    background: rgba(245, 158, 11, 0.1);
    color: var(--warning-color);
}

.activity-content {
    flex: 1;
}

.activity-title {
    font-weight: 500;
    margin-bottom: 0.25rem;
}

.activity-meta {
    display: flex;
    align-items: center;
    gap: 1rem;
    font-size: 0.875rem;
}

.activity-status {
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 500;
}

.status-pending {
    background: rgba(245, 158, 11, 0.1);
    color: var(--warning-color);
}

.status-resolved {
    background: rgba(16, 185, 129, 0.1);
    color: var(--success-color);
}

.status-responded {
    background: rgba(6, 182, 212, 0.1);
    color: var(--accent-color);
}

.activity-time {
    color: var(--text-muted);
}

/* Trending Section */
.trending-section {
    margin-bottom: 3rem;
}

.filter-tabs {
    display: flex;
    gap: 0.5rem;
}

.filter-tab {
    padding: 8px 16px;
    background: transparent;
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    color: var(--text-secondary);
    cursor: pointer;
    transition: var(--transition);
}

.filter-tab:hover,
.filter-tab.active {
    background: var(--primary-color);
    border-color: var(--primary-color);
    color: white;
}

.complaints-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 1.5rem;
}

.complaint-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-lg);
    overflow: hidden;
    transition: var(--transition);
}

.complaint-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
}

.complaint-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 1.5rem;
    border-bottom: 1px solid var(--border-color);
}

.complaint-user {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.complaint-user img {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    object-fit: cover;
}

.user-info {
    display: flex;
    flex-direction: column;
}

.user-name {
    font-weight: 500;
    font-size: 0.875rem;
}

.user-badge {
    font-size: 0.75rem;
    color: var(--text-muted);
}

.complaint-priority {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.875rem;
}

.priority-high {
    background: rgba(239, 68, 68, 0.1);
    color: var(--error-color);
}

.priority-normal {
    background: rgba(6, 182, 212, 0.1);
    color: var(--accent-color);
}

.complaint-content {
    padding: 1.5rem;
}

.complaint-content h3 {
    font-size: 1.125rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
}

.complaint-content p {
    color: var(--text-secondary);
    margin-bottom: 1rem;
    line-height: 1.5;
}

.complaint-image {
    border-radius: var(--border-radius);
    overflow: hidden;
    margin-top: 1rem;
}

.complaint-image img {
    width: 100%;
    height: 200px;
    object-fit: cover;
}

.complaint-footer {
    padding: 1rem 1.5rem;
    border-top: 1px solid var(--border-color);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.complaint-meta {
    display: flex;
    align-items: center;
    gap: 1rem;
    font-size: 0.875rem;
}

.location {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    color: var(--text-muted);
}

.complaint-actions {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.vote-btn,
.comment-btn,
.share-btn {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    padding: 6px 12px;
    background: transparent;
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    color: var(--text-secondary);
    cursor: pointer;
    transition: var(--transition);
    font-size: 0.875rem;
}

.vote-btn:hover,
.comment-btn:hover,
.share-btn:hover {
    background: var(--bg-tertiary);
    color: var(--text-primary);
}

.vote-btn.voted {
    background: rgba(239, 68, 68, 0.1);
    border-color: var(--error-color);
    color: var(--error-color);
}

/* Large Modal */
.large-modal {
    max-width: 800px;
    width: 95%;
}

/* Map Container */
.map-container {
    height: 200px;
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    overflow: hidden;
    cursor: pointer;
    transition: var(--transition);
}

.map-container:hover {
    border-color: var(--primary-color);
}

.map-placeholder {
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: var(--bg-tertiary);
    color: var(--text-muted);
    text-align: center;
}

.map-placeholder i {
    font-size: 2rem;
    margin-bottom: 0.5rem;
    color: var(--primary-color);
}

.map-selected {
    height: 100%;
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    background: var(--primary-light);
}

.map-selected i {
    font-size: 2rem;
    color: var(--primary-color);
}

.location-info strong {
    display: block;
    margin-bottom: 0.25rem;
}

/* Image Upload */
.image-upload-area {
    border: 2px dashed var(--border-color);
    border-radius: var(--border-radius);
    padding: 2rem;
    text-align: center;
    cursor: pointer;
    transition: var(--transition);
}

.image-upload-area:hover,
.image-upload-area.drag-over {
    border-color: var(--primary-color);
    background: var(--primary-light);
}

.upload-placeholder i {
    font-size: 3rem;
    color: var(--primary-color);
    margin-bottom: 1rem;
}

.image-preview-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 1rem;
    margin-top: 1rem;
}

.image-preview {
    position: relative;
    border-radius: var(--border-radius);
    overflow: hidden;
    background: var(--bg-tertiary);
}

.image-preview img {
    width: 100%;
    height: 120px;
    object-fit: cover;
}

.remove-image {
    position: absolute;
    top: 8px;
    right: 8px;
    width: 24px;
    height: 24px;
    background: rgba(0, 0, 0, 0.7);
    border: none;
    border-radius: 50%;
    color: white;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.875rem;
}

.image-info {
    padding: 0.5rem;
    font-size: 0.75rem;
}

.image-name {
    display: block;
    font-weight: 500;
    margin-bottom: 0.25rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.image-size {
    color: var(--text-muted);
}

.field-help {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-top: 0.5rem;
    font-size: 0.875rem;
    color: var(--text-muted);
}

/* Responsive */
@media (max-width: 768px) {
    .dashboard-header {
        flex-direction: column;
        gap: 1rem;
        text-align: center;
    }
    
    .stats-grid {
        grid-template-columns: 1fr;
    }
    
    .actions-grid {
        grid-template-columns: 1fr;
    }
    
    .complaints-grid {
        grid-template-columns: 1fr;
    }
    
    .complaint-footer {
        flex-direction: column;
        gap: 1rem;
        align-items: flex-start;
    }
    
    .large-modal {
        width: 98%;
        margin: 1rem;
    }
}
`;

// Inject dashboard styles
const styleSheet = document.createElement('style');
styleSheet.textContent = dashboardStyles;
document.head.appendChild(styleSheet);

