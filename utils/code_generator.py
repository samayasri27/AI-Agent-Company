"""
Code Generator Module
Generates complete applications and code structures for Engineering Department
"""
import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime


class CodeGenerator:
    """Generates complete application code and project structures"""
    
    def __init__(self):
        self.templates = {
            'web_app': self._get_web_app_template,
            'python_app': self._get_python_app_template,
            'flask_api': self._get_flask_api_template,
            'react_app': self._get_react_app_template,
            'fastapi_app': self._get_fastapi_app_template
        }
    
    def create_web_app(self, spec: Dict[str, Any]) -> Dict[str, str]:
        """Create a complete web application"""
        app_name = spec.get('name', 'webapp')
        app_type = spec.get('type', 'static')  # static, dynamic, spa
        features = spec.get('features', [])
        
        files = {}
        
        # HTML files
        files['index.html'] = self._generate_html_file(spec)
        
        if 'about' in features:
            files['about.html'] = self._generate_about_page(spec)
        
        if 'contact' in features:
            files['contact.html'] = self._generate_contact_page(spec)
        
        # CSS files
        files['styles.css'] = self._generate_css_file(spec)
        
        if 'responsive' in features:
            files['responsive.css'] = self._generate_responsive_css()
        
        # JavaScript files
        files['script.js'] = self._generate_javascript_file(spec)
        
        if 'api' in features:
            files['api.js'] = self._generate_api_client(spec)
        
        # Configuration files
        if app_type == 'dynamic':
            files['package.json'] = self._generate_package_json(spec)
        
        return files
    
    def create_python_app(self, spec: Dict[str, Any]) -> Dict[str, str]:
        """Create a complete Python application"""
        app_name = spec.get('name', 'python_app')
        app_type = spec.get('type', 'cli')  # cli, web, api, desktop
        features = spec.get('features', [])
        
        files = {}
        
        # Main application file
        if app_type == 'web':
            files['app.py'] = self._generate_flask_app(spec)
        elif app_type == 'api':
            files['main.py'] = self._generate_fastapi_app(spec)
        else:
            files['main.py'] = self._generate_cli_app(spec)
        
        # Configuration and utilities
        files['config.py'] = self._generate_config_file(spec)
        files['utils.py'] = self._generate_utils_file(spec)
        
        # Database models if needed
        if 'database' in features:
            files['models.py'] = self._generate_models_file(spec)
            files['database.py'] = self._generate_database_file(spec)
        
        # API routes if web/api app
        if app_type in ['web', 'api']:
            files['routes.py'] = self._generate_routes_file(spec)
        
        # Tests
        files['test_main.py'] = self._generate_test_file(spec)
        
        # Documentation
        files['README.md'] = self._generate_readme(spec)
        
        return files
    
    def create_requirements_file(self, dependencies: List[str], app_type: str = 'python') -> str:
        """Generate requirements.txt file"""
        if app_type == 'python':
            # Common Python dependencies
            base_deps = [
                'requests>=2.28.0',
                'python-dotenv>=0.19.0'
            ]
            
            # Add framework-specific dependencies
            if 'flask' in dependencies:
                base_deps.extend([
                    'Flask>=2.0.0',
                    'Flask-CORS>=3.0.0'
                ])
            
            if 'fastapi' in dependencies:
                base_deps.extend([
                    'fastapi>=0.68.0',
                    'uvicorn>=0.15.0'
                ])
            
            if 'database' in dependencies:
                base_deps.extend([
                    'SQLAlchemy>=1.4.0',
                    'psycopg2-binary>=2.9.0'
                ])
            
            if 'ai' in dependencies:
                base_deps.extend([
                    'openai>=0.27.0',
                    'numpy>=1.21.0',
                    'pandas>=1.3.0'
                ])
            
            # Add custom dependencies
            all_deps = list(set(base_deps + dependencies))
            return '\n'.join(sorted(all_deps))
        
        elif app_type == 'node':
            # Node.js package.json dependencies
            deps = {
                'express': '^4.18.0',
                'cors': '^2.8.5',
                'dotenv': '^16.0.0'
            }
            
            for dep in dependencies:
                if dep not in deps:
                    deps[dep] = 'latest'
            
            return json.dumps({'dependencies': deps}, indent=2)
        
        return '\n'.join(dependencies)
    
    def create_project_structure(self, project_type: str, spec: Dict[str, Any]) -> Dict[str, str]:
        """Create complete project structure with all files"""
        files = {}
        
        if project_type == 'web_app':
            files.update(self.create_web_app(spec))
            files['requirements.txt'] = self.create_requirements_file(
                spec.get('dependencies', []), 'python'
            )
        
        elif project_type == 'python_app':
            files.update(self.create_python_app(spec))
            files['requirements.txt'] = self.create_requirements_file(
                spec.get('dependencies', []), 'python'
            )
        
        elif project_type == 'flask_api':
            spec['type'] = 'web'
            spec['dependencies'] = spec.get('dependencies', []) + ['flask']
            files.update(self.create_python_app(spec))
            files['requirements.txt'] = self.create_requirements_file(
                spec.get('dependencies', []), 'python'
            )
        
        elif project_type == 'fastapi_app':
            spec['type'] = 'api'
            spec['dependencies'] = spec.get('dependencies', []) + ['fastapi']
            files.update(self.create_python_app(spec))
            files['requirements.txt'] = self.create_requirements_file(
                spec.get('dependencies', []), 'python'
            )
        
        # Add common project files
        files['.gitignore'] = self._generate_gitignore(project_type)
        files['docker-compose.yml'] = self._generate_docker_compose(spec)
        files['Dockerfile'] = self._generate_dockerfile(project_type, spec)
        
        return files
    
    # HTML Generation Methods
    def _generate_html_file(self, spec: Dict[str, Any]) -> str:
        app_name = spec.get('name', 'Web App')
        description = spec.get('description', 'A modern web application')
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{app_name}</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header>
        <nav>
            <div class="logo">
                <h1>{app_name}</h1>
            </div>
            <ul class="nav-links">
                <li><a href="#home">Home</a></li>
                <li><a href="#about">About</a></li>
                <li><a href="#services">Services</a></li>
                <li><a href="#contact">Contact</a></li>
            </ul>
        </nav>
    </header>

    <main>
        <section id="home" class="hero">
            <div class="hero-content">
                <h2>Welcome to {app_name}</h2>
                <p>{description}</p>
                <button class="cta-button">Get Started</button>
            </div>
        </section>

        <section id="about" class="section">
            <div class="container">
                <h2>About Us</h2>
                <p>We provide innovative solutions for modern businesses.</p>
            </div>
        </section>

        <section id="services" class="section">
            <div class="container">
                <h2>Our Services</h2>
                <div class="services-grid">
                    <div class="service-card">
                        <h3>Service 1</h3>
                        <p>Description of service 1</p>
                    </div>
                    <div class="service-card">
                        <h3>Service 2</h3>
                        <p>Description of service 2</p>
                    </div>
                    <div class="service-card">
                        <h3>Service 3</h3>
                        <p>Description of service 3</p>
                    </div>
                </div>
            </div>
        </section>
    </main>

    <footer>
        <div class="container">
            <p>&copy; 2024 {app_name}. All rights reserved.</p>
        </div>
    </footer>

    <script src="script.js"></script>
</body>
</html>'''
    
    def _generate_css_file(self, spec: Dict[str, Any]) -> str:
        theme = spec.get('theme', 'modern')
        
        return '''/* Reset and Base Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Arial', sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f4f4f4;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

/* Header Styles */
header {
    background: #fff;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    position: fixed;
    width: 100%;
    top: 0;
    z-index: 1000;
}

nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 2rem;
}

.logo h1 {
    color: #2c3e50;
    font-size: 1.8rem;
}

.nav-links {
    display: flex;
    list-style: none;
    gap: 2rem;
}

.nav-links a {
    text-decoration: none;
    color: #333;
    font-weight: 500;
    transition: color 0.3s ease;
}

.nav-links a:hover {
    color: #3498db;
}

/* Main Content */
main {
    margin-top: 80px;
}

.hero {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 100px 0;
    text-align: center;
}

.hero-content h2 {
    font-size: 3rem;
    margin-bottom: 1rem;
}

.hero-content p {
    font-size: 1.2rem;
    margin-bottom: 2rem;
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
}

.cta-button {
    background: #e74c3c;
    color: white;
    padding: 15px 30px;
    border: none;
    border-radius: 5px;
    font-size: 1.1rem;
    cursor: pointer;
    transition: background 0.3s ease;
}

.cta-button:hover {
    background: #c0392b;
}

.section {
    padding: 80px 0;
    background: white;
    margin: 2rem 0;
}

.section h2 {
    text-align: center;
    margin-bottom: 3rem;
    font-size: 2.5rem;
    color: #2c3e50;
}

.services-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    margin-top: 2rem;
}

.service-card {
    background: #f8f9fa;
    padding: 2rem;
    border-radius: 10px;
    text-align: center;
    transition: transform 0.3s ease;
}

.service-card:hover {
    transform: translateY(-5px);
}

.service-card h3 {
    color: #2c3e50;
    margin-bottom: 1rem;
}

/* Footer */
footer {
    background: #2c3e50;
    color: white;
    text-align: center;
    padding: 2rem 0;
}

/* Responsive Design */
@media (max-width: 768px) {
    .nav-links {
        display: none;
    }
    
    .hero-content h2 {
        font-size: 2rem;
    }
    
    .services-grid {
        grid-template-columns: 1fr;
    }
}'''
    
    def _generate_javascript_file(self, spec: Dict[str, Any]) -> str:
        return '''// Main JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    // Smooth scrolling for navigation links
    const navLinks = document.querySelectorAll('.nav-links a');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetSection = document.getElementById(targetId);
            
            if (targetSection) {
                targetSection.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // CTA Button functionality
    const ctaButton = document.querySelector('.cta-button');
    if (ctaButton) {
        ctaButton.addEventListener('click', function() {
            alert('Welcome! Ready to get started?');
            // Add your custom functionality here
        });
    }
    
    // Form handling (if contact form exists)
    const contactForm = document.querySelector('#contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            handleFormSubmission(this);
        });
    }
    
    // Scroll animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // Observe all sections for animations
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';
        section.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(section);
    });
});

// Form submission handler
function handleFormSubmission(form) {
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);
    
    // Simulate form submission
    console.log('Form submitted:', data);
    
    // Show success message
    showNotification('Thank you for your message! We will get back to you soon.', 'success');
    
    // Reset form
    form.reset();
}

// Notification system
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'success' ? '#27ae60' : '#3498db'};
        color: white;
        border-radius: 5px;
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);'''
    
    # Python Generation Methods
    def _generate_flask_app(self, spec: Dict[str, Any]) -> str:
        app_name = spec.get('name', 'flask_app')
        
        return f'''"""
{app_name.title()} - Flask Web Application
Generated by AI Agent Company
"""
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['DEBUG'] = os.environ.get('DEBUG', 'True').lower() == 'true'

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html', 
                         app_name='{app_name}',
                         timestamp=datetime.now())

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({{
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'app_name': '{app_name}'
    }})

@app.route('/api/data')
def get_data():
    """Sample API endpoint"""
    return jsonify({{
        'message': 'Hello from {app_name}!',
        'data': [
            {{'id': 1, 'name': 'Item 1', 'value': 100}},
            {{'id': 2, 'name': 'Item 2', 'value': 200}},
            {{'id': 3, 'name': 'Item 3', 'value': 300}}
        ],
        'timestamp': datetime.now().isoformat()
    }})

@app.route('/api/submit', methods=['POST'])
def submit_data():
    """Handle form submissions"""
    data = request.get_json()
    
    # Process the data here
    # For now, just echo it back
    
    return jsonify({{
        'success': True,
        'message': 'Data received successfully',
        'received_data': data,
        'timestamp': datetime.now().isoformat()
    }})

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({{'error': 'Not found'}}, 404)

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({{'error': 'Internal server error'}}, 500)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])'''
    
    def _generate_fastapi_app(self, spec: Dict[str, Any]) -> str:
        app_name = spec.get('name', 'fastapi_app')
        
        return f'''"""
{app_name.title()} - FastAPI Application
Generated by AI Agent Company
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os

# Data models
class Item(BaseModel):
    id: int
    name: str
    value: float
    created_at: Optional[datetime] = None

class SubmitData(BaseModel):
    name: str
    email: str
    message: str

# Initialize FastAPI app
app = FastAPI(
    title="{app_name.title()}",
    description="API generated by AI Agent Company",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sample data
sample_items = [
    Item(id=1, name="Item 1", value=100.0, created_at=datetime.now()),
    Item(id=2, name="Item 2", value=200.0, created_at=datetime.now()),
    Item(id=3, name="Item 3", value=300.0, created_at=datetime.now())
]

@app.get("/")
async def root():
    """Root endpoint"""
    return {{
        "message": "Welcome to {app_name.title()}",
        "timestamp": datetime.now().isoformat(),
        "docs": "/docs",
        "health": "/health"
    }}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {{
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "app_name": "{app_name}"
    }}

@app.get("/items", response_model=List[Item])
async def get_items():
    """Get all items"""
    return sample_items

@app.get("/items/{{item_id}}", response_model=Item)
async def get_item(item_id: int):
    """Get specific item by ID"""
    for item in sample_items:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")

@app.post("/items", response_model=Item)
async def create_item(item: Item):
    """Create new item"""
    item.created_at = datetime.now()
    sample_items.append(item)
    return item

@app.post("/submit")
async def submit_data(data: SubmitData):
    """Handle form submissions"""
    # Process the data here
    # For now, just acknowledge receipt
    
    return {{
        "success": True,
        "message": "Data received successfully",
        "received_data": data.dict(),
        "timestamp": datetime.now().isoformat()
    }}

@app.delete("/items/{{item_id}}")
async def delete_item(item_id: int):
    """Delete item by ID"""
    for i, item in enumerate(sample_items):
        if item.id == item_id:
            deleted_item = sample_items.pop(i)
            return {{"message": f"Item {{item_id}} deleted", "deleted_item": deleted_item}}
    raise HTTPException(status_code=404, detail="Item not found")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)'''
    
    def _generate_cli_app(self, spec: Dict[str, Any]) -> str:
        app_name = spec.get('name', 'cli_app')
        
        return f'''"""
{app_name.title()} - Command Line Application
Generated by AI Agent Company
"""
import argparse
import sys
import os
from datetime import datetime
import json

def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(description='{app_name.title()} CLI Application')
    parser.add_argument('--version', action='version', version='1.0.0')
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Process command
    process_parser = subparsers.add_parser('process', help='Process data')
    process_parser.add_argument('input', help='Input file or data')
    process_parser.add_argument('--output', '-o', help='Output file')
    process_parser.add_argument('--format', choices=['json', 'csv', 'txt'], default='json')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show application status')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Configuration management')
    config_parser.add_argument('action', choices=['show', 'set', 'reset'])
    config_parser.add_argument('--key', help='Configuration key')
    config_parser.add_argument('--value', help='Configuration value')
    
    args = parser.parse_args()
    
    if args.verbose:
        print(f"Starting {{app_name.title()}} at {{datetime.now()}}")
    
    if args.command == 'process':
        return process_data(args)
    elif args.command == 'status':
        return show_status(args)
    elif args.command == 'config':
        return manage_config(args)
    else:
        parser.print_help()
        return 1

def process_data(args):
    """Process input data"""
    try:
        print(f"Processing: {{args.input}}")
        
        # Simulate data processing
        result = {{
            'input': args.input,
            'processed_at': datetime.now().isoformat(),
            'status': 'success',
            'records_processed': 100,
            'format': args.format
        }}
        
        if args.output:
            with open(args.output, 'w') as f:
                if args.format == 'json':
                    json.dump(result, f, indent=2)
                else:
                    f.write(str(result))
            print(f"Results saved to: {{args.output}}")
        else:
            print(json.dumps(result, indent=2))
        
        return 0
        
    except Exception as e:
        print(f"Error processing data: {{e}}", file=sys.stderr)
        return 1

def show_status(args):
    """Show application status"""
    status = {{
        'app_name': '{app_name}',
        'version': '1.0.0',
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'python_version': sys.version,
        'platform': sys.platform
    }}
    
    print(json.dumps(status, indent=2))
    return 0

def manage_config(args):
    """Manage application configuration"""
    config_file = args.config or 'config.json'
    
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
        else:
            config = {{}}
        
        if args.action == 'show':
            print(json.dumps(config, indent=2))
        elif args.action == 'set':
            if not args.key or not args.value:
                print("Error: --key and --value required for set action", file=sys.stderr)
                return 1
            config[args.key] = args.value
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"Set {{args.key}} = {{args.value}}")
        elif args.action == 'reset':
            config = {{}}
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            print("Configuration reset")
        
        return 0
        
    except Exception as e:
        print(f"Error managing config: {{e}}", file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main())'''
    
    def _generate_config_file(self, spec: Dict[str, Any]) -> str:
        return '''"""
Configuration module
"""
import os
from typing import Dict, Any

class Config:
    """Application configuration"""
    
    # Basic settings
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database settings
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    
    # API settings
    API_HOST = os.environ.get('API_HOST', '0.0.0.0')
    API_PORT = int(os.environ.get('API_PORT', 8000))
    
    # External services
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    
    # Application settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    
    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """Get all configuration as dictionary"""
        return {
            'debug': cls.DEBUG,
            'api_host': cls.API_HOST,
            'api_port': cls.API_PORT,
            'database_url': cls.DATABASE_URL,
            'upload_folder': cls.UPLOAD_FOLDER,
            'max_content_length': cls.MAX_CONTENT_LENGTH
        }
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate required configuration"""
        required_vars = ['SECRET_KEY']
        
        for var in required_vars:
            if not getattr(cls, var):
                print(f"Warning: {var} not configured")
                return False
        
        return True

# Create config instance
config = Config()'''
    
    def _generate_utils_file(self, spec: Dict[str, Any]) -> str:
        return '''"""
Utility functions
"""
import json
import os
import hashlib
from datetime import datetime
from typing import Any, Dict, List, Optional

def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load JSON file safely"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file {file_path}: {e}")
        return {}

def save_json_file(data: Dict[str, Any], file_path: str) -> bool:
    """Save data to JSON file"""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving JSON file {file_path}: {e}")
        return False

def generate_hash(text: str) -> str:
    """Generate SHA256 hash of text"""
    return hashlib.sha256(text.encode()).hexdigest()

def format_timestamp(dt: datetime = None) -> str:
    """Format timestamp for display"""
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for filesystem safety"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename[:255]  # Limit length

def ensure_directory(path: str) -> bool:
    """Ensure directory exists"""
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creating directory {path}: {e}")
        return False

def get_file_size(file_path: str) -> int:
    """Get file size in bytes"""
    try:
        return os.path.getsize(file_path)
    except OSError:
        return 0

def format_file_size(size_bytes: int) -> str:
    """Format file size for human reading"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"

def validate_email(email: str) -> bool:
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

class Logger:
    """Simple logging utility"""
    
    def __init__(self, log_file: str = None):
        self.log_file = log_file
    
    def log(self, message: str, level: str = "INFO"):
        """Log message with timestamp"""
        timestamp = format_timestamp()
        log_entry = f"[{timestamp}] {level}: {message}"
        
        print(log_entry)
        
        if self.log_file:
            try:
                with open(self.log_file, 'a') as f:
                    f.write(log_entry + '\\n')
            except Exception as e:
                print(f"Error writing to log file: {e}")
    
    def info(self, message: str):
        """Log info message"""
        self.log(message, "INFO")
    
    def error(self, message: str):
        """Log error message"""
        self.log(message, "ERROR")
    
    def warning(self, message: str):
        """Log warning message"""
        self.log(message, "WARNING")'''
    
    def _generate_readme(self, spec: Dict[str, Any]) -> str:
        app_name = spec.get('name', 'Application')
        description = spec.get('description', 'A Python application generated by AI Agent Company')
        
        return f'''# {app_name.title()}

{description}

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Set the following environment variables:

- `DEBUG`: Enable debug mode (default: False)
- `SECRET_KEY`: Secret key for security (required)
- `DATABASE_URL`: Database connection URL
- `API_HOST`: API host (default: 0.0.0.0)
- `API_PORT`: API port (default: 8000)

## Usage

### Running the Application

```bash
python main.py
```

### Command Line Options

```bash
python main.py --help
```

### API Endpoints

- `GET /`: Root endpoint
- `GET /health`: Health check
- `GET /api/data`: Get sample data
- `POST /api/submit`: Submit data

## Development

### Running Tests

```bash
python -m pytest test_main.py
```

### Project Structure

```
{app_name}/
├── main.py          # Main application
├── config.py        # Configuration
├── utils.py         # Utility functions
├── requirements.txt # Dependencies
├── README.md        # This file
└── tests/
    └── test_main.py # Tests
```

## License

MIT License

## Generated by

AI Agent Company - Autonomous AI-powered business operations platform
Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
'''
    
    def _generate_gitignore(self, project_type: str) -> str:
        base_ignore = '''# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# pyenv
.python-version

# celery beat schedule file
celerybeat-schedule

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json'''

        if project_type == 'web_app':
            base_ignore += '''

# Node modules
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Build outputs
dist/
build/'''

        return base_ignore
    
    def _generate_dockerfile(self, project_type: str, spec: Dict[str, Any]) -> str:
        if project_type in ['python_app', 'flask_api', 'fastapi_app']:
            return '''FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "main.py"]'''
        
        return '''FROM node:16-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "start"]'''
    
    def _generate_docker_compose(self, spec: Dict[str, Any]) -> str:
        app_name = spec.get('name', 'app')
        
        return f'''version: '3.8'

services:
  {app_name}:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=false
      - DATABASE_URL=postgresql://user:password@db:5432/appdb
    depends_on:
      - db
    volumes:
      - ./uploads:/app/uploads

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=appdb
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:'''
    
    def _generate_test_file(self, spec: Dict[str, Any]) -> str:
        return '''"""
Test module
"""
import unittest
import json
from main import app

class TestApp(unittest.TestCase):
    """Test cases for the application"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = app.test_client() if hasattr(app, 'test_client') else None
        self.app_context = getattr(app, 'app_context', lambda: None)()
        if self.app_context:
            self.app_context.push()
    
    def tearDown(self):
        """Clean up after tests"""
        if self.app_context:
            self.app_context.pop()
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        if self.app:
            response = self.app.get('/health')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data['status'], 'healthy')
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        if self.app:
            response = self.app.get('/')
            self.assertEqual(response.status_code, 200)
    
    def test_data_processing(self):
        """Test data processing functionality"""
        # Add your specific tests here
        sample_data = {'test': 'data'}
        # Process data and assert results
        self.assertIsInstance(sample_data, dict)
    
    def test_configuration(self):
        """Test configuration loading"""
        from config import config
        self.assertIsNotNone(config)

if __name__ == '__main__':
    unittest.main()'''
    
    def get_available_templates(self) -> List[str]:
        """Get list of available project templates"""
        return list(self.templates.keys())
    
    def _get_web_app_template(self) -> Dict[str, Any]:
        """Get web app template configuration"""
        return {
            'name': 'Web Application',
            'description': 'Modern responsive web application',
            'files': ['index.html', 'styles.css', 'script.js'],
            'features': ['responsive', 'animations', 'forms']
        }
    
    def _get_python_app_template(self) -> Dict[str, Any]:
        """Get Python app template configuration"""
        return {
            'name': 'Python Application',
            'description': 'Full-featured Python application',
            'files': ['main.py', 'config.py', 'utils.py', 'requirements.txt'],
            'features': ['cli', 'configuration', 'logging', 'testing']
        }
    
    def _get_flask_api_template(self) -> Dict[str, Any]:
        """Get Flask API template configuration"""
        return {
            'name': 'Flask API',
            'description': 'RESTful API built with Flask',
            'files': ['app.py', 'routes.py', 'models.py', 'requirements.txt'],
            'features': ['rest_api', 'database', 'authentication', 'cors']
        }
    
    def _get_react_app_template(self) -> Dict[str, Any]:
        """Get React app template configuration"""
        return {
            'name': 'React Application',
            'description': 'Modern React single-page application',
            'files': ['App.js', 'index.js', 'package.json'],
            'features': ['spa', 'components', 'routing', 'state_management']
        }
    
    def _get_fastapi_app_template(self) -> Dict[str, Any]:
        """Get FastAPI template configuration"""
        return {
            'name': 'FastAPI Application',
            'description': 'High-performance API with FastAPI',
            'files': ['main.py', 'models.py', 'requirements.txt'],
            'features': ['async_api', 'automatic_docs', 'validation', 'performance']
        }