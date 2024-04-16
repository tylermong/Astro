/*
* Simple Javascript particle system used to create stars
* based on various simple particle systems
*/

class Star {
    constructor(canvasWidth, canvasHeight) {
        this.x = Math.random() * canvasWidth;
        this.y = Math.random() * canvasHeight;
        this.velocity = 0.1 + Math.random() * 0.1;
        this.radius = 0.5 + Math.random() * 1.5;
    }

    update() {
        this.y += this.velocity;
        if (this.y > canvas.height) {
            this.y = 0;
            this.x = Math.random() * canvas.width;
        }
    }

    draw(ctx) {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.radius, 0, 2 * Math.PI);
        ctx.fillStyle = "white";
        ctx.fill();
    }
}

const canvas = document.getElementById('stars-background');
const ctx = canvas.getContext('2d');

let stars = [];

function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    stars = [];
    for (let i = 0; i < 100; i++) { // Number of stars
        stars.push(new Star(canvas.width, canvas.height));
    }
}

function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (let star of stars) {
        star.update();
        star.draw(ctx);
    }
    requestAnimationFrame(animate);
}

window.addEventListener('resize', resizeCanvas);
resizeCanvas();
animate();