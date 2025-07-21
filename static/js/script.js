/**
 * Aggarwal Bhawan, Haridwar - Main JavaScript File
 * Handles form interactions, AJAX requests, and dynamic UI updates
 */

// Global variables
let dashboardRefreshInterval;
const API_BASE_URL = '';

// Utility Functions
const Utils = {
    /**
     * Show notification to user
     * @param {string} message - Message to display
     * @param {string} type - Type of notification (success, error, info)
     */
    showNotification(message, type = 'info') {
        const flashContainer = document.querySelector('.flash-messages') || this.createFlashContainer();

        const flashDiv = document.createElement('div');
        flashDiv.className = `flash flash-${type}`;
        flashDiv.innerHTML = `
            ${message}
            <button class="flash-close" onclick="this.parentElement.style.display='none'">&times;</button>
        `;

        flashContainer.appendChild(flashDiv);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (flashDiv.parentNode) {
                flashDiv.style.opacity = '0';
                setTimeout(() => flashDiv.remove(), 300);
            }
        }, 5000);
    },

    /**
     * Create flash message container if it doesn't exist
     */
    createFlashContainer() {
        const container = document.createElement('div');
        container.className = 'flash-messages';
        document.querySelector('.main-content').insertBefore(container, document.querySelector('.main-content').firstChild);
        return container;
    },

    /**
     * Format currency for display
     * @param {number} amount - Amount to format
     * @returns {string} Formatted currency string
     */
    formatCurrency(amount) {
        return `₹${parseFloat(amount).toFixed(2)}`;
    },

    /**
     * Validate form field in real-time
     * @param {HTMLElement} field - Form field to validate
     * @param {Object} rules - Validation rules
     */
    validateField(field, rules) {
        const value = field.value.trim();
        let isValid = true;
        let errorMessage = '';

        // Required field validation
        if (rules.required && !value) {
            isValid = false;
            errorMessage = `${rules.label} is required`;
        }

        // Pattern validation
        if (isValid && rules.pattern && !rules.pattern.test(value)) {
            isValid = false;
            errorMessage = rules.message || `Invalid ${rules.label} format`;
        }

        // Length validation
        if (isValid && rules.length && value.length !== rules.length) {
            isValid = false;
            errorMessage = `${rules.label} must be exactly ${rules.length} characters`;
        }

        // Min/Max validation
        if (isValid && rules.min !== undefined && parseFloat(value) < rules.min) {
            isValid = false;
            errorMessage = `${rules.label} must be at least ${rules.min}`;
        }

        if (isValid && rules.max !== undefined && parseFloat(value) > rules.max) {
            isValid = false;
            errorMessage = `${rules.label} must not exceed ${rules.max}`;
        }

        // Update field appearance
        field.classList.toggle('valid', isValid);
        field.classList.toggle('invalid', !isValid);

        // Show/hide error message
        let errorDiv = field.parentNode.querySelector('.field-error');
        if (!isValid) {
            if (!errorDiv) {
                errorDiv = document.createElement('div');
                errorDiv.className = 'field-error';
                field.parentNode.appendChild(errorDiv);
            }
            errorDiv.textContent = errorMessage;
            errorDiv.style.color = '#dc3545';
            errorDiv.style.fontSize = '0.8rem';
            errorDiv.style.marginTop = '0.25rem';
        } else if (errorDiv) {
            errorDiv.remove();
        }

        return isValid;
    },

    /**
     * Debounce function to limit API calls
     * @param {Function} func - Function to debounce
     * @param {number} wait - Wait time in milliseconds
     */
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
};

// Form Validation Module
const FormValidator = {
    // Validation rules for different fields
    rules: {
        full_name: {
            required: true,
            label: 'Full Name'
        },
        address: {
            required: true,
            label: 'Address'
        },
        area: {
            required: true,
            label: 'Area'
        },
        pincode: {
            required: true,
            pattern: /^\d{6}$/,
            label: 'Pincode',
            message: 'Pincode must be exactly 6 digits'
        },
        aadhar_number: {
            required: true,
            pattern: /^\d{12}$/,
            length: 12,
            label: 'Aadhar Number',
            message: 'Aadhar number must be exactly 12 digits'
        },
        mobile_number: {
            required: true,
            pattern: /^\d{10}$/,
            length: 10,
            label: 'Mobile Number',
            message: 'Mobile number must be exactly 10 digits'
        },
        email: {
            required: true,
            pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
            label: 'Email Address',
            message: 'Please enter a valid email address'
        },
        amount_paid_today: {
            required: true,
            min: 0,
            label: 'Amount Paid Today'
        },
        remaining_amount: {
            required: true,
            min: 0,
            label: 'Remaining Amount'
        },
        room_number: {
            required: true,
            label: 'Room Number'
        }
    },

    /**
     * Initialize form validation
     * @param {string} formId - ID of the form to validate
     */
    init(formId) {
        const form = document.getElementById(formId);
        if (!form) return;

        // Add validation to each field
        Object.keys(this.rules).forEach(fieldName => {
            const field = form.querySelector(`[name="${fieldName}"]`);
            if (field) {
                // Real-time validation on input
                field.addEventListener('input', Utils.debounce(() => {
                    Utils.validateField(field, this.rules[fieldName]);
                }, 300));

                // Validation on blur
                field.addEventListener('blur', () => {
                    Utils.validateField(field, this.rules[fieldName]);
                });
            }
        });

        // Form submission validation
        form.addEventListener('submit', (e) => {
            console.log('Form submit event triggered');
            const isFormValid = this.validateForm(form);
            console.log('Form validation result:', isFormValid);

            if (!isFormValid) {
                e.preventDefault();
                console.log('Form submission prevented due to validation errors');
                Utils.showNotification('Please fix the validation errors before submitting', 'error');
            } else {
                console.log('Form validation passed, allowing submission');
            }
        });
    },

    /**
     * Validate entire form
     * @param {HTMLElement} form - Form element to validate
     * @returns {boolean} True if form is valid
     */
    validateForm(form) {
        let isValid = true;
        const errors = [];

        console.log('Validating form fields...');

        Object.keys(this.rules).forEach(fieldName => {
            const field = form.querySelector(`[name="${fieldName}"]`);
            if (field) {
                const fieldValid = Utils.validateField(field, this.rules[fieldName]);
                console.log(`Field ${fieldName}: ${fieldValid ? 'VALID' : 'INVALID'} (value: "${field.value}")`);
                if (!fieldValid) {
                    isValid = false;
                    errors.push(fieldName);
                }
            } else {
                console.log(`Field ${fieldName}: NOT FOUND in form`);
            }
        });

        console.log('Form validation summary:', { isValid, errors });
        return isValid;
    }
};

// Dashboard Module
const Dashboard = {
    /**
     * Initialize dashboard functionality
     */
    init() {
        this.loadRoomStatus();
        this.startAutoRefresh();
        this.bindEvents();
    },

    /**
     * Load room status from API
     */
    async loadRoomStatus() {
        // ROOM STATUS LOADING DISABLED TO PREVENT FLICKERING
        console.log('🛑 Room status loading disabled to prevent flickering');
        return;
        // try {
        //     const response = await fetch('/api/room_status');
        //     if (!response.ok) throw new Error('Failed to fetch room status');

        //     const roomStatus = await response.json();
        //     this.renderRoomGrid(roomStatus);
        // } catch (error) {
        //     console.error('Error loading room status:', error);
        //     Utils.showNotification('Failed to load room status', 'error');
        // }
    },

    /**
     * Render room status grid
     * @param {Object} roomStatus - Room status data
     */
    renderRoomGrid(roomStatus) {
        const roomGrid = document.getElementById('room-grid');
        if (!roomGrid) return;

        roomGrid.innerHTML = '';

        // Create room cells for all 157 rooms
        for (let roomNum = 1; roomNum <= 157; roomNum++) {
            const roomDiv = document.createElement('div');
            roomDiv.className = `room-cell ${roomStatus[roomNum] || 'available'}`;
            roomDiv.textContent = roomNum;
            roomDiv.title = `Room ${roomNum}: ${roomStatus[roomNum] || 'available'}`;

            // Add click event for room details
            roomDiv.addEventListener('click', () => this.showRoomDetails(roomNum, roomStatus[roomNum]));

            roomGrid.appendChild(roomDiv);
        }
    },

    /**
     * Show room details in modal or notification
     * @param {number} roomNumber - Room number
     * @param {string} status - Room status
     */
    showRoomDetails(roomNumber, status) {
        const statusText = status === 'occupied' ? 'Occupied' : 'Available';
        const statusIcon = status === 'occupied' ? '🔴' : '🟢';

        Utils.showNotification(
            `${statusIcon} Room ${roomNumber} is currently ${statusText}`,
            status === 'occupied' ? 'info' : 'success'
        );
    },

    /**
     * Start auto-refresh for dashboard data
     */
    startAutoRefresh() {
        // AUTO-REFRESH DISABLED TO PREVENT FLICKERING
        console.log('🛑 Dashboard auto-refresh disabled to prevent flickering');
        // dashboardRefreshInterval = setInterval(() => {
        //     this.loadRoomStatus();
        // }, 30000);
    },

    /**
     * Stop auto-refresh
     */
    stopAutoRefresh() {
        if (dashboardRefreshInterval) {
            clearInterval(dashboardRefreshInterval);
        }
    },

    /**
     * Bind dashboard events
     */
    bindEvents() {
        // Manual refresh button
        const refreshBtn = document.querySelector('[data-action="refresh"]');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.loadRoomStatus();
                Utils.showNotification('Dashboard refreshed', 'success');
            });
        }

        // Click on dashboard title to refresh - DISABLED TO PREVENT FLICKERING
        const dashboardTitle = document.querySelector('.dashboard-container h2');
        if (dashboardTitle) {
            // dashboardTitle.addEventListener('click', () => {
            //     location.reload();
            // });
            // dashboardTitle.style.cursor = 'pointer';
            // dashboardTitle.title = 'Click to refresh page';
            console.log('🛑 Dashboard title click-to-refresh disabled to prevent flickering');
        }
    }
}
};

// Check-in Form Module
const CheckinForm = {
    /**
     * Initialize check-in form
     */
    init() {
        this.bindEvents();
        this.setupCalculations();
        FormValidator.init('checkinForm');
    },

    /**
     * Bind form events
     */
    bindEvents() {
        const form = document.getElementById('checkinForm');
        if (!form) return;

        // Number-only inputs
        this.setupNumberOnlyFields();

        // Auto-format fields
        this.setupAutoFormatting();

        // Form reset
        const resetBtn = document.querySelector('[onclick="resetForm()"]');
        if (resetBtn) {
            resetBtn.onclick = this.resetForm.bind(this);
        }
    },

    /**
     * Setup number-only input fields
     */
    setupNumberOnlyFields() {
        const numberFields = ['aadhar_number', 'mobile_number', 'pincode'];

        numberFields.forEach(fieldName => {
            const field = document.getElementById(fieldName);
            if (field) {
                field.addEventListener('input', (e) => {
                    // Remove non-numeric characters
                    e.target.value = e.target.value.replace(/[^0-9]/g, '');

                    // Limit length based on field
                    const maxLengths = {
                        aadhar_number: 12,
                        mobile_number: 10,
                        pincode: 6
                    };

                    if (e.target.value.length > maxLengths[fieldName]) {
                        e.target.value = e.target.value.slice(0, maxLengths[fieldName]);
                    }
                });
            }
        });
    },

    /**
     * Setup auto-formatting for certain fields
     */
    setupAutoFormatting() {
        // Auto-format Aadhar number with spaces (display only)
        const aadharField = document.getElementById('aadhar_number');
        if (aadharField) {
            let lastValue = '';
            aadharField.addEventListener('input', (e) => {
                const value = e.target.value.replace(/\s/g, '');
                if (value !== lastValue) {
                    lastValue = value;
                    // Format: XXXX XXXX XXXX
                    const formatted = value.replace(/(\d{4})(?=\d)/g, '$1 ');
                    e.target.setAttribute('data-formatted', formatted);
                }
            });
        }

        // Auto-capitalize names
        const nameField = document.getElementById('full_name');
        if (nameField) {
            nameField.addEventListener('blur', (e) => {
                e.target.value = e.target.value.replace(/\b\w/g, l => l.toUpperCase());
            });
        }
    },

    /**
     * Setup amount calculations
     */
    setupCalculations() {
        const paidField = document.getElementById('amount_paid_today');
        const remainingField = document.getElementById('remaining_amount');

        if (paidField && remainingField) {
            const calculateTotal = () => {
                const paid = parseFloat(paidField.value) || 0;
                const remaining = parseFloat(remainingField.value) || 0;
                const total = paid + remaining;

                this.updateTotalDisplay(total);
            };

            paidField.addEventListener('input', calculateTotal);
            remainingField.addEventListener('input', calculateTotal);
        }
    },

    /**
     * Update total amount display
     * @param {number} total - Total amount
     */
    updateTotalDisplay(total) {
        let totalDisplay = document.getElementById('total-display');

        if (total > 0) {
            if (!totalDisplay) {
                totalDisplay = document.createElement('div');
                totalDisplay.id = 'total-display';
                totalDisplay.className = 'total-amount';

                const remainingField = document.getElementById('remaining_amount');
                remainingField.parentNode.appendChild(totalDisplay);
            }

            totalDisplay.innerHTML = `<strong>Total Amount: ${Utils.formatCurrency(total)}</strong>`;
        } else if (totalDisplay) {
            totalDisplay.remove();
        }
    },

    /**
     * Reset form with confirmation
     */
    resetForm() {
        if (confirm('Are you sure you want to reset the form? All entered data will be lost.')) {
            const form = document.getElementById('checkinForm');
            form.reset();

            // Remove validation classes
            document.querySelectorAll('.valid, .invalid').forEach(el => {
                el.classList.remove('valid', 'invalid');
            });

            // Remove error messages
            document.querySelectorAll('.field-error').forEach(el => el.remove());

            // Remove total display
            const totalDisplay = document.getElementById('total-display');
            if (totalDisplay) totalDisplay.remove();

            // Focus on first field
            document.getElementById('full_name').focus();

            Utils.showNotification('Form has been reset', 'info');
        }
    }
};

// Calendar Module
const CalendarView = {
    /**
     * Initialize calendar view
     */
    init() {
        this.bindKeyboardEvents();
        this.setupTooltips();
    },

    /**
     * Bind keyboard navigation events
     */
    bindKeyboardEvents() {
        document.addEventListener('keydown', (e) => {
            switch (e.key) {
                case 'ArrowLeft':
                    this.navigateMonth(-1);
                    break;
                case 'ArrowRight':
                    this.navigateMonth(1);
                    break;
                case 'Escape':
                    this.closeBookingDetails();
                    break;
            }
        });
    },

    /**
     * Navigate to previous/next month
     * @param {number} direction - -1 for previous, 1 for next
     */
    navigateMonth(direction) {
        const currentDate = new Date(window.currentMonth || new Date());
        currentDate.setMonth(currentDate.getMonth() + direction);

        const yearMonth = `${currentDate.getFullYear()}-${String(currentDate.getMonth() + 1).padStart(2, '0')}`;
        window.location.href = `/calendar?month=${yearMonth}`;
    },

    /**
     * Close booking details panel
     */
    closeBookingDetails() {
        const bookingDetails = document.getElementById('bookingDetails');
        if (bookingDetails) {
            bookingDetails.style.display = 'none';
        }
    },

    /**
     * Setup tooltips for calendar elements
     */
    setupTooltips() {
        // Add hover effects and enhanced tooltips
        document.querySelectorAll('.calendar-day').forEach(day => {
            day.addEventListener('mouseenter', (e) => {
                if (e.target.classList.contains('has-bookings')) {
                    e.target.style.transform = 'scale(1.02)';
                    e.target.style.zIndex = '10';
                }
            });

            day.addEventListener('mouseleave', (e) => {
                e.target.style.transform = '';
                e.target.style.zIndex = '';
            });
        });
    }
};

// Initialize modules based on current page
document.addEventListener('DOMContentLoaded', function () {
    // Common initialization for all pages
    setupGlobalFeatures();

    // Page-specific initialization
    const currentPage = window.location.pathname;

    if (currentPage === '/' || currentPage === '/dashboard') {
        Dashboard.init();
    } else if (currentPage === '/checkin') {
        // CheckinForm.init(); // Disabled to avoid conflicts with inline JS
        console.log('Checkin page detected - using inline validation');
    } else if (currentPage === '/calendar') {
        CalendarView.init();
    } else if (currentPage.startsWith('/calendar')) {
        CalendarView.init();
    }

    // Initialize form validation for any forms on the page
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        if (form.id && form.id !== 'checkinForm') {
            FormValidator.init(form.id);
        }
    });
});

/**
 * Setup global features available on all pages
 */
function setupGlobalFeatures() {
    // Auto-hide flash messages
    setTimeout(() => {
        document.querySelectorAll('.flash').forEach(flash => {
            flash.style.opacity = '0';
            setTimeout(() => flash.remove(), 300);
        });
    }, 5000);

    // Add loading states to buttons
    document.querySelectorAll('button[type="submit"]').forEach(btn => {
        btn.addEventListener('click', function () {
            const originalText = this.innerHTML;
            this.innerHTML = '⏳ Processing...';
            this.disabled = true;

            // Re-enable after 10 seconds as fallback
            setTimeout(() => {
                this.innerHTML = originalText;
                this.disabled = false;
            }, 10000);
        });
    });

    // Add smooth scrolling to anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Ctrl+/ for help
        if (e.ctrlKey && e.key === '/') {
            e.preventDefault();
            showKeyboardShortcuts();
        }

        // Ctrl+R for refresh (custom handler)
        if (e.ctrlKey && e.key === 'r') {
            e.preventDefault();
            location.reload();
        }
    });
}

/**
 * Show keyboard shortcuts help
 */
function showKeyboardShortcuts() {
    const shortcuts = [
        'Ctrl + / : Show this help',
        'Ctrl + R : Refresh page',
        'Arrow Keys : Navigate calendar (on calendar page)',
        'Escape : Close modals/details',
        'Tab : Navigate form fields'
    ];

    Utils.showNotification(
        '⌨️ Keyboard Shortcuts:<br>' + shortcuts.join('<br>'),
        'info'
    );
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (typeof Dashboard !== 'undefined') {
        Dashboard.stopAutoRefresh();
    }
});

// Export for global access
window.HotelManagement = {
    Utils,
    FormValidator,
    Dashboard,
    CheckinForm,
    CalendarView
};
