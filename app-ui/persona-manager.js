/**
 * Persona Manager for Remo AI Frontend
 * Handles persona switching and management
 */

class PersonaManager {
    constructor(apiBaseUrl = 'http://localhost:8000') {
        this.apiBaseUrl = apiBaseUrl;
        this.currentPersona = 'remo';
        this.availablePersonas = {};
    }

    /**
     * Load available personas from the API
     */
    async loadPersonas() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/personas`);
            const data = await response.json();
            
            if (data.success) {
                this.availablePersonas = data.personas;
                this.currentPersona = data.current_persona;
                return data;
            } else {
                throw new Error(data.error || 'Failed to load personas');
            }
        } catch (error) {
            console.error('Error loading personas:', error);
            throw error;
        }
    }

    /**
     * Get current persona details
     */
    async getCurrentPersona() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/personas/current`);
            const data = await response.json();
            
            if (data.success) {
                this.currentPersona = data.current_persona;
                return data;
            } else {
                throw new Error(data.error || 'Failed to get current persona');
            }
        } catch (error) {
            console.error('Error getting current persona:', error);
            throw error;
        }
    }

    /**
     * Switch to a different persona
     */
    async setPersona(personaName) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/personas/${personaName}`, {
                method: 'POST'
            });
            const data = await response.json();
            
            if (data.success) {
                this.currentPersona = personaName;
                return data;
            } else {
                throw new Error(data.error || 'Failed to set persona');
            }
        } catch (error) {
            console.error('Error setting persona:', error);
            throw error;
        }
    }

    /**
     * Get persona display name
     */
    getPersonaDisplayName(personaName) {
        const persona = this.availablePersonas[personaName];
        return persona ? persona.split(' - ')[0] : personaName;
    }

    /**
     * Get persona description
     */
    getPersonaDescription(personaName) {
        return this.availablePersonas[personaName] || '';
    }

    /**
     * Create persona selector HTML
     */
    createPersonaSelector() {
        const selector = document.createElement('div');
        selector.className = 'persona-selector';
        selector.innerHTML = `
            <div class="persona-header">
                <h3>Choose Your AI Assistant</h3>
                <div class="current-persona">
                    <span class="persona-name">${this.getPersonaDisplayName(this.currentPersona)}</span>
                    <span class="persona-description">${this.getPersonaDescription(this.currentPersona)}</span>
                </div>
            </div>
            <div class="persona-options">
                ${Object.keys(this.availablePersonas).map(personaName => `
                    <div class="persona-option ${personaName === this.currentPersona ? 'active' : ''}" 
                         data-persona="${personaName}">
                        <div class="persona-option-name">${this.getPersonaDisplayName(personaName)}</div>
                        <div class="persona-option-desc">${this.getPersonaDescription(personaName)}</div>
                    </div>
                `).join('')}
            </div>
        `;

        // Add click handlers
        selector.querySelectorAll('.persona-option').forEach(option => {
            option.addEventListener('click', async () => {
                const personaName = option.dataset.persona;
                if (personaName !== this.currentPersona) {
                    try {
                        await this.setPersona(personaName);
                        this.updatePersonaSelector(selector);
                        this.onPersonaChanged?.(personaName);
                    } catch (error) {
                        console.error('Failed to switch persona:', error);
                        alert('Failed to switch persona: ' + error.message);
                    }
                }
            });
        });

        return selector;
    }

    /**
     * Update persona selector after switching
     */
    updatePersonaSelector(selector) {
        selector.querySelectorAll('.persona-option').forEach(option => {
            option.classList.toggle('active', option.dataset.persona === this.currentPersona);
        });
        
        const currentPersonaEl = selector.querySelector('.current-persona');
        if (currentPersonaEl) {
            currentPersonaEl.querySelector('.persona-name').textContent = this.getPersonaDisplayName(this.currentPersona);
            currentPersonaEl.querySelector('.persona-description').textContent = this.getPersonaDescription(this.currentPersona);
        }
    }

    /**
     * Callback for when persona changes
     */
    onPersonaChanged = null;
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PersonaManager;
}
