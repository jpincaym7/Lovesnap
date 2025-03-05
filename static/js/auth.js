document.addEventListener('alpine:init', () => {
    Alpine.data('auth', () => ({
        activeTab: 'login',
        loading: false,
        error: null,
        showPassword: false,
        loginData: {
            login: '',
            password: '',
            remember: false
        },
        registerData: {
            email: '',
            username: '',
            first_name: '',
            last_name: '',
            password: '',
            confirm_password: '',
            phone: '',
            bio: ''
        },

        // Utility function to get CSRF token
        getCsrfToken() {
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
            if (!csrfToken) {
                throw new Error('CSRF token not found. Please refresh the page.');
            }
            return csrfToken;
        },

        // Utility function to handle API responses
        async handleApiResponse(response) {
            const data = await response.json();
            
            if (!response.ok) {
                if (typeof data === 'object' && data !== null) {
                    // Handle Django REST framework error format
                    if (data.detail) {
                        throw new Error(data.detail);
                    }
                    // Handle form validation errors
                    const errorMessages = Object.entries(data)
                        .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(', ') : value}`)
                        .join('\n');
                    throw new Error(errorMessages);
                }
                throw new Error('An unexpected error occurred');
            }
            
            return data;
        },

        // Utility function to store token
        storeToken(token) {
            localStorage.setItem('auth_token', token);
        },

        async handleLogin() {
            try {
                if (!this.loginData.login || !this.loginData.password) {
                    throw new Error('Please fill in all required fields');
                }

                this.loading = true;
                this.error = null;

                const response = await fetch('/security/users/login/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCsrfToken()
                    },
                    body: JSON.stringify(this.loginData),
                    credentials: 'include' // Include cookies in the request
                });

                const data = await this.handleApiResponse(response);
                
                // Store token from response
                this.storeToken(data.token);
                
                // Redirect to dashboard
                window.location.href = '/';

            } catch (err) {
                this.error = err.message;
            } finally {
                this.loading = false;
            }
        },

        validatePassword(password) {
            if (password.length < 8) {
                throw new Error('Password must be at least 8 characters long');
            }
            if (!/(?=.*[A-Za-z])(?=.*\d)/.test(password)) {
                throw new Error('Password must contain at least one letter and one number');
            }
        },

        async handleRegister() {
            try {
                const requiredFields = ['email', 'username', 'password', 'confirm_password'];
                const missingFields = requiredFields.filter(field => !this.registerData[field]);
                
                if (missingFields.length > 0) {
                    throw new Error('Please fill in all required fields');
                }

                this.validatePassword(this.registerData.password);

                if (this.registerData.password !== this.registerData.confirm_password) {
                    throw new Error('Passwords do not match');
                }

                this.loading = true;
                this.error = null;

                const response = await fetch('/security/users/register/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCsrfToken()
                    },
                    body: JSON.stringify(this.registerData),
                    credentials: 'include' // Include cookies in the request
                });

                const data = await this.handleApiResponse(response);
                
                // Store token from response
                this.storeToken(data.token);
                
                // Redirect to dashboard
                window.location.href = '/';

            } catch (err) {
                this.error = err.message;
            } finally {
                this.loading = false;
            }
        }
    }));

    // Auto-advance slides every 5 seconds with error handling
    const autoAdvanceSlides = () => {
        try {
            const slideContainer = document.querySelector('[x-data]');
            if (slideContainer && slideContainer.__x) {
                const currentSlide = slideContainer.__x.$data.currentSlide;
                slideContainer.__x.$data.currentSlide = (currentSlide + 1) % 3;
            }
        } catch (error) {
            console.error('Error advancing slides:', error);
        }
    };

    const slideInterval = setInterval(autoAdvanceSlides, 5000);

    // Cleanup interval when page is hidden/inactive
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            clearInterval(slideInterval);
        } else {
            setInterval(autoAdvanceSlides, 5000);
        }
    });
});