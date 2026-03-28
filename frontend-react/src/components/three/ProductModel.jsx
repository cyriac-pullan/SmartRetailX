import React, { useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import { RoundedBox, MeshDistortMaterial, Float } from '@react-three/drei'

export default function ProductModel({ color = '#6366F1', hover = false }) {
  const ref = useRef()

  useFrame((state) => {
    if (ref.current) {
        ref.current.rotation.y += 0.01
        ref.current.scale.setScalar(THREE.MathUtils.lerp(ref.current.scale.x, hover ? 1.2 : 1, 0.1))
    }
  })

  return (
    <Float speed={5} rotationIntensity={0.5} floatIntensity={0.5}>
        <RoundedBox ref={ref} args={[1, 1, 1]} radius={0.1} smoothness={4} castShadow>
            <meshStandardMaterial 
                color={color} 
                roughness={0.1} 
                metalness={0.8} 
                emissive={color}
                emissiveIntensity={0.2}
            />
        </RoundedBox>
    </Float>
  )
}

import * as THREE from 'three'
