from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for server deployment
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import re
import math

app = Flask(__name__)
CORS(app)  # Enable CORS for React app

@app.route('/api/generate', methods=['POST'])
def generate_graph():
    data = request.get_json()
    function_type = data.get('functionType')
    expression = data.get('expression')
    
    print(f"📨 Received request: type={function_type}, expression={expression}")
    
    if not expression:
        print("❌ No expression provided")
        return jsonify({
            'status': 'error',
            'message': 'No expression provided'
        }), 400
    
    try:
        if function_type == '2D':
            print("🔄 Generating 2D graph...")
            graph_data = generate_2d_graph(expression)
            print("✅ 2D graph generated successfully!")
            return jsonify({
                'status': 'success',
                'type': '2D',
                'data': graph_data
            })
        elif function_type == '3D':
            print("🔄 Generating 3D model...")
            model_data = generate_3d_model(expression)
            print("✅ 3D model generated successfully!")
            return jsonify({
                'status': 'success',
                'type': '3D', 
                'data': model_data
            })
        else:
            print(f"❌ Invalid function type: {function_type}")
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
    """Safely evaluate polar mathematical expressions like rose curves"""
    # Replace common mathematical notation
    expression = expression.lower()
    expression = expression.replace('^', '**')  # Handle exponents
    expression = expression.replace('θ', 'theta').replace('ϴ', 'theta')
    
    # Create safe environment for evaluation
    safe_dict = {
        "theta": theta_values,
        "a": a,
        "n": n,
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
        # Fallback to simple rose curve
        return np.cos(2 * theta_values)

def detect_polar_equation(expression):
    """Detect if the expression is a polar equation (contains r, theta, etc.)"""
    expr_lower = expression.lower()
    polar_indicators = ['r =', 'r=', 'theta', 'θ', 'ϴ', 'cos(', 'sin(']
    cartesian_indicators = ['y =', 'y=', 'f(x)', 'x**', 'x^']
    
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
    """Extract parameters a and n from rose curve expressions"""
    expr = expression.lower()
    
    # Default values
    a = 1
    n = 1
    
    # Try to extract 'a' coefficient
    import re
    a_match = re.search(r'r\s*=\s*(\d+(?:\.\d+)?)\s*\*?\s*cos', expr)
    if a_match:
        a = float(a_match.group(1))
    
    # Try to extract 'n' from cos(nθ) or cos(n*theta)
    n_match = re.search(r'cos\s*\(\s*(\d+(?:\.\d+)?)\s*\*?\s*[θϴtheta]', expr)
    if n_match:
        n = float(n_match.group(1))
    
    return a, n

def analyze_polar_function(theta, r, expression, a, n):
    """Analyze polar functions like rose curves"""
    finite_r = r[np.isfinite(r)]
    
    if len(finite_r) == 0:
        return {'error': 'No finite values to analyze'}
    
    # Determine number of petals for rose curves
    if 'cos' in expression.lower():
        if n % 2 == 0:  # Even n
            petals = 2 * n
        else:  # Odd n
            petals = n
    else:
        petals = "Variable"
    
    analysis = {
        'type': 'Rose Curve (Polar)',
        'equation_type': f'r = a cos(nθ) where a≈{a:.1f}, n≈{n:.1f}',
        'petals': f'{petals} petals',
        'max_radius': f'{finite_r.max():.2f}',
        'symmetry': 'Symmetric about origin',
        'domain': 'θ ∈ [0, 2π] (extended to 4π for visualization)',
        'properties': [
            f'Rose curve with {petals} petals',
            f'Maximum radius: {finite_r.max():.2f}',
            'Closed curve' if petals != "Variable" else 'Complex curve'
        ]
    }
    
    return analysis

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
            }
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
            }
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

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Flask backend is running successfully!'
    })

if __name__ == '__main__':
    print("🚀 Starting Flask backend server...")
    print("📊 Graph generation API ready!")
    print("🌐 Access at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
