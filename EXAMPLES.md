# 📐 Complete Graph Examples Collection

Welcome to your comprehensive mathematical curve visualization system! Here are all the supported curve types with practical examples.

---

## 🌹 **Rose Curves (r = a·cos(nθ) or r = a·sin(nθ))**

### Basic Rose Curves
```
r = cos(theta)           # Simple 2-petal rose
r = sin(theta)           # 2-petal rose (rotated)
r = cos(2*theta)         # 4-petal rose
r = sin(2*theta)         # 4-petal rose (rotated 45°)
r = cos(3*theta)         # 3-petal rose
r = sin(3*theta)         # 3-petal rose (rotated)
r = cos(4*theta)         # 8-petal rose
r = sin(4*theta)         # 8-petal rose
```

### Scaled Rose Curves
```
r = 2*cos(theta)         # Larger 2-petal rose
r = 3*sin(2*theta)       # Large 4-petal rose
r = 5*cos(4*theta)       # Large 8-petal rose
r = 4*sin(3*theta)       # Large 3-petal rose
```

### Advanced Rose Patterns
```
r = cos(5*theta)         # 5-petal rose
r = cos(6*theta)         # 12-petal rose
r = cos(7*theta)         # 7-petal rose
r = sin(8*theta)         # 16-petal rose
```

**Mathematical Rule**: 
- If n is odd → n petals
- If n is even → 2n petals

---

## ❤️ **Cardioids (Heart Shapes)**

### Basic Cardioids
```
r = 1 + cos(theta)       # Classic cardioid (heart pointing right)
r = 1 - cos(theta)       # Inverted cardioid (heart pointing left)
r = 1 + sin(theta)       # Rotated cardioid (heart pointing up)
r = 1 - sin(theta)       # Rotated cardioid (heart pointing down)
```

### Scaled Cardioids
```
r = 2 + 2*cos(theta)     # Large cardioid
r = 3 + 3*sin(theta)     # Extra large cardioid
r = 0.5 + 0.5*cos(theta) # Small cardioid
```

---

## 🌀 **Archimedean Spirals (r = a + bθ)**

### Basic Spirals
```
r = theta                # Simple spiral (a=0, b=1)
r = 2*theta              # Faster growing spiral
r = 0.5*theta            # Slower growing spiral
r = -theta               # Clockwise spiral
```

### Offset Spirals
```
r = 1 + theta            # Spiral starting at distance 1
r = 2 + theta            # Spiral starting at distance 2
r = 5 + 2*theta          # Large offset, fast growth
r = 3 + 0.5*theta        # Large offset, slow growth
```

### Special Spiral Patterns
```
r = theta*cos(theta)     # Modulated spiral (wavy)
r = theta*sin(theta)     # Sine-modulated spiral
r = theta*sin(2*theta)   # Flower spiral pattern
r = theta*cos(3*theta)   # Triple-frequency wavy spiral
```

---

## 🌀 **Logarithmic Spirals (Spira Mirabilis) - r = a·e^(b·θ)**

### Basic Logarithmic Spirals

#### 1. Slowly Expanding Spiral
```
r = exp(0.1*theta)       # r = e^(0.1θ) - gentle outward growth
```
**Properties**: Moderate expansion, classical shell pattern, pitch angle ≈ 84.3°

#### 2. Faster Outward Spiral  
```
r = exp(0.3*theta)       # r = e^(0.3θ) - rapid outward expansion
```
**Properties**: Quick growth, wide arm spacing, pitch angle ≈ 73.3°

#### 3. Inward Spiral (Shrinking)
```
r = 5*exp(-0.2*theta)    # r = 5e^(-0.2θ) - contracts toward center
```
**Properties**: Starts large (r=5), shrinks exponentially inward

#### 4. Very Tight Spiral
```
r = 2*exp(0.05*theta)    # r = 2e^(0.05θ) - extremely slow growth
```
**Properties**: Almost circular, very gentle expansion

#### 5. Wide Outward Spiral
```
r = 0.5*exp(0.5*theta)   # r = 0.5e^(0.5θ) - rapid arm separation
```
**Properties**: Fast expansion, arms spread far apart quickly

### Advanced Logarithmic Spirals

#### 6. Very Tight Inward Spiral
```
r = 10*exp(-0.3*theta)   # r = 10e^(-0.3θ) - rapid inward contraction
```
**Properties**: Starts very large, contracts quickly to center

#### 7. Balanced Spiral (Artistic)
```
r = 3*exp(0.15*theta)    # r = 3e^(0.15θ) - smooth architectural spiral
```
**Properties**: Aesthetically pleasing, often used in design and tiling

#### 8. Slowly Decaying Spiral
```
r = 4*exp(-0.05*theta)   # r = 4e^(-0.05θ) - gentle inward drift
```
**Properties**: Almost circular, very slow inward winding

#### 9. Golden Spiral (Special Case)
```
r = exp(theta*log(1.618))  # r = e^(θ·ln(φ)) where φ = golden ratio
r = exp(theta*0.481)       # Approximation: r = e^(0.481θ)
```
**Properties**: Self-similar at all scales, matches Fibonacci growth, found in nature
**Natural Examples**: Nautilus shells, galaxy arms, flower petals, pine cones

#### 10. Custom Growth Rates
```
r = exp(0.2*theta)       # Medium expansion
r = exp(-0.1*theta)      # Gentle contraction  
r = 2*exp(0.25*theta)    # Scaled medium expansion
```

### Mathematical Properties of Logarithmic Spirals

**Key Characteristics**:
- **Self-Similar**: Every zoomed portion looks identical to the whole
- **Constant Pitch Angle**: Angle between radius and tangent is constant
- **Exponential Growth**: Distance between arms increases geometrically
- **Natural Occurrence**: Found throughout nature and art

**Parameters**:
- **a** (scaling constant): Controls overall size
- **b** (growth rate): Controls spiral tightness
  - **b > 0**: Outward expansion (counter-clockwise)
  - **b < 0**: Inward contraction (spiral toward center)
  - **|b| larger**: Faster growth/contraction

**Real-World Examples**:
- 🐚 Nautilus shells (chambered growth)
- 🌪️ Hurricane and cyclone patterns  
- 🌌 Galaxy spiral arms
- 🌻 Sunflower seed arrangements
- 🏛️ Baroque architecture and art
- 📈 Financial compound growth curves

---

## 🦋 **Butterfly Curves (Exponential + Trigonometric)**

### Temple Fay Classic (1989)
```
r = exp(sin(theta)) - 2*cos(4*theta)
```
**Original complete formula**: `r = exp(sin(theta)) - 2*cos(4*theta) + sin(2*theta-pi/24)**5`

### Butterfly Variations

#### Wider Wings
```
r = exp(sin(2*theta)) - 2*cos(3*theta) + sin(2*theta/12)**4
```

#### Compact Butterfly
```
r = exp(sin(theta)) - cos(6*theta) + sin(theta/8)**5
```

#### Double-wing Spread
```
r = exp(sin(3*theta)) - 2*cos(5*theta) + sin(2*theta/16)**3
```

#### Rippled Butterfly
```
r = exp(sin(theta)) - 2*cos(8*theta) + sin(3*theta/20)**6
```

#### Asymmetric Wings
```
r = exp(cos(theta)) - 1.5*cos(4*theta) + sin(2*theta/10)**5
```

#### Stretched Version
```
r = exp(sin(theta)) - 2.5*cos(2*theta) + sin(4*theta/18)**5
```

#### Swallowtail-like
```
r = exp(sin(2*theta)) - 3*cos(5*theta) + sin(2*theta/24)**4
```

#### Mini-butterfly
```
r = exp(sin(theta/2)) - cos(4*theta) + sin(theta/30)**5
```

#### Dragonfly-inspired
```
r = exp(cos(2*theta)) - 2*cos(6*theta) + sin(3*theta/15)**5
```

---

## 🔄 **Limaçons (r = a + b·cos(θ))**

### Inner Loop Limaçons (a < b)
```
r = 1 + 2*cos(theta)     # Inner loop limaçon
r = 2 + 3*sin(theta)     # Large inner loop
```

### Cardioid-like (a = b)
```
r = 2 + 2*cos(theta)     # Cardioid (special case)
```

### Dimpled Limaçons (a > b)
```
r = 3 + 2*cos(theta)     # Dimpled limaçon
r = 4 + 3*sin(theta)     # Large dimpled limaçon
```

---

## 🎯 **Quick Test Examples**

### For Rose Curves
```
r = cos(3*theta)         # Beautiful 3-petal rose
r = 2*sin(4*theta)       # Large 8-petal rose
```

### For Spirals
```
r = theta                # Classic spiral
r = 2 + theta            # Offset spiral
```

### For Butterfly Curves
```
r = exp(sin(theta)) - 2*cos(4*theta)  # Classic butterfly
```

### For Cardioids
```
r = 1 + cos(theta)       # Perfect heart shape
```

---

## 🎨 **Creative Combinations**

### Mathematical Art
```
r = 2*cos(5*theta)       # 5-petal artistic rose
r = 3 + 2*cos(2*theta)   # Figure-8 with offset
r = exp(sin(3*theta)) - cos(6*theta)  # Complex butterfly
```

### Educational Examples
```
r = cos(theta)           # Start with simple 2-petal
r = cos(2*theta)         # Progress to 4-petal
r = cos(3*theta)         # Then 3-petal
r = 1 + cos(theta)       # Finally cardioid
```

---

## 🔬 **System Features**

Each curve provides:
- **Automatic Analysis**: Mathematical properties and characteristics
- **Pattern Recognition**: Curve type identification
- **Visual Rendering**: High-quality polar plots
- **Parameter Extraction**: Automatic coefficient detection
- **Educational Insights**: Mathematical explanations

---

## 🚀 **Getting Started**

1. **Choose a curve type** from above
2. **Copy the equation** into the input field
3. **Click "Generate 2D Graph"**
4. **Explore the analysis** provided
5. **Try variations** by changing coefficients

---

## 💡 **Pro Tips**

- **Rose Curves**: Try different values of n for various petal counts
- **Spirals**: Adjust coefficients for tighter/looser spirals
- **Butterfly Curves**: Experiment with exponential terms for unique wing patterns
- **Cardioids**: Scale parameters for different heart sizes

Start with simple examples and gradually explore more complex patterns!
