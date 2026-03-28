import React, { useRef, useMemo } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import * as THREE from 'three'

const COUNT = 50

function DataNodes() {
  const mesh = useRef()
  const dummy = useMemo(() => new THREE.Object3D(), [])

  // Pre-compute random positions
  const positions = useMemo(() =>
    Array.from({ length: COUNT }, () => [
      THREE.MathUtils.randFloatSpread(10),
      THREE.MathUtils.randFloatSpread(10),
      THREE.MathUtils.randFloatSpread(10),
    ])
  , [])

  useFrame((state) => {
    const t = state.clock.getElapsedTime()
    positions.forEach(([x, y, z], i) => {
      dummy.position.set(x, y + Math.sin(t + x) * 0.1, z)
      dummy.rotation.set(t * 0.2, t * 0.3, t * 0.1)
      dummy.scale.setScalar(0.8 + Math.sin(t + i) * 0.2)
      dummy.updateMatrix()
      mesh.current.setMatrixAt(i, dummy.matrix)
    })
    mesh.current.instanceMatrix.needsUpdate = true
    mesh.current.rotation.z = t * 0.05
    mesh.current.rotation.x = t * 0.03
  })

  return (
    <instancedMesh ref={mesh} args={[null, null, COUNT]}>
      <boxGeometry args={[0.2, 0.2, 0.2]} />
      <meshStandardMaterial color="#6366F1" roughness={0.3} metalness={0.5} />
    </instancedMesh>
  )
}

export default function DashboardScene() {
  return (
    <div className="w-full h-full min-h-[300px] absolute inset-0 -z-10 opacity-30 pointer-events-none" aria-hidden="true">
      <Canvas camera={{ position: [0, 0, 15], fov: 35 }} gl={{ antialias: false }}>
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} intensity={1} color="#6366F1" />
        <DataNodes />
      </Canvas>
    </div>
  )
}
