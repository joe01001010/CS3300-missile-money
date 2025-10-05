// Missile Money JavaScript
// Added because I wanted to have a placeholder. Feel free to modify
console.log('Missile Money loaded successfully!');

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('click', function() {
            this.classList.add('loading');
            setTimeout(() => {
                this.classList.remove('loading');
            }, 1000);
        });
    });
});

function toggleTheme() {
    const html = document.documentElement;
    const currentTheme = html.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    html.classList.add('theme-transition');
    
    setTimeout(() => {
        html.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        
        setTimeout(() => {
            html.classList.remove('theme-transition');
        }, 300);
    }, 50);
}