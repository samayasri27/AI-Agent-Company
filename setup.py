#!/usr/bin/env python3
# setup.py - Setup script for AI Agent Company

import os
import sys
import subprocess
import platform

def get_python_command():
    """Get the correct Python command for this system"""
    # Try python3 first (common on macOS/Linux)
    try:
        result = subprocess.run(['python3', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            return 'python3'
    except FileNotFoundError:
        pass
    
    # Try python (common on Windows)
    try:
        result = subprocess.run(['python', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            return 'python'
    except FileNotFoundError:
        pass
    
    print("❌ Neither 'python' nor 'python3' command found")
    sys.exit(1)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version.split()[0]}")

def create_virtual_environment():
    """Create virtual environment if it doesn't exist"""
    python_cmd = get_python_command()
    
    if not os.path.exists('venv'):
        print("📦 Creating virtual environment...")
        try:
            subprocess.run([python_cmd, '-m', 'venv', 'venv'], check=True)
            print("✅ Virtual environment created")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create virtual environment: {e}")
            sys.exit(1)
    else:
        print("✅ Virtual environment already exists")

def get_pip_command():
    """Get the correct pip command for the virtual environment"""
    if os.name == 'nt':  # Windows
        return os.path.join('venv', 'Scripts', 'pip')
    else:  # Unix/Linux/macOS
        return os.path.join('venv', 'bin', 'pip')

def install_dependencies():
    """Install required dependencies"""
    print("📥 Installing dependencies...")
    
    pip_path = get_pip_command()
    
    try:
        # Upgrade pip first
        subprocess.run([pip_path, 'install', '--upgrade', 'pip'], check=True)
        
        # Install requirements
        subprocess.run([pip_path, 'install', '-r', 'requirements.txt'], check=True)
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print("Please try manually:")
        print(f"1. Activate virtual environment")
        print(f"2. Run: {pip_path} install -r requirements.txt")

def setup_environment_file():
    """Setup environment configuration file"""
    if not os.path.exists('.env'):
        print("📝 Creating environment configuration file...")
        try:
            with open('.env.example', 'r') as example:
                content = example.read()
            
            with open('.env', 'w') as env_file:
                env_file.write(content)
            
            print("✅ Created .env file from template")
            print("⚠️  Please edit .env file and add your API keys")
        except FileNotFoundError:
            print("⚠️  .env.example not found, creating basic .env file")
            with open('.env', 'w') as env_file:
                env_file.write("# AI Agent Company Environment Configuration\n")
                env_file.write("GROQ_API_KEY_1=your_primary_groq_api_key_here\n")
                env_file.write("GROQ_API_KEY_2=your_backup_groq_api_key_here\n")
                env_file.write("MODEL_NAME=mixtral-8x7b-32768\n")
            print("✅ Created basic .env file")
    else:
        print("✅ Environment file already exists")

def create_directories():
    """Create necessary directories"""
    directories = ['logs', 'workspace', 'data']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created directory: {directory}")

def setup_memory_system():
    """Setup the centralized memory system."""
    print("🧠 Setting up Memory System...")
    
    python_cmd = get_python_command()
    
    # Get the correct python executable for the virtual environment
    if os.name == 'nt':  # Windows
        python_path = os.path.join('venv', 'Scripts', 'python')
    else:  # Unix/Linux/macOS
        python_path = os.path.join('venv', 'bin', 'python')
    
    try:
        # Run memory system setup
        result = subprocess.run([
            python_path, 'scripts/setup_memory_system.py'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Memory system setup completed")
        else:
            print("⚠️  Memory system setup completed with warnings")
            if result.stderr:
                print(f"Warnings: {result.stderr}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Memory system setup failed: {e}")
        return False
    except FileNotFoundError:
        print("⚠️  Memory system setup script not found, skipping...")
        return True

def main():
    """Main setup function"""
    print("🚀 AI Agent Company Setup")
    print("=" * 40)
    print(f"Platform: {platform.system()} {platform.release()}")
    
    try:
        check_python_version()
        create_virtual_environment()
        install_dependencies()
        setup_environment_file()
        create_directories()
        
        # Setup memory system (optional, may fail if credentials not configured)
        setup_memory_system()
        
        print("\n" + "=" * 40)
        print("🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Edit .env file and add your API keys:")
        print("   - Groq API keys for LLM functionality")
        print("   - Supabase credentials for memory system")
        print("2. Activate virtual environment:")
        
        if os.name == 'nt':  # Windows
            print("   venv\\Scripts\\activate")
        else:  # Unix/Linux/macOS
            print("   source venv/bin/activate")
        
        print("3. Validate memory system configuration:")
        python_cmd = get_python_command()
        print(f"   {python_cmd} scripts/validate_memory_config.py")
        print("4. Run the system:")
        print(f"   {python_cmd} main.py")
        print("\n" + "=" * 40)
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()