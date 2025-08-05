# Flask Backend for Graph UI React App

This is the Flask backend that provides graph generation APIs for the React frontend.

## Features

- **2D Graph Generation**: Creates matplotlib plots for mathematical expressions
- **3D Surface Plots**: Generates 3D visualizations 
- **Expression Analysis**: Provides function analysis and properties
- **CORS Enabled**: Ready for React frontend integration
- **Error Handling**: Graceful fallbacks for invalid expressions

## API Endpoints

### POST /api/generate
Generates graphs based on mathematical expressions.

**Request Body:**
```json
{
  "functionType": "2D" | "3D",
  "expression": "x^2" | "sin(x)" | "cos(x)" | etc.
}
```

**Response:**
```json
{
  "status": "success",
  "type": "2D",
  "data": {
    "image": "data:image/png;base64,...",
    "expression": "x^2",
    "analysis": {...}
  }
}
```

### GET /api/health
Health check endpoint.

## Installation

1. Create virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
python app.py
```

The server will start on `http://localhost:5000`

## Supported Mathematical Expressions

- **Basic operations**: +, -, *, /
- **Exponents**: x^2, x**3
- **Trigonometric**: sin(x), cos(x), tan(x)
- **Exponential**: exp(x), e**x
- **Logarithmic**: log(x), ln(x)
- **Square root**: sqrt(x)
- **Constants**: pi, e

## Examples

- `x^2` - Parabola
- `sin(x)` - Sine wave
- `cos(x)` - Cosine wave
- `exp(x)` - Exponential growth
- `log(x)` - Logarithmic curve
- `x^3 - 2*x` - Cubic polynomial
