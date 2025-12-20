/**
 * MATRIX CODE RAIN EFFECT
 * Cyberpunk Terminal Visual Enhancement
 */

(function() {
    'use strict';

    // Configuration
    const config = {
        enabled: true,
        fontSize: 14,
        columns: null,
        drops: [],
        chars: 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@#$%^&*()_+-=[]{}|;:,.<>?/~`ﾊﾐﾋｰｳｼﾅﾓﾆｻﾜﾂｵﾘｱﾎﾃﾏｹﾒｴｶｷﾑﾕﾗｾﾈｽﾀﾇﾍ',
        opacity: 0.05, // Very subtle, won't interfere with content
        speed: 33, // ms per frame
        density: 0.015, // Lower = fewer characters
        color: '#00ff41'
    };

    let canvas, ctx, animationId;

    function init() {
        // Create canvas element
        canvas = document.createElement('canvas');
        canvas.id = 'matrix-canvas';
        canvas.style.position = 'fixed';
        canvas.style.top = '0';
        canvas.style.left = '0';
        canvas.style.width = '100%';
        canvas.style.height = '100%';
        canvas.style.pointerEvents = 'none';
        canvas.style.zIndex = '1';
        canvas.style.opacity = config.opacity;

        document.body.insertBefore(canvas, document.body.firstChild);

        ctx = canvas.getContext('2d');

        // Set canvas size
        resizeCanvas();

        // Start animation
        if (config.enabled) {
            animate();
        }

        // Handle resize
        window.addEventListener('resize', debounce(resizeCanvas, 250));

        // Pause animation when tab is not visible (performance optimization)
        document.addEventListener('visibilitychange', handleVisibilityChange);
    }

    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        config.columns = Math.floor(canvas.width / config.fontSize);

        // Initialize drops array
        config.drops = [];
        for (let i = 0; i < config.columns; i++) {
            // Random starting position
            config.drops[i] = Math.random() < config.density ? Math.floor(Math.random() * -100) : -100;
        }
    }

    function animate() {
        // Semi-transparent black to create fade effect
        ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Set text style
        ctx.fillStyle = config.color;
        ctx.font = config.fontSize + 'px monospace';

        // Loop through drops
        for (let i = 0; i < config.drops.length; i++) {
            // Random character
            const char = config.chars[Math.floor(Math.random() * config.chars.length)];

            // Draw character
            const x = i * config.fontSize;
            const y = config.drops[i] * config.fontSize;

            // Add glow effect to some characters
            if (Math.random() > 0.98) {
                ctx.shadowBlur = 10;
                ctx.shadowColor = config.color;
            } else {
                ctx.shadowBlur = 0;
            }

            ctx.fillText(char, x, y);

            // Reset drop to top randomly after it has crossed the screen
            if (y > canvas.height && Math.random() > 0.975) {
                config.drops[i] = 0;
            }

            // Increment Y coordinate
            config.drops[i]++;
        }

        animationId = setTimeout(() => {
            requestAnimationFrame(animate);
        }, config.speed);
    }

    function handleVisibilityChange() {
        if (document.hidden) {
            // Pause animation
            if (animationId) {
                clearTimeout(animationId);
            }
        } else {
            // Resume animation
            if (config.enabled) {
                animate();
            }
        }
    }

    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Public API
    window.MatrixEffect = {
        start: function() {
            config.enabled = true;
            animate();
        },
        stop: function() {
            config.enabled = false;
            if (animationId) {
                clearTimeout(animationId);
            }
            // Clear canvas
            if (ctx) {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
            }
        },
        setOpacity: function(opacity) {
            config.opacity = Math.max(0, Math.min(1, opacity));
            if (canvas) {
                canvas.style.opacity = config.opacity;
            }
        },
        setSpeed: function(speed) {
            config.speed = Math.max(10, Math.min(100, speed));
        }
    };

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Add toggle control to settings (optional)
    function addToggleControl() {
        const style = document.createElement('style');
        style.textContent = `
            #matrix-toggle {
                position: fixed;
                bottom: 100px;
                right: 30px;
                background: rgba(0, 0, 0, 0.8);
                border: 2px solid #00ff41;
                color: #00ff41;
                padding: 8px 12px;
                border-radius: 6px;
                cursor: pointer;
                z-index: 999;
                font-family: 'Fira Code', monospace;
                font-size: 0.8rem;
                transition: all 0.3s ease;
                box-shadow: 0 0 15px rgba(0, 255, 65, 0.3);
            }
            #matrix-toggle:hover {
                background: rgba(0, 255, 65, 0.2);
                box-shadow: 0 0 25px rgba(0, 255, 65, 0.6);
                transform: scale(1.05);
            }
        `;
        document.head.appendChild(style);

        const toggle = document.createElement('button');
        toggle.id = 'matrix-toggle';
        toggle.textContent = '⚡ Matrix';
        toggle.title = 'Toggle Matrix Effect';

        let isEnabled = true;
        toggle.addEventListener('click', function() {
            isEnabled = !isEnabled;
            if (isEnabled) {
                window.MatrixEffect.start();
                toggle.textContent = '⚡ Matrix';
                toggle.style.borderColor = '#00ff41';
                toggle.style.color = '#00ff41';
            } else {
                window.MatrixEffect.stop();
                toggle.textContent = '⚡ Off';
                toggle.style.borderColor = '#ff006e';
                toggle.style.color = '#ff006e';
            }
        });

        document.body.appendChild(toggle);
    }

    // Uncomment to add toggle button
    // setTimeout(addToggleControl, 1000);

})();

/**
 * SCANNING LINE EFFECT
 * Adds a subtle scanning line across the screen
 */
(function() {
    'use strict';

    function initScanline() {
        const style = document.createElement('style');
        style.textContent = `
            @keyframes scanline {
                0% {
                    transform: translateY(-100%);
                }
                100% {
                    transform: translateY(100vh);
                }
            }

            #cyber-scanline {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 3px;
                background: linear-gradient(to bottom,
                    transparent,
                    rgba(0, 255, 65, 0.3),
                    transparent
                );
                pointer-events: none;
                z-index: 9999;
                animation: scanline 8s linear infinite;
                box-shadow: 0 0 10px rgba(0, 255, 65, 0.5);
            }
        `;
        document.head.appendChild(style);

        const scanline = document.createElement('div');
        scanline.id = 'cyber-scanline';
        document.body.appendChild(scanline);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initScanline);
    } else {
        initScanline();
    }
})();

/**
 * GLITCH TEXT EFFECT
 * Randomly glitches certain elements for cyberpunk aesthetic
 */
(function() {
    'use strict';

    function addGlitchToHeaders() {
        const style = document.createElement('style');
        style.textContent = `
            @keyframes text-glitch {
                0% {
                    transform: translate(0);
                    opacity: 1;
                }
                20% {
                    transform: translate(-2px, 1px);
                    opacity: 0.8;
                }
                40% {
                    transform: translate(-1px, -1px);
                    opacity: 0.9;
                }
                60% {
                    transform: translate(1px, 1px);
                    opacity: 0.8;
                }
                80% {
                    transform: translate(1px, -1px);
                    opacity: 0.9;
                }
                100% {
                    transform: translate(0);
                    opacity: 1;
                }
            }

            .cyber-glitch {
                animation: text-glitch 0.3s ease-in-out;
            }
        `;
        document.head.appendChild(style);

        // Randomly glitch h1 elements
        function triggerGlitch() {
            const headers = document.querySelectorAll('h1');
            if (headers.length > 0) {
                const randomHeader = headers[Math.floor(Math.random() * headers.length)];
                randomHeader.classList.add('cyber-glitch');
                setTimeout(() => {
                    randomHeader.classList.remove('cyber-glitch');
                }, 300);
            }

            // Schedule next glitch (between 10-30 seconds)
            const nextGlitch = Math.random() * 20000 + 10000;
            setTimeout(triggerGlitch, nextGlitch);
        }

        // Start glitch effect after page load
        setTimeout(triggerGlitch, 5000);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', addGlitchToHeaders);
    } else {
        addGlitchToHeaders();
    }
})();

/**
 * PARTICLE GLOW EFFECT
 * Adds floating particles around cursor (optional, subtle)
 */
(function() {
    'use strict';

    let particles = [];
    const maxParticles = 30;
    let mouseX = 0;
    let mouseY = 0;
    let canvas, ctx;

    function initParticles() {
        canvas = document.createElement('canvas');
        canvas.id = 'particle-canvas';
        canvas.style.position = 'fixed';
        canvas.style.top = '0';
        canvas.style.left = '0';
        canvas.style.width = '100%';
        canvas.style.height = '100%';
        canvas.style.pointerEvents = 'none';
        canvas.style.zIndex = '2';

        document.body.appendChild(canvas);

        ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        window.addEventListener('resize', () => {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        });

        document.addEventListener('mousemove', (e) => {
            mouseX = e.clientX;
            mouseY = e.clientY;

            // Create particle occasionally
            if (Math.random() > 0.9 && particles.length < maxParticles) {
                particles.push({
                    x: mouseX,
                    y: mouseY,
                    vx: (Math.random() - 0.5) * 2,
                    vy: (Math.random() - 0.5) * 2,
                    life: 1,
                    decay: 0.01
                });
            }
        });

        animateParticles();
    }

    function animateParticles() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        particles = particles.filter(p => p.life > 0);

        particles.forEach(p => {
            p.x += p.vx;
            p.y += p.vy;
            p.life -= p.decay;

            ctx.beginPath();
            ctx.arc(p.x, p.y, 2, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(0, 255, 65, ${p.life * 0.3})`;
            ctx.shadowBlur = 10;
            ctx.shadowColor = '#00ff41';
            ctx.fill();
        });

        requestAnimationFrame(animateParticles);
    }

    // Uncomment to enable particle effect
    // if (document.readyState === 'loading') {
    //     document.addEventListener('DOMContentLoaded', initParticles);
    // } else {
    //     initParticles();
    // }
})();
