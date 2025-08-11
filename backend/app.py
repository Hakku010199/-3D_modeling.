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
import os
from typing import Dict, List, Tuple
# import google.generativeai as genai  # Temporarily commented out

app = Flask(__name__)
CORS(app)  # Enable CORS for React app

# Configure Gemini AI (you'll need to set your API key)
# Set your API key: export GEMINI_API_KEY="your_api_key_here"
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
model = None  # Temporarily disabled
print("⚠️  Gemini AI temporarily disabled. Basic graph generation will work.")

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
    
    # Handle multiple theta formats
    expression = expression.replace('θ', 'theta')  # Greek theta
    expression = expression.replace('ϴ', 'theta')  # Alternative theta
    expression = expression.replace('t)', 'theta)')  # t as theta
    expression = expression.replace('(t', '(theta')  # t as theta
    expression = expression.replace(' t ', ' theta ')  # standalone t
    expression = expression.replace('*t*', '*theta*')  # t between operators
    expression = expression.replace('+t+', '+theta+')  # t with plus
    expression = expression.replace('-t-', '-theta-')  # t with minus
    
    # Create safe environment for evaluation
    safe_dict = {
        "theta": theta_values,
        "t": theta_values,  # Also accept 't' as theta
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
    polar_indicators = ['r =', 'r=', 'theta', 'θ', 'ϴ', 'cos(', 'sin(', 'cos(t)', 'sin(t)', 'cos(theta)', 'sin(theta)']
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
    
    print(f"🗣️  Natural language input: {user_input}")
    
    if not user_input:
        return jsonify({
            'success': False,
            'error': 'No input provided'
        }), 400
    
    try:
        result = parse_natural_language(user_input)
        print(f"✅ Parsed result: {result}")
        return jsonify(result)
    except Exception as e:
        print(f"❌ Error parsing: {e}")
        return jsonify({
            'success': False,
            'error': f'Error parsing input: {str(e)}'
        }), 400

if __name__ == '__main__':
    print("🚀 Starting Flask backend server...")
    print("📊 Graph generation API ready!")
    print("🌐 Access at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
