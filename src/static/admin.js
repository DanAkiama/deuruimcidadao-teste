// Admin panel functionality
class AdminManager {
    constructor() {
        this.currentSection = 'dashboard';
        this.currentPage = 1;
        this.itemsPerPage = 20;
        this.selectedComplaints = new Set();
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadDashboardData();
        this.animateStats();
        this.setupCharts();
        this.loadComplaintsData();
        this.loadUsersData();
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const href = link.getAttribute('href');
                if (href.startsWith('#')) {
                    const sectionId = href.substring(1);
                    this.switchSection(sectionId.replace('-section', ''));
                }
            });
        });

        // City selector
        const citySelect = document.getElementById('admin-city-select');
        if (citySelect) {
            citySelect.addEventListener('change', () => {
                this.handleCityChange(citySelect.value);
            });
        }

        // Refresh data button
        const refreshBtn = document.getElementById('refresh-data-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.refreshAllData();
            });
        }

        // Export report button
        const exportReportBtn = document.getElementById('export-report-btn');
        if (exportReportBtn) {
            exportReportBtn.addEventListener('click', () => {
                this.exportReport();
            });
        }

        // Complaints search
        const complaintsSearch = document.getElementById('complaints-search');
        if (complaintsSearch) {
            complaintsSearch.addEventListener('input', (e) => {
                this.searchComplaints(e.target.value);
            });
        }

        // Filters
        const filters = ['status-filter', 'category-filter', 'priority-filter', 'assignee-filter'];
        filters.forEach(filterId => {
            const filter = document.getElementById(filterId);
            if (filter) {
                filter.addEventListener('change', () => {
                    this.applyFilters();
                });
            }
        });

        // Date filters
        const dateFrom = document.getElementById('date-from');
        const dateTo = document.getElementById('date-to');
        if (dateFrom && dateTo) {
            dateFrom.addEventListener('change', () => this.applyFilters());
            dateTo.addEventListener('change', () => this.applyFilters());
        }

        // Select all complaints
        const selectAllCheckbox = document.getElementById('select-all-complaints');
        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', (e) => {
                this.toggleSelectAll(e.target.checked);
            });
        }

        // Bulk actions
        const bulkActionsBtn = document.getElementById('bulk-actions-btn');
        if (bulkActionsBtn) {
            bulkActionsBtn.addEventListener('click', () => {
                this.showBulkActions();
            });
        }

        // Assign complaint button
        const assignBtn = document.getElementById('assign-complaint-btn');
        if (assignBtn) {
            assignBtn.addEventListener('click', () => {
                app.openModal('assign-modal');
            });
        }

        // Assign form
        const assignForm = document.getElementById('assign-form');
        if (assignForm) {
            assignForm.addEventListener('submit', (e) => {
                this.handleAssignComplaint(e);
            });
        }

        // Pagination
        const prevPageBtn = document.getElementById('prev-page');
        const nextPageBtn = document.getElementById('next-page');
        if (prevPageBtn && nextPageBtn) {
            prevPageBtn.addEventListener('click', () => this.changePage(this.currentPage - 1));
            nextPageBtn.addEventListener('click', () => this.changePage(this.currentPage + 1));
        }

        // Chart period selectors
        const categoryPeriod = document.getElementById('category-period');
        const resolutionPeriod = document.getElementById('resolution-period');
        if (categoryPeriod) {
            categoryPeriod.addEventListener('change', () => {
                this.updateCategoryChart(categoryPeriod.value);
            });
        }
        if (resolutionPeriod) {
            resolutionPeriod.addEventListener('change', () => {
                this.updateResolutionChart(resolutionPeriod.value);
            });
        }

        // Map filters
        const mapFilters = ['map-filter-all', 'map-filter-urgent', 'map-filter-pending'];
        mapFilters.forEach(filterId => {
            const filter = document.getElementById(filterId);
            if (filter) {
                filter.addEventListener('click', () => {
                    this.updateMapFilter(filterId.replace('map-filter-', ''));
                });
            }
        });

        // Generate report button
        const generateReportBtn = document.getElementById('generate-report-btn');
        if (generateReportBtn) {
            generateReportBtn.addEventListener('click', () => {
                this.generateReport();
            });
        }

        // Export users button
        const exportUsersBtn = document.getElementById('export-users-btn');
        if (exportUsersBtn) {
            exportUsersBtn.addEventListener('click', () => {
                this.exportUsers();
            });
        }

        // Invite user button
        const inviteUserBtn = document.getElementById('invite-user-btn');
        if (inviteUserBtn) {
            inviteUserBtn.addEventListener('click', () => {
                this.inviteUser();
            });
        }
    }

    switchSection(sectionName) {
        // Update navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        document.querySelector(`[href="#${sectionName}-section"]`).classList.add('active');

        // Update sections
        document.querySelectorAll('.admin-section').forEach(section => {
            section.classList.remove('active');
        });
        document.getElementById(`${sectionName}-section`).classList.add('active');

        this.currentSection = sectionName;

        // Load section-specific data
        this.loadSectionData(sectionName);
    }

    async loadSectionData(sectionName) {
        switch (sectionName) {
            case 'dashboard':
                await this.loadDashboardData();
                break;
            case 'complaints':
                await this.loadComplaintsData();
                break;
            case 'users':
                await this.loadUsersData();
                break;
            case 'reports':
                await this.loadReportsData();
                break;
            case 'settings':
                await this.loadSettingsData();
                break;
        }
    }

    async loadDashboardData() {
        try {
            // Simulate API call
            console.log('Loading dashboard data...');
            
            // Update stats with animation
            this.animateStats();
            
            // Update charts
            this.updateCharts();
            
        } catch (error) {
            console.error('Error loading dashboard data:', error);
        }
    }

    async loadComplaintsData() {
        try {
            console.log('Loading complaints data...');
            
            // Simulate loading complaints
            const complaintsData = this.generateMockComplaints();
            this.renderComplaintsTable(complaintsData);
            this.updatePagination(complaintsData.length);
            
        } catch (error) {
            console.error('Error loading complaints data:', error);
        }
    }

    async loadUsersData() {
        try {
            console.log('Loading users data...');
            
            // Simulate loading users
            const usersData = this.generateMockUsers();
            this.renderUsersTable(usersData);
            
        } catch (error) {
            console.error('Error loading users data:', error);
        }
    }

    async loadReportsData() {
        try {
            console.log('Loading reports data...');
        } catch (error) {
            console.error('Error loading reports data:', error);
        }
    }

    async loadSettingsData() {
        try {
            console.log('Loading settings data...');
        } catch (error) {
            console.error('Error loading settings data:', error);
        }
    }

    generateMockComplaints() {
        const complaints = [];
        const categories = ['buracos', 'iluminacao', 'limpeza', 'transito', 'seguranca'];
        const statuses = ['pending', 'in-progress', 'resolved', 'urgent'];
        const priorities = ['low', 'medium', 'high', 'urgent'];
        const locations = ['Centro', 'Jardim Europa', 'Cidade Verde', 'Porto', 'Alvorada'];
        const citizens = ['Maria Silva', 'João Santos', 'Ana Costa', 'Pedro Lima', 'Carla Souza'];

        for (let i = 1; i <= 50; i++) {
            complaints.push({
                id: `#${String(i).padStart(4, '0')}`,
                title: `Reclamação ${i}`,
                category: categories[Math.floor(Math.random() * categories.length)],
                status: statuses[Math.floor(Math.random() * statuses.length)],
                priority: priorities[Math.floor(Math.random() * priorities.length)],
                citizen: citizens[Math.floor(Math.random() * citizens.length)],
                location: locations[Math.floor(Math.random() * locations.length)],
                date: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toLocaleDateString('pt-BR'),
                assignee: Math.random() > 0.3 ? 'Equipe de Manutenção' : 'Não atribuída'
            });
        }

        return complaints;
    }

    generateMockUsers() {
        const users = [];
        const names = ['Maria Silva', 'João Santos', 'Ana Costa', 'Pedro Lima', 'Carla Souza'];
        const types = ['Cidadão', 'Gestor Público'];
        const cities = ['Cuiabá', 'Várzea Grande'];
        const statuses = ['Ativo', 'Inativo'];

        for (let i = 1; i <= 20; i++) {
            const name = names[Math.floor(Math.random() * names.length)];
            users.push({
                id: i,
                name: `${name} ${i}`,
                email: `${name.toLowerCase().replace(' ', '.')}${i}@email.com`,
                type: types[Math.floor(Math.random() * types.length)],
                city: cities[Math.floor(Math.random() * cities.length)],
                complaints: Math.floor(Math.random() * 20),
                lastActivity: `${Math.floor(Math.random() * 30)} dias atrás`,
                status: statuses[Math.floor(Math.random() * statuses.length)],
                avatar: `https://via.placeholder.com/40x40/6366f1/ffffff?text=${name.charAt(0)}`
            });
        }

        return users;
    }

    renderComplaintsTable(complaints) {
        const tbody = document.getElementById('complaints-table-body');
        if (!tbody) return;

        tbody.innerHTML = '';

        complaints.slice((this.currentPage - 1) * this.itemsPerPage, this.currentPage * this.itemsPerPage).forEach(complaint => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>
                    <input type="checkbox" class="complaint-checkbox" data-id="${complaint.id}">
                </td>
                <td>${complaint.id}</td>
                <td>
                    <div class="complaint-title">
                        ${complaint.title}
                        ${complaint.priority === 'urgent' ? '<span class="urgent-badge">URGENTE</span>' : ''}
                    </div>
                </td>
                <td>
                    <span class="category-badge category-${complaint.category}">
                        ${this.getCategoryName(complaint.category)}
                    </span>
                </td>
                <td>
                    <span class="status-badge status-${complaint.status}">
                        ${this.getStatusName(complaint.status)}
                    </span>
                </td>
                <td>
                    <span class="priority-badge priority-${complaint.priority}">
                        ${this.getPriorityName(complaint.priority)}
                    </span>
                </td>
                <td>${complaint.citizen}</td>
                <td>${complaint.location}</td>
                <td>${complaint.date}</td>
                <td>${complaint.assignee}</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-small btn-outline" onclick="adminManager.viewComplaint('${complaint.id}')">
                            <i class="bi bi-eye"></i>
                        </button>
                        <button class="btn btn-small btn-primary" onclick="adminManager.editComplaint('${complaint.id}')">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-small btn-success" onclick="adminManager.resolveComplaint('${complaint.id}')">
                            <i class="bi bi-check"></i>
                        </button>
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });

        // Add event listeners to checkboxes
        document.querySelectorAll('.complaint-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                const complaintId = e.target.getAttribute('data-id');
                if (e.target.checked) {
                    this.selectedComplaints.add(complaintId);
                } else {
                    this.selectedComplaints.delete(complaintId);
                }
                this.updateBulkActionsButton();
            });
        });
    }

    renderUsersTable(users) {
        const tbody = document.getElementById('users-table-body');
        if (!tbody) return;

        tbody.innerHTML = '';

        users.forEach(user => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>
                    <img src="${user.avatar}" alt="${user.name}" class="user-avatar-small">
                </td>
                <td>${user.name}</td>
                <td>${user.email}</td>
                <td>
                    <span class="type-badge type-${user.type.toLowerCase().replace(' ', '-')}">
                        ${user.type}
                    </span>
                </td>
                <td>${user.city}</td>
                <td>${user.complaints}</td>
                <td>${user.lastActivity}</td>
                <td>
                    <span class="status-badge status-${user.status.toLowerCase()}">
                        ${user.status}
                    </span>
                </td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-small btn-outline" onclick="adminManager.viewUser(${user.id})">
                            <i class="bi bi-eye"></i>
                        </button>
                        <button class="btn btn-small btn-primary" onclick="adminManager.editUser(${user.id})">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-small btn-danger" onclick="adminManager.suspendUser(${user.id})">
                            <i class="bi bi-ban"></i>
                        </button>
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    getCategoryName(category) {
        const names = {
            'buracos': 'Buracos',
            'iluminacao': 'Iluminação',
            'limpeza': 'Limpeza',
            'transito': 'Trânsito',
            'seguranca': 'Segurança'
        };
        return names[category] || category;
    }

    getStatusName(status) {
        const names = {
            'pending': 'Pendente',
            'in-progress': 'Em Andamento',
            'resolved': 'Resolvida',
            'urgent': 'Urgente'
        };
        return names[status] || status;
    }

    getPriorityName(priority) {
        const names = {
            'low': 'Baixa',
            'medium': 'Média',
            'high': 'Alta',
            'urgent': 'Urgente'
        };
        return names[priority] || priority;
    }

    updatePagination(totalItems) {
        const totalPages = Math.ceil(totalItems / this.itemsPerPage);
        const showingFrom = (this.currentPage - 1) * this.itemsPerPage + 1;
        const showingTo = Math.min(this.currentPage * this.itemsPerPage, totalItems);

        // Update info
        document.getElementById('showing-from').textContent = showingFrom;
        document.getElementById('showing-to').textContent = showingTo;
        document.getElementById('total-complaints').textContent = totalItems;

        // Update pagination buttons
        const prevBtn = document.getElementById('prev-page');
        const nextBtn = document.getElementById('next-page');
        
        if (prevBtn) prevBtn.disabled = this.currentPage === 1;
        if (nextBtn) nextBtn.disabled = this.currentPage === totalPages;

        // Generate page numbers
        const pagesContainer = document.getElementById('pagination-pages');
        if (pagesContainer) {
            pagesContainer.innerHTML = '';
            
            for (let i = 1; i <= Math.min(totalPages, 5); i++) {
                const pageBtn = document.createElement('button');
                pageBtn.className = `pagination-btn ${i === this.currentPage ? 'active' : ''}`;
                pageBtn.textContent = i;
                pageBtn.addEventListener('click', () => this.changePage(i));
                pagesContainer.appendChild(pageBtn);
            }
        }
    }

    changePage(page) {
        this.currentPage = page;
        this.loadComplaintsData();
    }

    toggleSelectAll(checked) {
        document.querySelectorAll('.complaint-checkbox').forEach(checkbox => {
            checkbox.checked = checked;
            const complaintId = checkbox.getAttribute('data-id');
            if (checked) {
                this.selectedComplaints.add(complaintId);
            } else {
                this.selectedComplaints.delete(complaintId);
            }
        });
        this.updateBulkActionsButton();
    }

    updateBulkActionsButton() {
        const bulkBtn = document.getElementById('bulk-actions-btn');
        if (bulkBtn) {
            const count = this.selectedComplaints.size;
            if (count > 0) {
                bulkBtn.innerHTML = `<i class="bi bi-check2-square"></i> Ações em Lote (${count})`;
                bulkBtn.disabled = false;
            } else {
                bulkBtn.innerHTML = '<i class="bi bi-check2-square"></i> Ações em Lote';
                bulkBtn.disabled = true;
            }
        }
    }

    applyFilters() {
        console.log('Applying filters...');
        // In a real implementation, this would filter the data and reload the table
        this.loadComplaintsData();
    }

    searchComplaints(query) {
        console.log('Searching complaints:', query);
        // In a real implementation, this would search the data and reload the table
    }

    handleCityChange(city) {
        console.log('City changed to:', city);
        // Reload all data for the selected city
        this.refreshAllData();
    }

    async refreshAllData() {
        const refreshBtn = document.getElementById('refresh-data-btn');
        if (refreshBtn) {
            const originalText = refreshBtn.innerHTML;
            refreshBtn.innerHTML = '<i class="bi bi-arrow-clockwise spin"></i> Atualizando...';
            refreshBtn.disabled = true;

            try {
                await this.loadSectionData(this.currentSection);
                app.showToast('Dados atualizados com sucesso!', 'success');
            } catch (error) {
                app.showToast('Erro ao atualizar dados', 'error');
            } finally {
                refreshBtn.innerHTML = originalText;
                refreshBtn.disabled = false;
            }
        }
    }

    viewComplaint(id) {
        console.log('Viewing complaint:', id);
        // In a real implementation, this would load complaint details and show modal
        app.openModal('complaint-detail-modal');
    }

    editComplaint(id) {
        console.log('Editing complaint:', id);
        // In a real implementation, this would open edit modal
    }

    resolveComplaint(id) {
        console.log('Resolving complaint:', id);
        // In a real implementation, this would update complaint status
        app.showToast('Reclamação marcada como resolvida!', 'success');
    }

    viewUser(id) {
        console.log('Viewing user:', id);
    }

    editUser(id) {
        console.log('Editing user:', id);
    }

    suspendUser(id) {
        console.log('Suspending user:', id);
        if (confirm('Tem certeza que deseja suspender este usuário?')) {
            app.showToast('Usuário suspenso com sucesso!', 'success');
        }
    }

    async handleAssignComplaint(e) {
        e.preventDefault();
        
        const form = e.target;
        const formData = new FormData(form);
        const submitBtn = form.querySelector('button[type="submit"]');
        
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Atribuindo...';
        submitBtn.disabled = true;

        try {
            // Simulate API call
            await new Promise(resolve => setTimeout(resolve, 1500));
            
            app.showToast('Reclamação atribuída com sucesso!', 'success');
            app.closeModal('assign-modal');
            form.reset();
            this.loadComplaintsData();
            
        } catch (error) {
            console.error('Error assigning complaint:', error);
            app.showToast('Erro ao atribuir reclamação', 'error');
        } finally {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    }

    showBulkActions() {
        if (this.selectedComplaints.size === 0) {
            app.showToast('Selecione pelo menos uma reclamação', 'warning');
            return;
        }

        const actions = [
            'Marcar como resolvidas',
            'Atribuir responsável',
            'Alterar prioridade',
            'Exportar selecionadas'
        ];

        // In a real implementation, this would show a dropdown or modal with bulk actions
        console.log('Bulk actions for:', Array.from(this.selectedComplaints));
    }

    exportReport() {
        console.log('Exporting report...');
        app.showToast('Relatório exportado com sucesso!', 'success');
    }

    generateReport() {
        console.log('Generating report...');
        app.showToast('Relatório sendo gerado...', 'info');
    }

    exportUsers() {
        console.log('Exporting users...');
        app.showToast('Lista de usuários exportada!', 'success');
    }

    inviteUser() {
        console.log('Inviting user...');
        // In a real implementation, this would open an invite modal
    }

    animateStats() {
        const stats = document.querySelectorAll('.stat-number');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const stat = entry.target;
                    const target = parseFloat(stat.getAttribute('data-count'));
                    const duration = 2000;
                    const step = target / (duration / 16);
                    let current = 0;

                    const timer = setInterval(() => {
                        current += step;
                        if (current >= target) {
                            current = target;
                            clearInterval(timer);
                        }
                        
                        // Handle decimal numbers
                        if (target % 1 !== 0) {
                            stat.textContent = current.toFixed(1);
                        } else {
                            stat.textContent = Math.floor(current);
                        }
                    }, 16);
                    
                    observer.unobserve(stat);
                }
            });
        }, { threshold: 0.5 });

        stats.forEach(stat => observer.observe(stat));
    }

    setupCharts() {
        // In a real implementation, this would set up Chart.js or similar
        console.log('Setting up charts...');
    }

    updateCharts() {
        console.log('Updating charts...');
    }

    updateCategoryChart(period) {
        console.log('Updating category chart for period:', period);
    }

    updateResolutionChart(period) {
        console.log('Updating resolution chart for period:', period);
    }

    updateMapFilter(filter) {
        console.log('Updating map filter:', filter);
        
        // Update active button
        document.querySelectorAll('[id^="map-filter-"]').forEach(btn => {
            btn.classList.remove('active');
        });
        document.getElementById(`map-filter-${filter}`).classList.add('active');
    }
}

// Initialize admin manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.adminManager = new AdminManager();
});

// CSS for admin-specific styles
const adminStyles = `
/* Admin Styles */
.admin-navbar {
    background: var(--bg-card);
    border-bottom: 1px solid var(--border-color);
    padding: 1rem 0;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 1000;
}

.admin-navbar .nav-brand {
    color: var(--danger-color);
    font-weight: 700;
}

.admin-main {
    padding-top: 90px;
    min-height: 100vh;
    background: var(--bg-primary);
}

.admin-section {
    display: none;
    padding: 2rem 0;
}

.admin-section.active {
    display: block;
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
}

.section-header h1 {
    font-size: 2rem;
    font-weight: 700;
}

.header-actions {
    display: flex;
    gap: 1rem;
}

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
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.stat-card.urgent {
    border-left: 4px solid var(--danger-color);
}

.stat-card.pending {
    border-left: 4px solid var(--warning-color);
}

.stat-card.in-progress {
    border-left: 4px solid var(--accent-color);
}

.stat-card.resolved {
    border-left: 4px solid var(--success-color);
}

.stat-card.users {
    border-left: 4px solid var(--primary-color);
}

.stat-card.satisfaction {
    border-left: 4px solid var(--purple-color);
}

.stat-icon {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    flex-shrink: 0;
}

.urgent .stat-icon {
    background: rgba(239, 68, 68, 0.1);
    color: var(--danger-color);
}

.pending .stat-icon {
    background: rgba(245, 158, 11, 0.1);
    color: var(--warning-color);
}

.in-progress .stat-icon {
    background: rgba(6, 182, 212, 0.1);
    color: var(--accent-color);
}

.resolved .stat-icon {
    background: rgba(16, 185, 129, 0.1);
    color: var(--success-color);
}

.users .stat-icon {
    background: var(--primary-light);
    color: var(--primary-color);
}

.satisfaction .stat-icon {
    background: rgba(147, 51, 234, 0.1);
    color: var(--purple-color);
}

.stat-content {
    flex: 1;
}

.stat-number {
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 0.25rem;
}

.stat-label {
    color: var(--text-secondary);
    font-size: 0.875rem;
    margin-bottom: 0.5rem;
}

.stat-change {
    font-size: 0.75rem;
    font-weight: 500;
}

.stat-change.positive {
    color: var(--success-color);
}

.stat-change.negative {
    color: var(--danger-color);
}

.analytics-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
    margin-bottom: 3rem;
}

.chart-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-lg);
    overflow: hidden;
}

.chart-card:last-child {
    grid-column: 1 / -1;
}

.chart-header {
    padding: 1.5rem;
    border-bottom: 1px solid var(--border-color);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.chart-header h3 {
    font-weight: 600;
}

.chart-content {
    padding: 1.5rem;
    height: 300px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.map-placeholder {
    text-align: center;
    color: var(--text-muted);
}

.map-placeholder i {
    font-size: 3rem;
    margin-bottom: 1rem;
    display: block;
}

.map-controls {
    display: flex;
    gap: 0.5rem;
}

.activity-section {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-lg);
    padding: 1.5rem;
}

.activity-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
}

.activity-list {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.activity-item {
    display: flex;
    gap: 1rem;
    padding: 1rem;
    border-radius: var(--border-radius);
    transition: var(--transition);
}

.activity-item.urgent {
    background: rgba(239, 68, 68, 0.05);
    border-left: 3px solid var(--danger-color);
}

.activity-item.resolved {
    background: rgba(16, 185, 129, 0.05);
    border-left: 3px solid var(--success-color);
}

.activity-item.in-progress {
    background: rgba(6, 182, 212, 0.05);
    border-left: 3px solid var(--accent-color);
}

.activity-icon {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.activity-content {
    flex: 1;
}

.activity-content h4 {
    font-weight: 600;
    margin-bottom: 0.5rem;
}

.activity-content p {
    color: var(--text-secondary);
    margin-bottom: 0.75rem;
}

.activity-meta {
    display: flex;
    gap: 1rem;
    font-size: 0.875rem;
    color: var(--text-muted);
    flex-wrap: wrap;
}

.meta-item {
    display: flex;
    align-items: center;
    gap: 0.25rem;
}

.activity-actions {
    display: flex;
    gap: 0.5rem;
    align-items: flex-start;
}

.filters-section {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-lg);
    padding: 1.5rem;
    margin-bottom: 2rem;
}

.search-box {
    position: relative;
    margin-bottom: 1rem;
}

.search-box i {
    position: absolute;
    left: 1rem;
    top: 50%;
    transform: translateY(-50%);
    color: var(--text-muted);
}

.search-box input {
    width: 100%;
    padding: 0.75rem 1rem 0.75rem 2.5rem;
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    background: var(--bg-primary);
    color: var(--text-primary);
}

.filters-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
}

.filters-grid select,
.filters-grid input {
    padding: 0.75rem;
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    background: var(--bg-primary);
    color: var(--text-primary);
}

.table-container {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-lg);
    overflow: hidden;
    margin-bottom: 2rem;
}

.complaints-table,
.users-table {
    width: 100%;
    border-collapse: collapse;
}

.complaints-table th,
.complaints-table td,
.users-table th,
.users-table td {
    padding: 1rem;
    text-align: left;
    border-bottom: 1px solid var(--border-color);
}

.complaints-table th,
.users-table th {
    background: var(--bg-tertiary);
    font-weight: 600;
    color: var(--text-secondary);
}

.complaint-title {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.urgent-badge {
    background: var(--danger-color);
    color: white;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 0.625rem;
    font-weight: 600;
}

.category-badge,
.status-badge,
.priority-badge,
.type-badge {
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 500;
}

.category-buracos {
    background: rgba(245, 158, 11, 0.1);
    color: var(--warning-color);
}

.category-iluminacao {
    background: rgba(6, 182, 212, 0.1);
    color: var(--accent-color);
}

.category-limpeza {
    background: rgba(16, 185, 129, 0.1);
    color: var(--success-color);
}

.category-transito {
    background: rgba(239, 68, 68, 0.1);
    color: var(--danger-color);
}

.category-seguranca {
    background: rgba(147, 51, 234, 0.1);
    color: var(--purple-color);
}

.status-pending {
    background: rgba(245, 158, 11, 0.1);
    color: var(--warning-color);
}

.status-in-progress {
    background: rgba(6, 182, 212, 0.1);
    color: var(--accent-color);
}

.status-resolved {
    background: rgba(16, 185, 129, 0.1);
    color: var(--success-color);
}

.status-urgent {
    background: rgba(239, 68, 68, 0.1);
    color: var(--danger-color);
}

.status-ativo {
    background: rgba(16, 185, 129, 0.1);
    color: var(--success-color);
}

.status-inativo {
    background: rgba(107, 114, 128, 0.1);
    color: var(--text-muted);
}

.priority-low {
    background: rgba(107, 114, 128, 0.1);
    color: var(--text-muted);
}

.priority-medium {
    background: rgba(6, 182, 212, 0.1);
    color: var(--accent-color);
}

.priority-high {
    background: rgba(245, 158, 11, 0.1);
    color: var(--warning-color);
}

.priority-urgent {
    background: rgba(239, 68, 68, 0.1);
    color: var(--danger-color);
}

.type-cidadão {
    background: var(--primary-light);
    color: var(--primary-color);
}

.type-gestor-público {
    background: rgba(239, 68, 68, 0.1);
    color: var(--danger-color);
}

.action-buttons {
    display: flex;
    gap: 0.5rem;
}

.user-avatar-small {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    object-fit: cover;
}

.pagination-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-lg);
}

.pagination {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.pagination-btn {
    padding: 0.5rem 0.75rem;
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    background: var(--bg-primary);
    color: var(--text-primary);
    cursor: pointer;
    transition: var(--transition);
}

.pagination-btn:hover:not(:disabled) {
    background: var(--primary-color);
    color: white;
}

.pagination-btn.active {
    background: var(--primary-color);
    color: white;
}

.pagination-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.user-stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.user-stat-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-lg);
    padding: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
}

.reports-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    margin-bottom: 2rem;
}

.report-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-lg);
    padding: 1.5rem;
}

.report-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
}

.report-status {
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 500;
}

.report-status.ready {
    background: rgba(16, 185, 129, 0.1);
    color: var(--success-color);
}

.report-status.processing {
    background: rgba(245, 158, 11, 0.1);
    color: var(--warning-color);
}

.report-content {
    margin-bottom: 1.5rem;
}

.report-stats {
    display: flex;
    gap: 1rem;
    font-size: 0.875rem;
    color: var(--text-muted);
    margin-top: 0.5rem;
}

.report-progress {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-top: 0.5rem;
}

.progress-bar {
    flex: 1;
    height: 6px;
    background: var(--bg-tertiary);
    border-radius: 3px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    background: var(--primary-color);
    transition: var(--transition);
}

.report-actions {
    display: flex;
    gap: 0.5rem;
}

.settings-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 2rem;
}

.settings-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-lg);
    padding: 1.5rem;
}

.settings-card h3 {
    font-weight: 600;
    margin-bottom: 1.5rem;
}

.settings-form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.settings-toggles {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.toggle-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 0;
    border-bottom: 1px solid var(--border-color);
}

.toggle-item:last-child {
    border-bottom: none;
}

.city-selector select {
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    padding: 0.5rem;
    color: var(--text-primary);
}

.spin {
    animation: spin 1s linear infinite;
}

@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 1024px) {
    .analytics-grid {
        grid-template-columns: 1fr;
    }
    
    .chart-card:last-child {
        grid-column: 1;
    }
}

@media (max-width: 768px) {
    .section-header {
        flex-direction: column;
        gap: 1rem;
        align-items: stretch;
    }
    
    .header-actions {
        flex-direction: column;
    }
    
    .stats-grid {
        grid-template-columns: 1fr;
    }
    
    .filters-grid {
        grid-template-columns: 1fr;
    }
    
    .table-container {
        overflow-x: auto;
    }
    
    .pagination-container {
        flex-direction: column;
        gap: 1rem;
    }
    
    .activity-item {
        flex-direction: column;
    }
    
    .activity-actions {
        align-self: flex-start;
    }
}
`;

// Inject admin styles
const styleSheet = document.createElement('style');
styleSheet.textContent = adminStyles;
document.head.appendChild(styleSheet);

