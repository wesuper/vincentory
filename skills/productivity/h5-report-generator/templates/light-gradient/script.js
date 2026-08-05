// Light Gradient Theme — Interaction System
// 幻灯片切换、Mermaid/ECharts 渲染、图片 Lightbox

/* global echarts, mermaid */

const slideOrder = [];
let currentSlide = 1;
let totalSlides = 1;

function initSlideOrder() {
    const slides = document.querySelectorAll('.slide');
    slides.forEach(slide => {
        if (slide.id) slideOrder.push(slide.id);
    });
    totalSlides = slideOrder.length;

    const totalEl = document.getElementById('totalPages');
    if (totalEl) totalEl.textContent = totalSlides;
}

function showSlide(n) {
    if (n > totalSlides) currentSlide = 1;
    if (n < 1) currentSlide = totalSlides;

    document.querySelectorAll('.slide').forEach(slide => slide.classList.remove('active'));

    const slideId = slideOrder[currentSlide - 1];
    const target = document.getElementById(slideId);
    if (target) target.classList.add('active');

    const currentEl = document.getElementById('currentPage');
    if (currentEl) currentEl.textContent = currentSlide;

    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    if (prevBtn) prevBtn.disabled = currentSlide === 1;
    if (nextBtn) nextBtn.disabled = currentSlide === totalSlides;

    window.scrollTo(0, 0);
}

function changeSlide(direction) {
    currentSlide += direction;
    showSlide(currentSlide);
}

// Keyboard navigation
document.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowLeft') {
        changeSlide(-1);
    } else if (e.key === 'ArrowRight' || e.key === ' ') {
        e.preventDefault();
        changeSlide(1);
    }
});

// === ECharts 初始化 ===
function initECharts() {
    if (typeof echarts === 'undefined') return;
    document.querySelectorAll('.echart[data-option]').forEach(container => {
        if (container.dataset.initialized === 'true') return;
        try {
            const chart = echarts.init(container);
            const option = JSON.parse(container.dataset.option);
            chart.setOption(option);
            container.dataset.initialized = 'true';
            window.addEventListener('resize', () => chart.resize());
        } catch (e) {
            console.error('ECharts error:', e);
        }
    });
}

// === 图片 Lightbox ===
function initLightbox() {
    const overlay = document.createElement('div');
    overlay.className = 'lightbox-overlay';
    overlay.innerHTML = `
        <div class="lightbox-content">
            <div class="lightbox-close">&times;</div>
            <img src="" alt="预览">
        </div>`;
    document.body.appendChild(overlay);

    overlay.querySelector('.lightbox-close').addEventListener('click', () => {
        overlay.classList.remove('active');
    });
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) overlay.classList.remove('active');
    });

    document.querySelectorAll('.image-item img').forEach(img => {
        img.style.cursor = 'pointer';
        img.addEventListener('click', () => {
            overlay.querySelector('img').src = img.src;
            overlay.classList.add('active');
        });
    });
}

// Initialize
document.addEventListener('DOMContentLoaded', async function () {
    initSlideOrder();

    if (typeof mermaid !== 'undefined') {
        mermaid.initialize({
            startOnLoad: false,
            theme: 'default',
            flowchart: {
                useMaxWidth: true,
                htmlLabels: true,
                curve: 'basis'
            }
        });

        const allSlides = document.querySelectorAll('.slide');
        allSlides.forEach(slide => slide.classList.add('active'));

        await mermaid.run();

        allSlides.forEach(slide => slide.classList.remove('active'));
    }

    showSlide(currentSlide);
    initECharts();
    initLightbox();
});
