import { useEffect, useRef } from 'react'

export default function MouseBackground() {
  const background = useRef(null)
  useEffect(() => {
    const move = ({ clientX, clientY }) => {
      background.current?.style.setProperty('--mouse-x', `${clientX}px`)
      background.current?.style.setProperty('--mouse-y', `${clientY}px`)
    }
    window.addEventListener('pointermove', move, { passive: true })
    return () => window.removeEventListener('pointermove', move)
  }, [])
  return <div className="mouse-background" ref={background} aria-hidden="true" />
}
