# 3D Polar Equation Examples

Here are some interesting polar equations to test the 3D modeling capabilities:

## Basic Examples

1. **Circle**: `r = 2`
   - Creates a circular surface in 3D

2. **Limacon**: `r = 2 + cos(theta)`
   - Creates a beautiful 3D limacon shape

3. **Rose Curve**: `r = 3 * cos(4 * theta)`
   - Creates a rose-like surface with 8 petals

4. **Spiral**: `r = theta / 10`
   - Creates a 3D spiral surface

5. **Heart (Cardioid)**: `r = 1 - cos(theta)`
   - Creates a heart-shaped 3D surface

## Advanced Examples

6. **Complex Rose**: `r = 2 * sin(3 * theta)`
   - Creates a 3-petal rose surface

7. **Butterfly**: `r = exp(cos(theta)) - 2 * cos(4 * theta) + sin(theta / 12) ** 5`
   - Creates a butterfly-like surface

8. **Complex Spiral**: `r = sin(theta) + theta / 20`
   - Combines oscillation with spiral growth

## Testing Instructions

1. Open the application at http://localhost:5174
2. Switch to 3D mode
3. Select "Interactive (WebGL)" for best visualization
4. Enter any of the above equations in the function input
5. Observe the 3D model generation

## Features to Test

- **Rotation**: Use mouse to rotate the 3D model
- **Zoom**: Scroll to zoom in/out
- **Pan**: Right-click and drag to pan
- **Animation**: Toggle animation for rotating view
- **Static vs WebGL**: Compare both rendering modes
