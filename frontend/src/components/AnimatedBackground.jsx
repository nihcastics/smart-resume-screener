import React, { useEffect, useRef } from 'react';

const AnimatedBackground = () => {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    let animationFrameId;
    let particles = [];

    // Set canvas size
    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Particle class
    class Particle {
      constructor() {
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height;
        this.size = Math.random() * 3 + 1;
        this.speedX = Math.random() * 0.5 - 0.25;
        this.speedY = Math.random() * 0.5 - 0.25;
        this.hue = Math.random() * 60 + 260; // Purple to pink range
        this.brightness = Math.random() * 30 + 50;
      }

      update() {
        this.x += this.speedX;
        this.y += this.speedY;

        if (this.x > canvas.width) this.x = 0;
        if (this.x < 0) this.x = canvas.width;
        if (this.y > canvas.height) this.y = 0;
        if (this.y < 0) this.y = canvas.height;
      }

      draw() {
        ctx.fillStyle = `hsla(${this.hue}, 80%, ${this.brightness}%, 0.8)`;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();

        // Glow effect
        ctx.shadowBlur = 20;
        ctx.shadowColor = `hsla(${this.hue}, 80%, ${this.brightness}%, 0.5)`;
      }
    }

    // Create particles
    const createParticles = () => {
      const particleCount = Math.min(100, Math.floor((canvas.width * canvas.height) / 10000));
      particles = [];
      for (let i = 0; i < particleCount; i++) {
        particles.push(new Particle());
      }
    };
    createParticles();

    // Animation loop
    let time = 0;
    const animate = () => {
      time += 0.005;

      // Create gradient background
      const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
      gradient.addColorStop(0, '#0f172a');
      gradient.addColorStop(0.5, '#1e1b4b');
      gradient.addColorStop(1, '#0f172a');
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Add moving gradient orbs
      const orb1X = canvas.width * (0.3 + Math.sin(time) * 0.2);
      const orb1Y = canvas.height * (0.3 + Math.cos(time) * 0.2);
      const orb2X = canvas.width * (0.7 + Math.sin(time + Math.PI) * 0.2);
      const orb2Y = canvas.height * (0.7 + Math.cos(time + Math.PI) * 0.2);

      // Purple orb
      const grd1 = ctx.createRadialGradient(orb1X, orb1Y, 0, orb1X, orb1Y, 300);
      grd1.addColorStop(0, 'rgba(139, 92, 246, 0.4)');
      grd1.addColorStop(0.5, 'rgba(139, 92, 246, 0.1)');
      grd1.addColorStop(1, 'rgba(139, 92, 246, 0)');
      ctx.fillStyle = grd1;
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Pink orb
      const grd2 = ctx.createRadialGradient(orb2X, orb2Y, 0, orb2X, orb2Y, 300);
      grd2.addColorStop(0, 'rgba(217, 70, 239, 0.4)');
      grd2.addColorStop(0.5, 'rgba(217, 70, 239, 0.1)');
      grd2.addColorStop(1, 'rgba(217, 70, 239, 0)');
      ctx.fillStyle = grd2;
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Update and draw particles
      particles.forEach((particle) => {
        particle.update();
        particle.draw();
      });

      // Connect nearby particles
      ctx.strokeStyle = 'rgba(139, 92, 246, 0.1)';
      ctx.lineWidth = 1;
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const distance = Math.sqrt(dx * dx + dy * dy);

          if (distance < 150) {
            ctx.beginPath();
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.stroke();
          }
        }
      }

      animationFrameId = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      window.removeEventListener('resize', resizeCanvas);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 -z-10"
      style={{ background: 'linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%)' }}
    />
  );
};

export default AnimatedBackground;
