# 🦋 Butterfly Curve Examples

Our system now supports beautiful butterfly curves! Here are the 10 examples you can try:

## 1. Original Temple Fay Butterfly (1989)
```
r = exp(sin(theta)) - 2*cos(4*theta) + sin(2*theta-pi/24)**5
```
**Note**: Use simplified version for testing: `r = exp(sin(theta)) - 2*cos(4*theta)`

## 2. Wider Wings
```
r = exp(sin(2*theta)) - 2*cos(3*theta) + sin(2*theta/12)**4
```

## 3. Compact Butterfly  
```
r = exp(sin(theta)) - cos(6*theta) + sin(theta/8)**5
```

## 4. Double-wing Spread
```
r = exp(sin(3*theta)) - 2*cos(5*theta) + sin(2*theta/16)**3
```

## 5. Rippled Butterfly
```
r = exp(sin(theta)) - 2*cos(8*theta) + sin(3*theta/20)**6
```

## 6. Asymmetric Wings
```
r = exp(cos(theta)) - 1.5*cos(4*theta) + sin(2*theta/10)**5
```

## 7. Stretched Version
```
r = exp(sin(theta)) - 2.5*cos(2*theta) + sin(4*theta/18)**5
```

## 8. Swallowtail-like
```
r = exp(sin(2*theta)) - 3*cos(5*theta) + sin(2*theta/24)**4
```

## 9. Mini-butterfly
```
r = exp(sin(theta/2)) - cos(4*theta) + sin(theta/30)**5
```

## 10. Dragonfly-inspired
```
r = exp(cos(2*theta)) - 2*cos(6*theta) + sin(3*theta/15)**5
```

## ✨ Analysis Features

Each butterfly curve is automatically analyzed with:

- **Mathematical Components**: Detection of exponential, sine, and cosine terms
- **Wing Characteristics**: Symmetry analysis and aesthetic properties  
- **Wing Span Measurements**: Maximum and minimum radius calculations
- **Pattern Recognition**: Identification of oscillation frequencies
- **Complexity Assessment**: Mathematical structure evaluation

## 🎨 Visual Features

- **Extended Theta Range**: 8π range for complete wing pattern capture
- **High Resolution**: 3000 points for smooth butterfly wings
- **Automatic Scaling**: Optimal radius limits for butterfly curves
- **Beautiful Rendering**: Professional matplotlib styling

Try any of these examples in the input field to see the magnificent butterfly patterns come to life!
