import React, { useRef, useMemo, Suspense } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { PerspectiveCamera, Environment, Stars } from '@react-three/drei'
import * as THREE from 'three'

// Premium Cinematic Particle Vortex
function ParticleVortex({ count = 1500 }) {
  const mesh = useRef()
  const light = useRef()

  // Generate random positions and colors for particles
  const particles = useMemo(() => {
    const temp = []
    for (let i = 0; i < count; i++) {
        const time = Math.random() * 100
        const factor = Math.random() * 100 + 20
        const speed = Math.random() * 0.015 + 0.005
        const x = Math.random() * 2 - 1
        const y = Math.random() * 2 - 1
        const z = Math.random() * 2 - 1
        
        // Normalize vector to create a sphere, then perturb
        const length = Math.sqrt(x*x + y*y + z*z)
        const radius = Math.random() * 3 + 1
        
        temp.push({ 
            t: time, 
            factor, 
            speed, 
            initialX: (x/length) * radius, 
            initialY: (y/length) * radius, 
            initialZ: (z/length) * radius,
            color: new THREE.Color().setHSL(Math.random() * 0.1 + 0.65, 0.9, Math.random() * 0.5 + 0.5) // Indigo/Purple hues
        })
    }
    return temp
  }, [count])

  const dummy = useMemo(() => new THREE.Object3D(), [])
  const colorArray = useMemo(() => Float32Array.from(new Array(count).fill().flatMap((_, i) => particles[i].color.toArray())), [count, particles])

  useFrame((state) => {
    particles.forEach((particle, i) => {
      let { t, factor, speed, initialX, initialY, initialZ } = particle
      t = particle.t += speed / 2
      const a = Math.cos(t) + Math.sin(t * 1) / 10
      const b = Math.sin(t) + Math.cos(t * 2) / 10
      const s = Math.cos(t)
      
      dummy.position.set(
        initialX + (Math.cos((t / 10) * factor) + (Math.sin(t * 1) * factor) / 10) / 10,
        initialY + (Math.sin((t / 10) * factor) + (Math.cos(t * 2) * factor) / 10) / 10,
        initialZ + (Math.cos((t / 10) * factor) + (Math.sin(t * 3) * factor) / 10) / 10
      )
      
      dummy.scale.setScalar(s * 0.05 + 0.02)
      dummy.rotation.set(s * 5, s * 5, s * 5)
      dummy.updateMatrix()
      
      mesh.current.setMatrixAt(i, dummy.matrix)
    })
    mesh.current.instanceMatrix.needsUpdate = true
    
    // Rotate the whole vortex slowly
    mesh.current.rotation.y += 0.001
    mesh.current.rotation.x += 0.0005
    
    // Make the central point light pulse
    if (light.current) {
        light.current.intensity = 2 + Math.sin(state.clock.elapsedTime * 2) * 1
    }
  })

  return (
    <group>
        <pointLight ref={light} color="#818CF8" distance={10} intensity={2} decay={2} />
        <instancedMesh ref={mesh} args={[null, null, count]}>
            <icosahedronGeometry args={[0.1, 1]}>
                <instancedBufferAttribute attach="attributes-color" args={[colorArray, 3]} />
            </icosahedronGeometry>
            <meshStandardMaterial vertexColors attach="material" roughness={0.2} metalness={0.8} />
        </instancedMesh>
    </group>
  )
}

function CinematicRig() {
  return useFrame((state) => {
    // Cinematic slow camera drift based on mouse
    const t = state.clock.getElapsedTime()
    state.camera.position.x = THREE.MathUtils.lerp(state.camera.position.x, Math.sin(t/5) * 2 + state.mouse.x * 2, 0.02)
    state.camera.position.y = THREE.MathUtils.lerp(state.camera.position.y, Math.cos(t/5) * 2 + state.mouse.y * 2, 0.02)
    state.camera.lookAt(0, 0, 0)
  })
}

export default function HeroScene() {
  return (
    <div className="w-full h-full absolute inset-0 mix-blend-screen" aria-hidden="true" style={{ pointerEvents: 'none' }}>
      <Canvas shadows dpr={[1, 2]} gl={{ antialias: true, alpha: true }}>
        <PerspectiveCamera makeDefault position={[0, 0, 12]} fov={45} />
        
        <ambientLight intensity={0.1} />
        <spotLight position={[10, 20, 10]} penumbra={1} angle={0.3} intensity={2} color="#4F46E5" />
        <pointLight position={[-10, -10, -10]} intensity={1} color="#c7d2fe" />
        
        <Suspense fallback={null}>
          <ParticleVortex count={800} />
          <Stars radius={50} depth={50} count={3000} factor={4} saturation={0} fade speed={1} />
        </Suspense>

        <CinematicRig />
      </Canvas>
    </div>
  )
}
