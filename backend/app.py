from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for server deployment
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.animation import PillowWriter
import base64
from io import BytesIO
import re
import math
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
# import google.generativeai as genai  # Temporarily commented out

app = Flask(__name__)
CORS(app)  # Enable CORS for React app

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///graph_visualizer.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'graph-visualizer-secret-key-change-in-production'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to saved graphs
    saved_graphs = db.relationship('SavedGraph', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'total_graphs': len(self.saved_graphs)
        }

class SavedGraph(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    expression = db.Column(db.Text, nullable=False)
    graph_type = db.Column(db.String(10), nullable=False)  # '2D' or '3D'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_favorite = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'expression': self.expression,
            'graph_type': self.graph_type,
            'created_at': self.created_at.isoformat(),
            'is_favorite': self.is_favorite
        }

# Create database tables
with app.app_context():
    db.create_all()
    print("Database tables created successfully!")

# Configure Gemini AI (you'll need to set your API key)
# Set your API key: export GEMINI_API_KEY="your_api_key_here"
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
model = None  # Temporarily disabled
print("Gemini AI temporarily disabled. Basic graph generation will work.")

# Authentication Routes
@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        # Validation
        if not username or not email or not password:
            return jsonify({'error': 'All fields are required'}), 400
        
        if len(username) < 3:
            return jsonify({'error': 'Username must be at least 3 characters'}), 400
            
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        # Create new user
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, email=email, password_hash=password_hash)
        
        db.session.add(new_user)
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(identity=new_user.id)
        
        print(f"New user registered: {username}")
        
        return jsonify({
            'message': 'User created successfully',
            'access_token': access_token,
            'user': new_user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Registration error: {e}")
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        # Find user
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            access_token = create_access_token(identity=user.id)
            print(f"User logged in: {username}")
            return jsonify({
                'message': 'Login successful',
                'access_token': access_token,
                'user': user.to_dict()
            })
        else:
            return jsonify({'error': 'Invalid username or password'}), 401
            
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@app.route('/api/auth/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if user:
            return jsonify({'user': user.to_dict()})
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': f'Profile fetch failed: {str(e)}'}), 500

@app.route('/api/graphs/save', methods=['POST'])
@jwt_required()
def save_graph():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        title = data.get('title', f"Graph {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        expression = data.get('expression')
        graph_type = data.get('graph_type')
        
        if not expression or not graph_type:
            return jsonify({'error': 'Expression and graph type are required'}), 400
        
        # Create new saved graph
        saved_graph = SavedGraph(
            user_id=current_user_id,
            title=title,
            expression=expression,
            graph_type=graph_type
        )
        
        db.session.add(saved_graph)
        db.session.commit()
        
        print(f"Graph saved for user {current_user_id}: {title}")
        
        return jsonify({
            'message': 'Graph saved successfully',
            'graph': saved_graph.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Save graph error: {e}")
        return jsonify({'error': f'Failed to save graph: {str(e)}'}), 500

@app.route('/api/graphs', methods=['GET'])
@jwt_required()
def get_user_graphs():
    try:
        current_user_id = get_jwt_identity()
        graphs = SavedGraph.query.filter_by(user_id=current_user_id).order_by(SavedGraph.created_at.desc()).all()
        
        return jsonify({
            'graphs': [graph.to_dict() for graph in graphs]
        })
        
    except Exception as e:
        print(f"Get graphs error: {e}")
        return jsonify({'error': f'Failed to fetch graphs: {str(e)}'}), 500

@app.route('/api/graphs/<int:graph_id>/favorite', methods=['PUT'])
@jwt_required()
def toggle_favorite(graph_id):
    try:
        current_user_id = get_jwt_identity()
        graph = SavedGraph.query.filter_by(id=graph_id, user_id=current_user_id).first()
        
        if not graph:
            return jsonify({'error': 'Graph not found'}), 404
            
        graph.is_favorite = not graph.is_favorite
        db.session.commit()
        
        return jsonify({
            'message': 'Favorite status updated',
            'is_favorite': graph.is_favorite
        })
        
    except Exception as e:
        print(f"Toggle favorite error: {e}")
        return jsonify({'error': f'Failed to update favorite: {str(e)}'}), 500

@app.route('/api/graphs/<int:graph_id>', methods=['DELETE'])
@jwt_required()
def delete_graph(graph_id):
    try:
        current_user_id = get_jwt_identity()
        graph = SavedGraph.query.filter_by(id=graph_id, user_id=current_user_id).first()
        
        if not graph:
            return jsonify({'error': 'Graph not found'}), 404
            
        db.session.delete(graph)
        db.session.commit()
        
        return jsonify({'message': 'Graph deleted successfully'})
        
    except Exception as e:
        print(f"Delete graph error: {e}")
        return jsonify({'error': f'Failed to delete graph: {str(e)}'}), 500

@app.route('/api/generate', methods=['POST'])
@jwt_required(optional=True)  # Make authentication optional for now
def generate_graph():
    current_user_id = get_jwt_identity()  # None if not authenticated
    
    data = request.get_json()
    function_type = data.get('functionType')
    expression = data.get('expression')
    
    print(f"📨 Received request: type={function_type}, expression={expression}, user={current_user_id}")
    
    if not expression:
        print("No expression provided")
        return jsonify({
            'status': 'error',
            'message': 'No expression provided'
        }), 400
    
    try:
        if function_type == '2D':
            print("Generating 2D graph...")
            graph_data = generate_2d_graph(expression)
            print("2D graph generated successfully!")
            return jsonify({
                'status': 'success',
                'type': '2D',
                'data': graph_data,
                'can_save': current_user_id is not None
            })
        elif function_type == '3D':
            print("Generating 3D model...")
            model_data = generate_3d_model(expression)
            print("3D model generated successfully!")
            return jsonify({
                'status': 'success',
                'type': '3D', 
                'data': model_data,
                'can_save': current_user_id is not None
            })
        else:
            print(f"Invalid function type: {function_type}")
            return jsonify({
                'status': 'error',
                'message': 'Invalid function type'
            }), 400
    except Exception as e:
        print(f"💥 Error generating graph: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error generating graph: {str(e)}'
        }), 400

def safe_eval_expression(expression, x_values):
    """Safely evaluate mathematical expressions"""
    # Replace common mathematical notation
    expression = expression.lower()
    expression = expression.replace('^', '**')  # Handle exponents
    expression = expression.replace('ln', 'log')  # Natural log
    
    # Create safe environment for evaluation
    safe_dict = {
        "x": x_values,
        "sin": np.sin,
        "cos": np.cos,
        "tan": np.tan,
        "exp": np.exp,
        "log": np.log,
        "sqrt": np.sqrt,
        "abs": np.abs,
        "pi": np.pi,
        "e": np.e,
        "__builtins__": {}  # Remove built-in functions for security
    }
    
    try:
        # Evaluate the expression
        result = eval(expression, safe_dict)
        return result
    except:
        # Fallback to simple polynomial if evaluation fails
        return x_values**2

def safe_eval_polar_expression(expression, theta_values, a=1, n=1):
    """Complete polar expression evaluation for accurate rose curves and cardioids"""
    original_expression = expression
    print(f"Evaluating polar expression: '{expression}'")
    
    # Clean and normalize expression
    expression = expression.lower().strip()
    expression = expression.replace('^', '**')
    expression = expression.replace('θ', 'theta')
    expression = expression.replace('ϴ', 'theta')
    expression = expression.replace(' ', '')  # Remove all spaces for pattern matching
    
    # Handle parentheses multiplication
    import re
    expression = re.sub(r'(\d+)\(', r'\1*(', expression)
    
    print(f"Normalized expression: '{expression}'")
    
    try:
        # ==================== CARDIOID PATTERNS ====================
        
        # Pattern 1: r = a(1 + cos(θ)) - RIGHT-FACING HEARTS
        cardioid_right = r'r=(\d+\.?\d*)?\*?\(1\+cos\(theta\)\)'
        match = re.search(cardioid_right, expression)
        if match:
            a = float(match.group(1)) if match.group(1) else 1.0
            print(f"RIGHT-FACING Cardioid: a={a}, x-axis symmetry")
            return a * (1 + np.cos(theta_values))
        
        # Pattern 2: r = a(1 - cos(θ)) - LEFT-FACING HEARTS
        cardioid_left = r'r=(\d+\.?\d*)?\*?\(1-cos\(theta\)\)'
        match = re.search(cardioid_left, expression)
        if match:
            a = float(match.group(1)) if match.group(1) else 1.0
            print(f"LEFT-FACING Cardioid: a={a}, x-axis symmetry, flipped")
            return a * (1 - np.cos(theta_values))
        
        # Pattern 3: r = a(1 + sin(θ)) - UP-FACING HEARTS
        cardioid_up = r'r=(\d+\.?\d*)?\*?\(1\+sin\(theta\)\)'
        match = re.search(cardioid_up, expression)
        if match:
            a = float(match.group(1)) if match.group(1) else 1.0
            print(f"UP-FACING Cardioid: a={a}, y-axis symmetry")
            return a * (1 + np.sin(theta_values))
        
        # Pattern 4: r = a(1 - sin(θ)) - DOWN-FACING HEARTS
        cardioid_down = r'r=(\d+\.?\d*)?\*?\(1-sin\(theta\)\)'
        match = re.search(cardioid_down, expression)
        if match:
            a = float(match.group(1)) if match.group(1) else 1.0
            print(f"DOWN-FACING Cardioid: a={a}, y-axis symmetry, inverted")
            return a * (1 - np.sin(theta_values))
        
        # ==================== LIMAÇON PATTERNS ====================
        
        # Pattern 5: r = 1 + 2*cos(θ) - INNER LOOP
        if expression == 'r=1+2*cos(theta)':
            print("INNER LOOP Limaçon: heart with inner loop (b > a)")
            return 1 + 2 * np.cos(theta_values)
        
        # Pattern 6: r = 2 + cos(θ) - DIMPLED
        if expression == 'r=2+cos(theta)':
            print("DIMPLED Limaçon: smooth dimple (a > b)")
            return 2 + np.cos(theta_values)
        
        # Additional limaçon patterns
        if expression == 'r=1+2*sin(theta)':
            print("INNER LOOP Limaçon (sin): rotated inner loop")
            return 1 + 2 * np.sin(theta_values)
        
        if expression == 'r=2+sin(theta)':
            print("DIMPLED Limaçon (sin): rotated dimpled shape")
            return 2 + np.sin(theta_values)
        
        # ==================== ROSE CURVE PATTERNS ====================
        
        # Pattern 1: r = a*cos(k*theta) with coefficient
        rose_cos_coeff = r'r=(\d+\.?\d*)\*?cos\((\d+)\*theta\)'
        match = re.search(rose_cos_coeff, expression)
        if match:
            amplitude = float(match.group(1))
            k = int(match.group(2))
            petals = k if k % 2 != 0 else 2 * k
            print(f"Rose curve (cos with amplitude): a={amplitude}, k={k}, petals={petals}")
            return amplitude * np.cos(k * theta_values)
        
        # Pattern 2: r = cos(k*theta) without coefficient
        rose_cos_simple = r'r=cos\((\d+)\*theta\)'
        match = re.search(rose_cos_simple, expression)
        if match:
            k = int(match.group(1))
            petals = k if k % 2 != 0 else 2 * k
            print(f"Rose curve (cos): k={k}, petals={petals}")
            return np.cos(k * theta_values)
        
        # Pattern 3: r = a*sin(k*theta) with coefficient
        rose_sin_coeff = r'r=(\d+\.?\d*)\*?sin\((\d+)\*theta\)'
        match = re.search(rose_sin_coeff, expression)
        if match:
            amplitude = float(match.group(1))
            k = int(match.group(2))
            petals = k if k % 2 != 0 else 2 * k
            print(f"Rose curve (sin with amplitude): a={amplitude}, k={k}, petals={petals}")
            return amplitude * np.sin(k * theta_values)
        
        # Pattern 4: r = sin(k*theta) without coefficient
        rose_sin_simple = r'r=sin\((\d+)\*theta\)'
        match = re.search(rose_sin_simple, expression)
        if match:
            k = int(match.group(1))
            petals = k if k % 2 != 0 else 2 * k
            print(f"Rose curve (sin): k={k}, petals={petals}")
            return np.sin(k * theta_values)
        
        # Special case: r = cos(theta) or r = sin(theta)
        if expression == 'r=cos(theta)':
            print("Single petal rose (cos)")
            return np.cos(theta_values)
        elif expression == 'r=sin(theta)':
            print("Single petal rose (sin)")
            return np.sin(theta_values)
        
        # ==================== EXACT PATTERN MATCHING ====================
        
        clean_expr = expression.replace('r=', '')
        
        # Comprehensive exact patterns
        exact_patterns = {
            # CARDIOIDS - Perfect heart shapes
            '1+cos(theta)': 1 + np.cos(theta_values),
            '1-cos(theta)': 1 - np.cos(theta_values),
            '1+sin(theta)': 1 + np.sin(theta_values),
            '1-sin(theta)': 1 - np.sin(theta_values),
            '2*(1+cos(theta))': 2 * (1 + np.cos(theta_values)),
            '3*(1-cos(theta))': 3 * (1 - np.cos(theta_values)),
            '4*(1+sin(theta))': 4 * (1 + np.sin(theta_values)),
            '2*(1-sin(theta))': 2 * (1 - np.sin(theta_values)),
            '2(1+cos(theta))': 2 * (1 + np.cos(theta_values)),
            '3(1-cos(theta))': 3 * (1 - np.cos(theta_values)),
            '4(1+sin(theta))': 4 * (1 + np.sin(theta_values)),
            '2(1-sin(theta))': 2 * (1 - np.sin(theta_values)),
            
            # LIMAÇONS
            '1+2*cos(theta)': 1 + 2 * np.cos(theta_values),
            '2+cos(theta)': 2 + np.cos(theta_values),
            '1+2*sin(theta)': 1 + 2 * np.sin(theta_values),
            '2+sin(theta)': 2 + np.sin(theta_values),
            
            # ROSE CURVES
            'cos(theta)': np.cos(theta_values),
            'sin(theta)': np.sin(theta_values),
            '2*cos(theta)': 2 * np.cos(theta_values),
            '3*sin(theta)': 3 * np.sin(theta_values),
            'cos(2*theta)': np.cos(2 * theta_values),
            'sin(2*theta)': np.sin(2 * theta_values),
            '2*cos(2*theta)': 2 * np.cos(2 * theta_values),
            'cos(3*theta)': np.cos(3 * theta_values),
            'sin(3*theta)': np.sin(3 * theta_values),
            '2*cos(3*theta)': 2 * np.cos(3 * theta_values),
            '4*sin(3*theta)': 4 * np.sin(3 * theta_values),
            'cos(4*theta)': np.cos(4 * theta_values),
            'sin(4*theta)': np.sin(4 * theta_values),
            '5*cos(4*theta)': 5 * np.cos(4 * theta_values),
            '3*sin(4*theta)': 3 * np.sin(4 * theta_values),
            'cos(5*theta)': np.cos(5 * theta_values),
            'sin(5*theta)': np.sin(5 * theta_values),
            '3*sin(5*theta)': 3 * np.sin(5 * theta_values),
            'cos(6*theta)': np.cos(6 * theta_values),
            'sin(6*theta)': np.sin(6 * theta_values),
            '6*cos(6*theta)': 6 * np.cos(6 * theta_values),
            'cos(7*theta)': np.cos(7 * theta_values),
            'sin(7*theta)': np.sin(7 * theta_values),
            '2*sin(7*theta)': 2 * np.sin(7 * theta_values),
            'cos(8*theta)': np.cos(8 * theta_values),
            'sin(8*theta)': np.sin(8 * theta_values),
        }
        
        if clean_expr in exact_patterns:
            print(f"Exact pattern match: {clean_expr}")
            return exact_patterns[clean_expr]
        
        # General safe evaluation
        safe_dict = {
            'theta': theta_values,
            'cos': np.cos,
            'sin': np.sin,
            'tan': np.tan,
            'pi': np.pi,
            'e': np.e,
            'exp': np.exp,
            'log': np.log,
            'sqrt': np.sqrt,
            'abs': np.abs,
            '__builtins__': {}
        }
        
        expr_eval = expression.replace('r=', '')
        result = eval(expr_eval, safe_dict)
        
        if isinstance(result, (int, float)):
            return np.full_like(theta_values, result)
        
        return result
        
    except Exception as e:
        print(f"Error in polar evaluation: {e}")
        # Enhanced fallback
        if 'cos(4*theta)' in expression:
            return np.cos(4 * theta_values)
        elif '1+cos(theta)' in expression:
            return 1 + np.cos(theta_values)
        elif '1-cos(theta)' in expression:
            return 1 - np.cos(theta_values)
        elif 'cos(theta)' in expression:
            return np.cos(theta_values)
        return np.ones_like(theta_values)
        # Evaluate the expression
        result = eval(expression, safe_dict)
        print(f"Successfully evaluated expression")
        return result
    except Exception as e:
        print(f"Error evaluating polar expression '{expression}': {e}")
        
        # Enhanced fallback for rose curves
        if 'cos(4*theta)' in expression:
            print("Fallback to 8-petal rose curve: cos(4*theta)")
            return np.cos(4 * theta_values)
        elif 'sin(4*theta)' in expression:
            print("Fallback to 8-petal rose curve: sin(4*theta)")
            return np.sin(4 * theta_values)
        elif 'cos(3*theta)' in expression:
            print("Fallback to 3-petal rose curve: cos(3*theta)")
            return np.cos(3 * theta_values)
        elif 'sin(3*theta)' in expression:
            print("Fallback to 3-petal rose curve: sin(3*theta)")
            return np.sin(3 * theta_values)
        elif "1 + cos" in expression or "1 - cos" in expression:
            print(f"Fallback to cardioid pattern")
            # Cardioid fallback
            if "1 + cos" in expression:
                return 1 + np.cos(theta_values)
            else:
                return 1 - np.cos(theta_values)
        elif "1 + sin" in expression or "1 - sin" in expression:
            print(f"Fallback to cardioid pattern (sin)")
            if "1 + sin" in expression:
                return 1 + np.sin(theta_values)
            else:
                return 1 - np.sin(theta_values)
        else:
            print(f"Falling back to default rose curve a*cos(n*theta) with a={a}, n={n}")
            # Fallback to simple rose curve
            return a * np.cos(n * theta_values)

def detect_polar_equation(expression):
    """Detect if the expression is a polar equation (contains r, theta, etc.)"""
    expr_lower = expression.lower()
    polar_indicators = ['r =', 'r=', 'theta', 'θ', 'ϴ', 'cos(', 'sin(', 'cos(t)', 'sin(t)', 'cos(theta)', 'sin(theta)']
    cartesian_indicators = ['y =', 'y=', 'f(x)', 'x**', 'x^']
    
    # Enhanced rose curve detection
    import re
    rose_patterns = [
        r'cos\s*\(\s*\d+\s*\*\s*theta\s*\)',  # cos(n*theta)
        r'sin\s*\(\s*\d+\s*\*\s*theta\s*\)',  # sin(n*theta)
        r'r\s*=\s*cos\s*\(\s*\d+\s*\*\s*theta\s*\)',  # r = cos(n*theta)
        r'r\s*=\s*sin\s*\(\s*\d+\s*\*\s*theta\s*\)',  # r = sin(n*theta)
    ]
    
    # Check for rose curve patterns
    for pattern in rose_patterns:
        if re.search(pattern, expr_lower):
            print(f"Detected rose curve pattern in: {expression}")
            return True
    
    has_polar = any(indicator in expr_lower for indicator in polar_indicators)
    has_cartesian = any(indicator in expr_lower for indicator in cartesian_indicators)
    
    # If it has polar indicators and no strong cartesian indicators, treat as polar
    return has_polar and not has_cartesian

def generate_2d_graph(expression):
    """Generate 2D graph with matplotlib - supports both Cartesian and Polar coordinates"""
    
    # Check if this is a polar equation
    is_polar = detect_polar_equation(expression)
    
    if is_polar:
        return generate_polar_graph(expression)
    else:
        return generate_cartesian_graph(expression)

def generate_polar_graph(expression):
    """Generate polar graph (like rose curves) with matplotlib"""
    try:
        # Create theta values (0 to 2π for most polar curves)
        theta = np.linspace(0, 4*np.pi, 1000)  # Extra range for multi-petal roses
        
        # Extract parameters from common rose curve patterns
        a, n = extract_rose_parameters(expression)
        
        # Clean the expression for evaluation
        expr_clean = expression.lower()
        expr_clean = expr_clean.replace('r =', '').replace('r=', '').strip()
        expr_clean = expr_clean.replace('θ', 'theta').replace('ϴ', 'theta')
        
        # Evaluate the polar expression
        r = safe_eval_polar_expression(expr_clean, theta, a, n)
        
        # Convert polar to Cartesian for plotting
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        
        # Filter out invalid points
        valid_mask = np.isfinite(x) & np.isfinite(y) & (np.abs(r) < 100)
        x = x[valid_mask]
        y = y[valid_mask]
        
        # Create the plot
        plt.figure(figsize=(10, 10))  # Square aspect ratio for polar plots
        plt.plot(x, y, 'b-', linewidth=2, label=f'r = {expression.split("=")[-1].strip() if "=" in expression else expression}')
        plt.grid(True, alpha=0.3)
        plt.title(f'Rose Curve: {expression}', fontsize=14, fontweight='bold')
        plt.xlabel('x', fontsize=12)
        plt.ylabel('y', fontsize=12)
        plt.legend()
        plt.axis('equal')  # Equal scaling for proper rose shape
        
        # Add origin lines
        plt.axhline(y=0, color='k', linewidth=0.5, alpha=0.5)
        plt.axvline(x=0, color='k', linewidth=0.5, alpha=0.5)
        
        # Convert plot to base64 image
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        # Calculate analysis
        analysis = analyze_polar_function(theta, r, expression, a, n)
        
        return {
            'image': f'data:image/png;base64,{image_base64}',
            'expression': expression,
            'analysis': analysis
        }
        
    except Exception as e:
        print(f"Error in polar graph generation: {e}")
        # Fallback to default rose curve
        theta = np.linspace(0, 4*np.pi, 1000)
        r = np.cos(2 * theta)
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        
        plt.figure(figsize=(10, 10))
        plt.plot(x, y, 'r--', linewidth=2, label='Default: r = cos(2θ)')
        plt.grid(True, alpha=0.3)
        plt.title(f'Error plotting "{expression}" - Showing default rose curve', fontsize=14)
        plt.xlabel('x', fontsize=12)
        plt.ylabel('y', fontsize=12)
        plt.legend()
        plt.axis('equal')
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return {
            'image': f'data:image/png;base64,{image_base64}',
            'expression': f'{expression} (error - showing default rose)',
            'analysis': {'error': str(e), 'type': 'Rose Curve (default)'}
        }

def generate_cartesian_graph(expression):
    """Generate Cartesian graph with matplotlib"""
    # Create x values
    x = np.linspace(-10, 10, 400)
    
    try:
        # Evaluate the expression
        y = safe_eval_expression(expression, x)
        
        # Handle cases where y might be a scalar
        if np.isscalar(y):
            y = np.full_like(x, y)
        
        # Create the plot
        plt.figure(figsize=(10, 6))
        plt.plot(x, y, 'b-', linewidth=2, label=f'f(x) = {expression}')
        plt.grid(True, alpha=0.3)
        plt.title(f'2D Graph of f(x) = {expression}', fontsize=14, fontweight='bold')
        plt.xlabel('x', fontsize=12)
        plt.ylabel('y', fontsize=12)
        plt.legend()
        
        # Add some styling
        plt.axhline(y=0, color='k', linewidth=0.5)
        plt.axvline(x=0, color='k', linewidth=0.5)
        
        # Set reasonable y-limits to avoid extreme values
        finite_y = y[np.isfinite(y)]
        if len(finite_y) > 0:
            y_min, y_max = np.percentile(finite_y, [5, 95])
            plt.ylim(y_min - 0.1 * abs(y_min), y_max + 0.1 * abs(y_max))
        
        # Convert plot to base64 image
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        # Calculate some basic analysis
        analysis = analyze_function(x, y, expression)
        
        return {
            'image': f'data:image/png;base64,{image_base64}',
            'expression': expression,
            'analysis': analysis
        }
        
    except Exception as e:
        # If anything goes wrong, create a simple plot
        y = x**2
        plt.figure(figsize=(10, 6))
        plt.plot(x, y, 'r--', linewidth=2, label='Default: f(x) = x²')
        plt.grid(True, alpha=0.3)
        plt.title(f'Error plotting "{expression}" - Showing default function', fontsize=14)
        plt.xlabel('x', fontsize=12)
        plt.ylabel('y', fontsize=12)
        plt.legend()
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return {
            'image': f'data:image/png;base64,{image_base64}',
            'expression': f'{expression} (error - showing default)',
            'analysis': {'error': str(e)}
        }

def extract_rose_parameters(expression):
    """Extract parameters a and n from polar expressions (rose curves, cardioids, etc.)"""
    expr = expression.lower()
    
    # Default values
    a = 1
    n = 1
    
    import re
    
    # Handle simple cardioids: r = 1 + cos(θ) or r = 1 - cos(θ)
    simple_cardioid = re.search(r'r\s*=\s*1\s*[+-]\s*cos', expr)
    if simple_cardioid:
        return 1, 1  # Standard cardioid parameters
        
    # Handle simple cardioids with sin: r = 1 + sin(θ) or r = 1 - sin(θ)
    simple_cardioid_sin = re.search(r'r\s*=\s*1\s*[+-]\s*sin', expr)
    if simple_cardioid_sin:
        return 1, 1  # Standard cardioid parameters
    
    # Handle scaled cardioids: r = a(1 + cos(θ)) or r = a(1 - cos(θ))
    cardioid_match = re.search(r'r\s*=\s*(\d+(?:\.\d+)?)\s*\*?\s*\(\s*1\s*[+-]\s*cos', expr)
    if cardioid_match:
        a = float(cardioid_match.group(1))
        return a, 1  # n=1 for cardioids
    
    # Handle cardioids: r = a + a*cos(θ) format
    cardioid_expanded = re.search(r'r\s*=\s*(\d+(?:\.\d+)?)\s*[+-]\s*\1\s*\*?\s*cos', expr)
    if cardioid_expanded:
        a = float(cardioid_expanded.group(1))
        return a, 1
    
    # Handle limacons: r = a + b*cos(θ)
    limacon_match = re.search(r'r\s*=\s*(\d+(?:\.\d+)?)\s*[+-]\s*(\d+(?:\.\d+)?)\s*\*?\s*cos', expr)
    if limacon_match:
        a = float(limacon_match.group(1))
        return a, 1
    
    # Handle rose curves: r = a*cos(n*θ) or r = a*sin(n*θ)
    rose_match = re.search(r'r\s*=\s*(\d+(?:\.\d+)?)\s*\*?\s*[cossin]+\s*\(\s*(\d+(?:\.\d+)?)\s*\*', expr)
    if rose_match:
        a = float(rose_match.group(1))
        n = float(rose_match.group(2))
        return a, n
    
    # Try to extract 'a' coefficient from general patterns
    a_match = re.search(r'r\s*=\s*(\d+(?:\.\d+)?)', expr)
    if a_match:
        a = float(a_match.group(1))
    
    # Try to extract 'n' from cos(nθ) or sin(nθ)
    n_match = re.search(r'[cossin]+\s*\(\s*(\d+(?:\.\d+)?)\s*\*?\s*[θϴtheta]', expr)
    if n_match:
        n = float(n_match.group(1))
    
    return a, n

def analyze_polar_function(theta, r, expression, a, n):
    """Complete analysis for rose curves and cardioids"""
    finite_r = r[np.isfinite(r)]
    
    if len(finite_r) == 0:
        return {'error': 'No finite values to analyze'}
    
    # Normalize expression for analysis
    expr_normalized = expression.lower().replace(' ', '')
    print(f"Analyzing expression: {expr_normalized}")
    
    # Check for cardioids first
    if any(pattern in expr_normalized for pattern in ['1+cos', '1-cos', '1+sin', '1-sin']):
        return analyze_cardioid_detailed(expression, finite_r, theta)
    
    # Check for limaçons
    elif any(pattern in expr_normalized for pattern in ['1+2*cos', '2+cos', '1+2*sin', '2+sin']):
        return analyze_limacon_detailed(expression, finite_r, theta)
    
    # Otherwise, it's a rose curve
    else:
        return analyze_rose_curve_detailed(expression, finite_r, theta)

def analyze_cardioid_detailed(expression, r_values, theta_values):
    """Detailed cardioid analysis following the reference"""
    try:
        # Determine cardioid characteristics
        clean_expr = expression.lower().replace(' ', '')
        
        amplitude = 1.0
        facing_direction = 'right'
        symmetry_axis = 'x-axis'
        
        # Analyze pattern
        if '1+cos' in clean_expr:
            facing_direction = 'right'
            symmetry_axis = 'x-axis'
            amp_match = re.search(r'(\d+\.?\d*)\*?\(1\+cos', clean_expr)
            amplitude = float(amp_match.group(1)) if amp_match else 1.0
        elif '1-cos' in clean_expr:
            facing_direction = 'left'
            symmetry_axis = 'x-axis'
            amp_match = re.search(r'(\d+\.?\d*)\*?\(1-cos', clean_expr)
            amplitude = float(amp_match.group(1)) if amp_match else 1.0
        elif '1+sin' in clean_expr:
            facing_direction = 'up'
            symmetry_axis = 'y-axis'
            amp_match = re.search(r'(\d+\.?\d*)\*?\(1\+sin', clean_expr)
            amplitude = float(amp_match.group(1)) if amp_match else 1.0
        elif '1-sin' in clean_expr:
            facing_direction = 'down'
            symmetry_axis = 'y-axis'
            amp_match = re.search(r'(\d+\.?\d*)\*?\(1-sin', clean_expr)
            amplitude = float(amp_match.group(1)) if amp_match else 1.0
        
        max_radius = float(np.max(np.abs(r_values))) if len(r_values) > 0 else 2 * amplitude
        min_radius = float(np.min(r_values)) if len(r_values) > 0 else 0.0
        
        return {
            'type': f'Cardioid ({facing_direction}-facing)',
            'curve_family': 'Cardioid (special case of Limaçon)',
            'facing_direction': facing_direction,
            'symmetry_axis': symmetry_axis,
            'amplitude': amplitude,
            'max_radius': max_radius,
            'min_radius': min_radius,
            'special_feature': 'sharp cusp at origin',
            'curve_description': f'Perfect heart shape facing {facing_direction}',
            'properties': [
                f'Heart-shaped curve facing {facing_direction}',
                f'Amplitude parameter: a = {amplitude}',
                f'Symmetry: {symmetry_axis}',
                f'Maximum radius: {max_radius:.2f}',
                f'Sharp cusp at origin',
                f'Named from Greek "kardia" (heart)'
            ]
        }
    except Exception as e:
        print(f"Error in cardioid analysis: {e}")
        return {
            'type': 'Cardioid',
            'properties': ['Heart-shaped polar curve'],
            'max_radius': 2.0
        }

def analyze_limacon_detailed(expression, r_values, theta_values):
    """Detailed limaçon analysis"""
    try:
        clean_expr = expression.lower().replace(' ', '')
        
        if '1+2*cos' in clean_expr:
            limacon_type = 'inner_loop'
            feature = 'inner loop inside heart (b > a)'
        elif '2+cos' in clean_expr:
            limacon_type = 'dimpled'
            feature = 'smooth dimple, no sharp cusp (a > b)'
        elif '1+2*sin' in clean_expr:
            limacon_type = 'inner_loop'
            feature = 'inner loop inside heart (b > a, rotated)'
        elif '2+sin' in clean_expr:
            limacon_type = 'dimpled'
            feature = 'smooth dimple, no sharp cusp (a > b, rotated)'
        else:
            limacon_type = 'general'
            feature = 'limaçon curve'
        
        max_radius = float(np.max(np.abs(r_values))) if len(r_values) > 0 else 3.0
        min_radius = float(np.min(r_values)) if len(r_values) > 0 else 0.0
        
        return {
            'type': f'Limaçon ({limacon_type})',
            'curve_family': 'Limaçon family',
            'limacon_type': limacon_type,
            'max_radius': max_radius,
            'min_radius': min_radius,
            'special_feature': feature,
            'properties': [
                f'Limaçon with {feature}',
                f'Maximum radius: {max_radius:.2f}',
                f'Minimum radius: {min_radius:.2f}',
                'Member of limaçon family'
            ]
        }
    except Exception as e:
        print(f"Error in limaçon analysis: {e}")
        return {
            'type': 'Limaçon',
            'properties': ['Limaçon polar curve'],
            'max_radius': 3.0
        }

def analyze_rose_curve_detailed(expression, r_values, theta_values):
    """Detailed rose curve analysis"""
    try:
        # Extract amplitude and k value
        amplitude = 1.0
        k = 1
        trig_func = 'cos'
        
        # Pattern matching for analysis
        import re
        
        # Pattern 1: r = a*cos(k*theta) or r = a*sin(k*theta)
        coeff_pattern = r'r=(\d+(?:\.\d+)?)\*?(cos|sin)\((\d+)\*theta\)'
        match = re.search(coeff_pattern, expression.replace(' ', ''))
        if match:
            amplitude = float(match.group(1))
            trig_func = match.group(2)
            k = int(match.group(3))
        else:
            # Pattern 2: r = cos(k*theta) or r = sin(k*theta)
            simple_pattern = r'r=(cos|sin)\((\d+)\*theta\)'
            match = re.search(simple_pattern, expression.replace(' ', ''))
            if match:
                trig_func = match.group(1)
                k = int(match.group(2))
            else:
                # Pattern 3: r = cos(theta) or r = sin(theta)
                single_pattern = r'r=(cos|sin)\(theta\)'
                match = re.search(single_pattern, expression.replace(' ', ''))
                if match:
                    trig_func = match.group(1)
                    k = 1
        
        # Apply Rose Curve Rule: Odd k → k petals, Even k → 2k petals
        petals = k if k % 2 != 0 else 2 * k
        
        # Determine symmetry
        symmetry = 'symmetric about x-axis' if trig_func == 'cos' else 'symmetric about y-axis (rotated)'
        
        # Shape description
        shape_descriptions = {
            1: 'Single petal (oval-like loop)',
            3: '3-petal rose (propeller/Mercedes logo shape)',
            4: '4-petal rose (four-leaf clover shape)',
            5: '5-petal rose (pentagonal flower)',
            8: '8-petal rose (daisy-like flower)',
            12: '12-petal rose (chrysanthemum pattern)',
        }
        
        shape_desc = shape_descriptions.get(petals, f'{petals}-petal rose curve')
        
        max_radius = float(np.max(np.abs(r_values))) if len(r_values) > 0 else amplitude
        
        return {
            'type': f'Rose Curve ({petals}-petal)',
            'amplitude': amplitude,
            'k_value': k,
            'petals': petals,
            'trig_function': trig_func,
            'max_radius': max_radius,
            'min_radius': 0.0,
            'symmetry': symmetry,
            'shape_description': shape_desc,
            'petal_rule': f'k={k} is {"odd" if k % 2 != 0 else "even"} → {petals} petals',
            'properties': [
                shape_desc,
                f'Amplitude (a) = {amplitude}',
                f'Petal parameter (k) = {k}',
                f'Rule: {"k petals (odd k)" if k % 2 != 0 else "2k petals (even k)"}',
                symmetry,
                f'Maximum radius: {max_radius:.2f}'
            ]
        }
    except Exception as e:
        print(f"Error in rose curve analysis: {e}")
        return {
            'type': 'Rose Curve',
            'properties': ['Rose curve pattern'],
            'max_radius': 1.0
        }

def analyze_function(x, y, expression):
    """Perform basic function analysis"""
    finite_y = y[np.isfinite(y)]
    
    if len(finite_y) == 0:
        return {'error': 'No finite values to analyze'}
    
    analysis = {
        'domain': f'Real numbers ({x.min():.1f} to {x.max():.1f} shown)',
        'range': f'Approximately {finite_y.min():.2f} to {finite_y.max():.2f}',
        'type': classify_function(expression),
        'properties': []
    }
    
    # Check for symmetry
    if len(finite_y) > 1:
        if np.allclose(finite_y, finite_y[::-1], rtol=0.1):
            analysis['properties'].append('Even function (symmetric about y-axis)')
        elif np.allclose(finite_y, -finite_y[::-1], rtol=0.1):
            analysis['properties'].append('Odd function (symmetric about origin)')
    
    # Check for monotonicity
    if np.all(np.diff(finite_y) >= 0):
        analysis['properties'].append('Monotonically increasing')
    elif np.all(np.diff(finite_y) <= 0):
        analysis['properties'].append('Monotonically decreasing')
    
    return analysis

def classify_function(expression):
    """Classify the type of function based on expression"""
    expr = expression.lower()
    
    if 'sin' in expr or 'cos' in expr or 'tan' in expr:
        return 'Trigonometric function'
    elif 'exp' in expr or 'e**' in expr:
        return 'Exponential function'
    elif 'log' in expr or 'ln' in expr:
        return 'Logarithmic function'
    elif '**' in expr or '^' in expr:
        return 'Power function'
    elif 'sqrt' in expr:
        return 'Square root function'
    elif any(op in expr for op in ['+', '-', '*', '/']):
        return 'Algebraic function'
    else:
        return 'Mathematical function'

def parse_natural_language(user_input: str) -> Dict:
    """
    Convert natural language input to mathematical expressions
    Examples:
    - "draw rose with 4 petals" -> "r = cos(2*theta)"
    - "create a circle" -> "r = 1"  
    - "make a sine wave" -> "sin(x)"
    """
    
    input_lower = user_input.lower().strip()
    
    # Rose curve patterns
    rose_patterns = [
        (r'rose.*?(\d+).*?petal', lambda match: generate_rose_equation(int(match.group(1)))),
        (r'(\d+).*?petal.*?rose', lambda match: generate_rose_equation(int(match.group(1)))),
        (r'rose.*?flower', lambda: "r = cos(2*theta)"),  # Default 4-petal rose
        (r'flower.*?pattern', lambda: "r = cos(3*theta)"),  # Default 3-petal
    ]
    
    # Basic shapes
    shape_patterns = [
        (r'circle', lambda: "r = 1"),
        (r'heart.*?shape|cardioid', lambda: "r = 1 + cos(theta)"),
        (r'spiral', lambda: "r = theta"),
        (r'figure.*?eight|lemniscate', lambda: "r = sqrt(2*cos(2*theta))"),
        (r'limaçon|lima.*?con', lambda: "r = 2 + cos(theta)"),
    ]
    
    # Wave functions  
    wave_patterns = [
        (r'sine.*?wave|sin.*?function', lambda: "sin(x)"),
        (r'cosine.*?wave|cos.*?function', lambda: "cos(x)"),
        (r'tangent.*?wave|tan.*?function', lambda: "tan(x)"),
        (r'wave.*?function', lambda: "sin(x)"),
    ]
    
    # Polynomial functions
    poly_patterns = [
        (r'parabola|quadratic', lambda: "x^2"),
        (r'cubic.*?function', lambda: "x^3"),
        (r'linear.*?function|straight.*?line', lambda: "x"),
        (r'square.*?root', lambda: "sqrt(x)"),
    ]
    
    # Advanced functions
    advanced_patterns = [
        (r'exponential.*?growth', lambda: "exp(x)"),
        (r'logarithm.*?function|log.*?function', lambda: "log(x)"),
        (r'bell.*?curve|gaussian', lambda: "exp(-x^2)"),
        (r'absolute.*?value', lambda: "abs(x)"),
    ]
    
    # Check all patterns
    all_patterns = rose_patterns + shape_patterns + wave_patterns + poly_patterns + advanced_patterns
    
    for pattern, generator in all_patterns:
        match = re.search(pattern, input_lower)
        if match:
            try:
                equation = generator(match) if 'match' in str(generator.__code__.co_varnames) else generator()
                return {
                    'success': True,
                    'equation': equation,
                    'interpretation': f'Interpreted "{user_input}" as: {equation}',
                    'type': determine_equation_type(equation),
                    'suggested_function_type': '2D' if any(x in equation for x in ['r =', 'sin(x)', 'cos(x)']) else '2D'
                }
            except:
                continue
    
    # If no pattern matches, try to extract numbers for rose curves
    numbers = re.findall(r'\d+', input_lower)
    if ('rose' in input_lower or 'petal' in input_lower) and numbers:
        petal_count = int(numbers[0])
        equation = generate_rose_equation(petal_count)
        return {
            'success': True,
            'equation': equation,
            'interpretation': f'Created rose with {petal_count} petals: {equation}',
            'type': 'polar',
            'suggested_function_type': '2D'
        }
    
    # Advanced NLP: Check for mathematical terms
    if any(term in input_lower for term in ['graph', 'plot', 'draw', 'show', 'create', 'make']):
        return {
            'success': False,
            'error': 'Could not understand the request. Try examples like:',
            'suggestions': [
                '"draw rose with 4 petals"',
                '"create a circle"', 
                '"make a sine wave"',
                '"show parabola"',
                '"plot heart shape"'
            ]
        }
    
    return {
        'success': False,
        'error': 'Natural language not recognized. Please use mathematical notation or try examples above.',
        'suggestions': ['r = cos(2*theta)', 'sin(x)', 'x^2']
    }

def generate_rose_equation(petal_count: int) -> str:
    """Generate rose equation based on desired petal count"""
    if petal_count <= 0:
        return "r = cos(2*theta)"  # Default
    
    # Rose curve mathematics:
    # - If n is even: 2n petals
    # - If n is odd: n petals
    
    if petal_count % 2 == 0:
        # Even number of petals: n = petals/2
        n = petal_count // 2
    else:
        # Odd number of petals: n = petals
        n = petal_count
    
    return f"r = cos({n}*theta)"

def determine_equation_type(equation: str) -> str:
    """Determine if equation is polar, cartesian, etc."""
    eq_lower = equation.lower()
    if 'r =' in eq_lower or 'theta' in eq_lower:
        return 'polar'
    elif any(func in eq_lower for func in ['sin(x)', 'cos(x)', 'tan(x)']):
        return 'cartesian_trig'
    else:
        return 'cartesian'

def generate_ai_explanation(expression, model_type, analysis):
    """Generate detailed AI explanation using Gemini API"""
    if not model or not GEMINI_API_KEY:
        return {
            'explanation': 'AI explanations are not available. Please set GEMINI_API_KEY environment variable.',
            'mathematical_insights': 'Advanced analysis requires API key configuration.',
            'real_world_applications': 'Please configure Gemini API for detailed explanations.'
        }
    
    try:
        # Create a comprehensive prompt for Gemini
        prompt = f"""
        You are a mathematics professor explaining a 3D mathematical model to students. 
        
        Mathematical Expression: {expression}
        Model Type: {model_type}
        Analysis Data: {analysis}
        
        Please provide a detailed, educational explanation covering:
        
        1. **Mathematical Foundation**: Explain what this equation represents mathematically
        2. **3D Visualization**: Describe what the 3D model shows and why it looks the way it does
        3. **Key Properties**: Highlight important mathematical properties (symmetry, periodicity, etc.)
        4. **Real-World Applications**: Where might this type of curve/surface be found in nature, engineering, or science?
        5. **Interesting Facts**: Share fascinating mathematical insights about this type of function
        
        Keep the explanation accessible but mathematically accurate. Use clear, engaging language.
        Format your response as a structured explanation that would help students understand both the mathematics and the visualization.
        """
        
        # Generate response using Gemini
        response = model.generate_content(prompt)
        
        # Parse the response (you might want to structure this better)
        explanation_text = response.text
        
        # Split into sections (this is a simple approach - you could make it more sophisticated)
        sections = explanation_text.split('\n\n')
        
        return {
            'full_explanation': explanation_text,
            'mathematical_foundation': extract_section(explanation_text, 'Mathematical Foundation'),
            'visualization_description': extract_section(explanation_text, '3D Visualization'),
            'key_properties': extract_section(explanation_text, 'Key Properties'),
            'real_world_applications': extract_section(explanation_text, 'Real-World Applications'),
            'interesting_facts': extract_section(explanation_text, 'Interesting Facts'),
            'ai_powered': True
        }
        
    except Exception as e:
        print(f"Error generating AI explanation: {e}")
        return {
            'explanation': f'Error generating AI explanation: {str(e)}',
            'mathematical_insights': 'AI analysis temporarily unavailable.',
            'real_world_applications': 'Please try again later.',
            'ai_powered': False
        }

def extract_section(text, section_name):
    """Extract a specific section from the AI response"""
    try:
        # Simple text extraction - you could make this more robust
        lines = text.split('\n')
        in_section = False
        section_content = []
        
        for line in lines:
            if section_name.lower() in line.lower() and ('**' in line or '#' in line):
                in_section = True
                continue
            elif in_section and (line.strip().startswith('**') or line.strip().startswith('#')):
                break
            elif in_section and line.strip():
                section_content.append(line.strip())
        
        return ' '.join(section_content) if section_content else f"Information about {section_name} is included in the full explanation."
    except:
        return f"See full explanation for {section_name} details."

def generate_3d_model(expression):
    """Generate 3D visualization - handles both Cartesian and Polar equations"""
    try:
        from mpl_toolkits.mplot3d import Axes3D
        
        # Check if this is a polar equation
        is_polar = detect_polar_equation(expression)
        
        if is_polar:
            return generate_3d_polar_surface(expression)
        else:
            return generate_3d_cartesian_surface(expression)
            
    except Exception as e:
        print(f"Error in 3D generation: {e}")
        return generate_3d_fallback(expression)

def generate_3d_polar_surface(expression):
    """Generate 3D surface from polar equation by creating surface of revolution"""
    try:
        from mpl_toolkits.mplot3d import Axes3D
        
        # Extract parameters from rose curve
        a, n = extract_rose_parameters(expression)
        
        # Create theta and z values
        theta = np.linspace(0, 4*np.pi, 100)
        z = np.linspace(-2, 2, 30)  # Height range for 3D surface
        THETA, Z = np.meshgrid(theta, z)
        
        # Clean the expression for evaluation
        expr_clean = expression.lower()
        expr_clean = expr_clean.replace('r =', '').replace('r=', '').strip()
        expr_clean = expr_clean.replace('θ', 'theta').replace('ϴ', 'theta')
        
        # Evaluate the polar expression for each theta
        r_values = []
        for t in theta:
            try:
                r_val = safe_eval_polar_expression(expr_clean, np.array([t]), a, n)[0]
                r_values.append(r_val if np.isfinite(r_val) and abs(r_val) < 10 else 0)
            except:
                r_values.append(0)
        
        r_values = np.array(r_values)
        
        # Create 3D surface by replicating the polar curve at different z levels
        R = np.tile(r_values, (len(z), 1))
        
        # Convert to Cartesian coordinates
        X = R * np.cos(THETA)
        Y = R * np.sin(THETA)
        
        # Create 3D plot
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        # Create surface plot with color mapping based on radius
        surf = ax.plot_surface(X, Y, Z, facecolors=plt.cm.viridis(R/np.max(R)), 
                              alpha=0.8, linewidth=0, antialiased=True)
        
        # Add wireframe for the original 2D curve at z=0
        r_2d = np.array(r_values)
        x_2d = r_2d * np.cos(theta)
        y_2d = r_2d * np.sin(theta)
        z_2d = np.zeros_like(theta)
        ax.plot(x_2d, y_2d, z_2d, 'r-', linewidth=3, label='Original 2D curve')
        
        # Set labels and title
        ax.set_title(f'3D Surface of Revolution: {expression}', fontsize=14, fontweight='bold')
        ax.set_xlabel('x', fontsize=12)
        ax.set_ylabel('y', fontsize=12)
        ax.set_zlabel('z', fontsize=12)
        ax.legend()
        
        # Set equal aspect ratio
        max_range = np.max(np.abs(r_values)) * 1.1
        ax.set_xlim([-max_range, max_range])
        ax.set_ylim([-max_range, max_range])
        ax.set_zlim([-2, 2])
        
        # Convert to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return {
            'image': f'data:image/png;base64,{image_base64}',
            'expression': expression,
            'analysis': {
                'type': '3D Surface of Revolution from Polar Curve',
                'description': f'Polar equation {expression} extruded in z-direction',
                'petals': f'{2*n if n%2==0 else n} petals' if 'cos' in expression else 'Complex pattern',
                'max_radius': f'{np.max(np.abs(r_values)):.2f}',
                'z_range': '[-2, 2]'
            },
            'ai_explanation': generate_ai_explanation(
                expression, 
                '3D Surface of Revolution from Polar Curve',
                {
                    'type': '3D Surface of Revolution from Polar Curve',
                    'petals': f'{2*n if n%2==0 else n} petals' if 'cos' in expression else 'Complex pattern',
                    'max_radius': f'{np.max(np.abs(r_values)):.2f}',
                    'z_range': '[-2, 2]'
                }
            )
        }
        
    except Exception as e:
        print(f"Error in polar 3D generation: {e}")
        return generate_3d_fallback(expression)

def generate_3d_cartesian_surface(expression):
    """Generate 3D surface plot for Cartesian functions"""
    try:
        from mpl_toolkits.mplot3d import Axes3D
        
        # Create meshgrid for 3D plot
        x = np.linspace(-5, 5, 50)
        y = np.linspace(-5, 5, 50)
        X, Y = np.meshgrid(x, y)
        
        # For 3D, we'll treat the expression as z = f(x,y)
        try:
            # Replace x and y in expression for 3D
            expr_3d = expression.lower().replace('^', '**')
            if 'y' not in expr_3d:
                # If no y in expression, create a 3D version
                expr_3d = expr_3d.replace('x', '(X+Y)')
            else:
                expr_3d = expr_3d.replace('x', 'X').replace('y', 'Y')
            
            # Safe evaluation for 3D
            safe_dict_3d = {
                "X": X, "Y": Y,
                "sin": np.sin, "cos": np.cos, "tan": np.tan,
                "exp": np.exp, "log": np.log, "sqrt": np.sqrt,
                "abs": np.abs, "pi": np.pi, "e": np.e,
                "__builtins__": {}
            }
            
            Z = eval(expr_3d, safe_dict_3d)
            
        except:
            # Fallback to a simple 3D function
            Z = X**2 + Y**2
            
        # Create 3D plot
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Create surface plot
        surf = ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.7)
        
        ax.set_title(f'3D Surface: f(x,y) = {expression}', fontsize=14, fontweight='bold')
        ax.set_xlabel('x', fontsize=12)
        ax.set_ylabel('y', fontsize=12)
        ax.set_zlabel('z', fontsize=12)
        
        # Add colorbar
        fig.colorbar(surf)
        
        # Convert to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return {
            'image': f'data:image/png;base64,{image_base64}',
            'expression': expression,
            'analysis': {
                'type': '3D Cartesian Surface',
                'description': f'Surface plot of z = {expression}',
                'domain': 'x,y ∈ [-5, 5]'
            },
            'ai_explanation': generate_ai_explanation(
                expression,
                '3D Cartesian Surface',
                {
                    'type': '3D Cartesian Surface',
                    'description': f'Surface plot of z = {expression}',
                    'domain': 'x,y ∈ [-5, 5]'
                }
            )
        }
        
    except Exception as e:
        print(f"Error in Cartesian 3D generation: {e}")
        return generate_3d_fallback(expression)

def generate_3d_fallback(expression):
    """Generate fallback 3D plot when other methods fail"""
    try:
        from mpl_toolkits.mplot3d import Axes3D
        
        x = np.linspace(-5, 5, 50)
        y = np.linspace(-5, 5, 50)
        X, Y = np.meshgrid(x, y)
        Z = X**2 + Y**2  # Simple paraboloid
        
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        surf = ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.7)
        
        ax.set_title(f'3D Fallback for: {expression}', fontsize=14, fontweight='bold')
        ax.set_xlabel('x', fontsize=12)
        ax.set_ylabel('y', fontsize=12)
        ax.set_zlabel('z', fontsize=12)
        fig.colorbar(surf)
        
        # Convert to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return {
            'image': f'data:image/png;base64,{image_base64}',
            'expression': f'{expression} (fallback)',
            'analysis': {
                'type': '3D Fallback Surface',
                'description': 'Default paraboloid z = x² + y²',
                'note': f'Could not render "{expression}" in 3D'
            }
        }
        
    except Exception as e:
        # Ultimate fallback
        return {
            'image': None,
            'expression': expression,
            'analysis': {'error': f'Failed to generate 3D plot: {str(e)}'}
        }

def generate_3d_fallback_animated(expression):
    """Generate animated fallback 3D plot when other methods fail"""
    try:
        from mpl_toolkits.mplot3d import Axes3D
        
        x = np.linspace(-5, 5, 50)
        y = np.linspace(-5, 5, 50)
        X, Y = np.meshgrid(x, y)
        Z_full = X**2 + Y**2  # Simple paraboloid
        
        # Create animated growing effect
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Animation parameters
        frames = 30  # Number of animation frames (2 seconds at 15 fps)
        z_min, z_max = np.min(Z_full), np.max(Z_full)
        growth_levels = np.linspace(z_min, z_max, frames)
        
        def animate_frame(frame):
            ax.clear()
            
            # Calculate current height for growing effect
            current_max_height = growth_levels[frame]
            
            # Clip Z values to current height (growing effect)
            Z_clipped = np.where(Z_full <= current_max_height, Z_full, np.nan)
            
            # Create surface plot
            surf = ax.plot_surface(X, Y, Z_clipped, cmap='viridis', alpha=0.7)
            
            # Set labels and title
            ax.set_title(f'Animated Fallback 3D: {expression}', fontsize=14, fontweight='bold')
            ax.set_xlabel('x', fontsize=12)
            ax.set_ylabel('y', fontsize=12)
            ax.set_zlabel('z', fontsize=12)
            
            # Set consistent axis limits
            ax.set_xlim([-5, 5])
            ax.set_ylim([-5, 5])
            ax.set_zlim([z_min, z_max])
            
            # Add progress indicator
            progress = (frame + 1) / frames * 100
            ax.text2D(0.02, 0.98, f'Growth: {progress:.0f}%', transform=ax.transAxes, 
                     fontsize=10, verticalalignment='top',
                     bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # Create animation
        anim = animation.FuncAnimation(fig, animate_frame, frames=frames, interval=67, repeat=True)
        
        # Save as GIF
        gif_buffer = BytesIO()
        writer = PillowWriter(fps=15)
        anim.save(gif_buffer, writer=writer)
        gif_buffer.seek(0)
        gif_base64 = base64.b64encode(gif_buffer.getvalue()).decode()
        plt.close()
        
        return {
            'image': f'data:image/gif;base64,{gif_base64}',
            'expression': f'{expression} (animated fallback)',
            'animation': True,
            'duration': '2 seconds',
            'analysis': {
                'type': '3D Animated Fallback Surface',
                'description': 'Default animated paraboloid z = x² + y²',
                'note': f'Could not render "{expression}" in 3D - showing animated fallback',
                'animation_frames': frames,
                'growth_effect': f'Surface grows from {z_min:.1f} to {z_max:.1f}'
            }
        }
        
    except Exception as e:
        # Ultimate fallback
        return {
            'image': None,
            'expression': expression,
            'animation': False,
            'analysis': {'error': f'Failed to generate animated 3D plot: {str(e)}'}
        }

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Flask backend is running successfully!'
    })

@app.route('/api/parse-language', methods=['POST'])
def parse_natural_language_endpoint():
    """Endpoint to parse natural language input"""
    data = request.get_json()
    user_input = data.get('input', '')
    
    print(f"Natural language input: {user_input}")
    
    if not user_input:
        return jsonify({
            'success': False,
            'error': 'No input provided'
        }), 400
    
    try:
        result = parse_natural_language(user_input)
        print(f"Parsed result: {result}")
        return jsonify(result)
    except Exception as e:
        print(f"Error parsing: {e}")
        return jsonify({
            'success': False,
            'error': f'Error parsing input: {str(e)}'
        }), 400

if __name__ == '__main__':
    print("Starting Flask backend server...")
    print("Graph generation API ready!")
    print("Access at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
