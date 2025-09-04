from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import hashlib
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:5174"}})  # Enable CORS specifically for frontend

# Database initialization
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print("Database initialized successfully")

# Authentication Routes
@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No data provided'}), 400
            
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        print(f"Registration attempt - Username: {username}, Email: {email}")
        
        # Validation
        if not username or not email or not password:
            return jsonify({'message': 'All fields are required'}), 400
        
        # Email format validation
        import re
        email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_regex, email):
            return jsonify({'message': 'Invalid email format'}), 400
        
        # Password length validation
        if len(password) < 6:
            return jsonify({'message': 'Password must be at least 6 characters long'}), 400
        
        # Hash password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        # Database operations
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                (username, email, hashed_password)
            )
            conn.commit()
            
            print(f"User {username} registered successfully")
            
            return jsonify({
                'message': 'Account created successfully!',
                'user': {'username': username, 'email': email}
            }), 201
            
        except sqlite3.IntegrityError as e:
            print(f"Registration failed - Integrity error: {str(e)}")
            if 'username' in str(e).lower():
                return jsonify({'message': 'Username already exists'}), 400
            elif 'email' in str(e).lower():
                return jsonify({'message': 'Email already exists'}), 400
            else:
                return jsonify({'message': 'User already exists'}), 400
        finally:
            conn.close()
            
    except Exception as e:
        print(f"Registration error: {str(e)}")
        return jsonify({'message': 'Server error occurred'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No data provided'}), 400
            
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        print(f"Login attempt - Username: {username}")
        
        if not username or not password:
            return jsonify({'message': 'Username and password are required'}), 400
        
        # Hash password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        # Database check
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT username, email FROM users WHERE username = ? AND password = ?',
            (username, hashed_password)
        )
        user = cursor.fetchone()
        conn.close()
        
        if user:
            print(f"User {username} logged in successfully")
            return jsonify({
                'message': 'Login successful!',
                'user': {'username': user[0], 'email': user[1]}
            }), 200
        else:
            print(f"Login failed for username: {username}")
            return jsonify({'message': 'Invalid username or password'}), 401
            
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'message': 'Server error occurred'}), 500

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'Backend server is running',
        'endpoints': ['register', 'login', 'generate_2d_graph', 'generate_3d_graph'],
        'timestamp': datetime.now().isoformat()
    }), 200

# Existing graph generation routes
@app.route('/api/generate_2d_graph', methods=['POST'])
def generate_2d_graph():
    try:
        data = request.get_json()
        expression = data.get('expression', '')
        
        if not expression:
            return jsonify({'error': 'No expression provided'}), 400
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Generate x values
        x = np.linspace(-10, 10, 1000)
        
        try:
            # Replace common mathematical expressions
            expression = expression.replace('^', '**')
            expression = expression.replace('sin', 'np.sin')
            expression = expression.replace('cos', 'np.cos')
            expression = expression.replace('tan', 'np.tan')
            expression = expression.replace('log', 'np.log')
            expression = expression.replace('sqrt', 'np.sqrt')
            expression = expression.replace('exp', 'np.exp')
            expression = expression.replace('pi', 'np.pi')
            expression = expression.replace('e', 'np.e')
            
            # Evaluate the expression
            y = eval(expression)
            
            # Plot the graph
            ax.plot(x, y, 'b-', linewidth=2)
            ax.grid(True, alpha=0.3)
            ax.axhline(y=0, color='k', linewidth=0.5)
            ax.axvline(x=0, color='k', linewidth=0.5)
            ax.set_xlabel('x')
            ax.set_ylabel('y')
            ax.set_title(f'Graph of y = {data.get("expression", "")}')
            
        except Exception as e:
            return jsonify({'error': f'Invalid expression: {str(e)}'}), 400
        
        # Save plot to base64
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close()
        
        return jsonify({
            'image': img_base64,
            'expression': data.get('expression', ''),
            'type': '2D'
        })
        
    except Exception as e:
        print(f"2D Graph generation error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate_3d_graph', methods=['POST'])
def generate_3d_graph():
    try:
        data = request.get_json()
        expression = data.get('expression', '')
        
        if not expression:
            return jsonify({'error': 'No expression provided'}), 400
        
        # Create 3D figure
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        # Generate theta and phi values for polar coordinates
        theta = np.linspace(0, 2*np.pi, 100)
        phi = np.linspace(0, np.pi, 50)
        THETA, PHI = np.meshgrid(theta, phi)
        
        try:
            # Replace mathematical expressions
            expr = expression.replace('^', '**')
            expr = expr.replace('sin', 'np.sin')
            expr = expr.replace('cos', 'np.cos')
            expr = expr.replace('tan', 'np.tan')
            expr = expr.replace('sqrt', 'np.sqrt')
            expr = expr.replace('pi', 'np.pi')
            expr = expr.replace('theta', 'THETA')
            expr = expr.replace('phi', 'PHI')
            
            # Evaluate the expression to get radius
            R = eval(expr)
            
            # Convert to Cartesian coordinates
            X = R * np.sin(PHI) * np.cos(THETA)
            Y = R * np.sin(PHI) * np.sin(THETA)
            Z = R * np.cos(PHI)
            
            # Plot the surface
            surf = ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8, linewidth=0, antialiased=True)
            
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')
            ax.set_title(f'3D Surface: r = {data.get("expression", "")}')
            
            # Add colorbar
            fig.colorbar(surf, shrink=0.5, aspect=5)
            
        except Exception as e:
            return jsonify({'error': f'Invalid expression: {str(e)}'}), 400
        
        # Save plot to base64
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close()
        
        return jsonify({
            'image': img_base64,
            'expression': data.get('expression', ''),
            'type': '3D'
        })
        
    except Exception as e:
        print(f"3D Graph generation error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Serve static files
@app.route('/')
def serve_frontend():
    return "Graph Generator Backend Server is running!"

if __name__ == '__main__':
    # Initialize database on startup
    init_db()
    
    print("=" * 50)
    print("🚀 Graph Generator Backend Server Starting...")
    print("📊 Endpoints available:")
    print("   - POST /api/register")
    print("   - POST /api/login") 
    print("   - POST /api/generate_2d_graph")
    print("   - POST /api/generate_3d_graph")
    print("   - GET /health")
    print("🌐 Server running on: http://localhost:5000")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)