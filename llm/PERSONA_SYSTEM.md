# Remo AI Persona System

The Remo AI Persona System allows you to switch between different AI personalities, each with their own unique communication style and behavior patterns.

## Available Personas

### 1. Remo (Default) - Friendly Assistant
- **Style**: Warm, helpful, and encouraging
- **Use Case**: General conversations, support, and friendly interactions
- **Characteristics**: Uses emojis, asks follow-up questions, patient and understanding

### 2. Professional - Business Assistant
- **Style**: Professional, efficient, and business-focused
- **Use Case**: Business communications, formal discussions, data analysis
- **Characteristics**: Direct, solution-focused, uses professional language

### 3. Creative - Artistic Assistant
- **Style**: Imaginative, enthusiastic, and creative
- **Use Case**: Creative writing, brainstorming, artistic projects
- **Characteristics**: Uses vivid language, metaphors, encourages creative thinking

## API Endpoints

### Get Available Personas
```http
GET /personas
```
Returns all available personas and the current persona.

### Get Current Persona
```http
GET /personas/current
```
Returns details about the currently active persona.

### Switch Persona
```http
POST /personas/{persona_name}
```
Switches to the specified persona. Available persona names:
- `remo` - Default friendly assistant
- `professional` - Business-focused assistant
- `creative` - Creative and artistic assistant

## Usage Examples

### Python API Usage
```python
import requests

# Get available personas
response = requests.get('http://localhost:8000/personas')
personas = response.json()

# Switch to professional persona
response = requests.post('http://localhost:8000/personas/professional')

# Send a message (will use the current persona)
response = requests.post('http://localhost:8000/chat', json={
    'message': 'Help me write a business proposal'
})
```

### JavaScript Frontend Usage
```javascript
const personaManager = new PersonaManager();

// Load personas
await personaManager.loadPersonas();

// Switch persona
await personaManager.setPersona('creative');

// Send message
const response = await fetch('http://localhost:8000/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: 'Write a poem about robots' })
});
```

## Configuration

Personas are configured in `persona.yaml` and can be customized by editing the file. Each persona includes:

- `name`: Display name
- `description`: Brief description
- `system_prompt`: The AI system prompt that defines behavior
- `greeting`: Welcome message
- `voice_style`: Description of speaking style
- `response_style`: Description of response characteristics

## Testing

Run the persona test script to verify functionality:

```bash
cd llm
python test_personas.py
```

## Frontend Demo

Open `app-ui/persona-demo.html` in a web browser to see an interactive demo of the persona system.

## Adding Custom Personas

You can add custom personas by editing the `persona.yaml` file or using the PersonaManager API:

```python
from persona import PersonaManager

pm = PersonaManager()
pm.add_persona('custom', {
    'name': 'Custom Assistant',
    'description': 'A custom AI assistant',
    'system_prompt': 'You are a custom assistant...',
    'greeting': 'Hello! I\'m your custom assistant.',
    'voice_style': 'custom style',
    'response_style': 'custom responses'
})
```
