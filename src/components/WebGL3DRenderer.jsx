import React, { useMemo, useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Grid, Text, Line } from '@react-three/drei';
import * as THREE from 'three';

// Component to render 3D polar surface
function PolarSurface({ expression, animate = false }) {
  const meshRef = useRef();
  
  // Animation rotation
  useFrame((state) => {
    if (animate && meshRef.current) {
      meshRef.current.rotation.z += 0.01;
    }
  });

  const geometry = useMemo(() => {
    try {
      // Create geometry for polar surface
      const thetaSegments = 64;
      const rSegments = 32;
      const maxR = 5;
      
      const geometry = new THREE.BufferGeometry();
      const vertices = [];
      const indices = [];
      const colors = [];
      
      // Evaluate polar expression
      const evaluateExpression = (theta, r) => {
        try {
          // Replace mathematical functions and constants
          let expr = expression
            .replace(/sin\(/g, 'Math.sin(')
            .replace(/cos\(/g, 'Math.cos(')
            .replace(/tan\(/g, 'Math.tan(')
            .replace(/sqrt\(/g, 'Math.sqrt(')
            .replace(/abs\(/g, 'Math.abs(')
            .replace(/pi/g, 'Math.PI')
            .replace(/e(?![a-zA-Z])/g, 'Math.E')
            .replace(/theta/g, theta)
            .replace(/r(?![a-zA-Z])/g, r);
          
          // For simple cases like "r = 1", "r = 2", etc.
          if (expr.includes('=')) {
            const parts = expr.split('=').map(part => part.trim());
            if (parts[0] === 'r') {
              expr = parts[1];
            }
          }
          
          return eval(expr);
        } catch (e) {
          return 1; // Default value
        }
      };

      // Generate vertices
      for (let i = 0; i <= thetaSegments; i++) {
        const theta = (i / thetaSegments) * Math.PI * 2;
        
        for (let j = 0; j <= rSegments; j++) {
          const r = (j / rSegments) * maxR;
          
          // Get z value from polar expression
          const z = evaluateExpression(theta, r);
          
          // Convert polar to cartesian
          const x = r * Math.cos(theta);
          const y = r * Math.sin(theta);
          
          vertices.push(x, y, z);
          
          // Add colors based on height
          const normalizedZ = (z + 2) / 4; // Normalize for color
          colors.push(normalizedZ, 0.5, 1 - normalizedZ);
        }
      }

      // Generate indices for triangles
      for (let i = 0; i < thetaSegments; i++) {
        for (let j = 0; j < rSegments; j++) {
          const a = i * (rSegments + 1) + j;
          const b = a + rSegments + 1;
          const c = a + 1;
          const d = b + 1;

          indices.push(a, b, c);
          indices.push(b, d, c);
        }
      }

      geometry.setIndex(indices);
      geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
      geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
      geometry.computeVertexNormals();
      
      return geometry;
    } catch (error) {
      console.error('Error creating geometry:', error);
      // Return a simple plane as fallback
      return new THREE.PlaneGeometry(5, 5, 32, 32);
    }
  }, [expression]);

  return (
    <mesh ref={meshRef} geometry={geometry} rotation={[-Math.PI / 2, 0, 0]}>
      <meshStandardMaterial 
        vertexColors 
        wireframe={false}
        transparent={true}
        opacity={0.8}
        side={THREE.DoubleSide}
      />
    </mesh>
  );
}

// Coordinate axes component
function CoordinateAxes() {
  const axisLength = 6;
  
  return (
    <group>
      {/* X axis - Red */}
      <Line
        points={[[-axisLength, 0, 0], [axisLength, 0, 0]]}
        color="red"
        lineWidth={2}
      />
      <Text
        position={[axisLength + 0.5, 0, 0]}
        fontSize={0.5}
        color="red"
        anchorX="center"
        anchorY="middle"
      >
        X
      </Text>
      
      {/* Y axis - Green */}
      <Line
        points={[[0, -axisLength, 0], [0, axisLength, 0]]}
        color="green"
        lineWidth={2}
      />
      <Text
        position={[0, axisLength + 0.5, 0]}
        fontSize={0.5}
        color="green"
        anchorX="center"
        anchorY="middle"
      >
        Y
      </Text>
      
      {/* Z axis - Blue */}
      <Line
        points={[[0, 0, -axisLength], [0, 0, axisLength]]}
        color="blue"
        lineWidth={2}
      />
      <Text
        position={[0, 0, axisLength + 0.5]}
        fontSize={0.5}
        color="blue"
        anchorX="center"
        anchorY="middle"
      >
        Z
      </Text>
    </group>
  );
}

// Main WebGL 3D Renderer component
function WebGL3DRenderer({ expression = "r = 1", showAxes = true, animate = false }) {
  return (
    <div style={{ width: '100%', height: '500px' }}>
      <Canvas
        camera={{ position: [8, 8, 8], fov: 60 }}
        style={{ background: 'linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)' }}
      >
        {/* Lighting */}
        <ambientLight intensity={0.6} />
        <directionalLight position={[10, 10, 5]} intensity={1} />
        <pointLight position={[-10, -10, -5]} intensity={0.5} />
        
        {/* Controls */}
        <OrbitControls 
          enablePan={true}
          enableZoom={true}
          enableRotate={true}
          dampingFactor={0.05}
        />
        
        {/* Grid */}
        <Grid 
          args={[20, 20]} 
          position={[0, 0, -2]}
          rotation={[Math.PI / 2, 0, 0]}
          infiniteGrid={false}
          fadeDistance={30}
          fadeStrength={1}
        />
        
        {/* Coordinate Axes */}
        {showAxes && <CoordinateAxes />}
        
        {/* 3D Polar Surface */}
        <PolarSurface expression={expression} animate={animate} />
      </Canvas>
    </div>
  );
}

export default WebGL3DRenderer;
