/**
 * Blue Business Theme — Interaction System
 * 企业蓝色商务风格 H5 交互逻辑
 *
 * 依赖 CDN 全局变量（由 skeleton.html 引入）：
 * - echarts: ECharts 图表库
 * - mermaid: Mermaid 流程图渲染
 */

/* global echarts, mermaid */

// === 幻灯片引擎 ===
class SlideEngine {
    constructor() {
        this.slides = document.querySelectorAll('.slide');
        this.currentIndex = 0;
        this.totalSlides = this.slides.length;
        this.touchStartX = 0;
        this.touchEndX = 0;
        this.init();
    }

    init() {
        this.slides.forEach((slide, index) => {
            slide.classList.remove('active', 'prev', 'next');
            if (index === 0) slide.classList.add('active');
            else if (index === 1) slide.classList.add('next');
        });
        this.updateProgress();
        this.bindEvents();
    }

    bindEvents() {
        document.addEventListener('keydown', (e) => this.handleKeydown(e));
        document.addEventListener('touchstart', (e) => this.handleTouchStart(e));
        document.addEventListener('touchend', (e) => this.handleTouchEnd(e));

        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = e.currentTarget.dataset.action;
                if (action === 'prev') this.prev();
                else if (action === 'next') this.next();
            });
        });
    }

    handleKeydown(e) {
        if (e.key === 'ArrowRight' || e.key === 'ArrowDown' || e.key === ' ') {
            e.preventDefault(); this.next();
        } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
            e.preventDefault(); this.prev();
        } else if (e.key === 'Home') {
            e.preventDefault(); this.goTo(0);
        } else if (e.key === 'End') {
            e.preventDefault(); this.goTo(this.totalSlides - 1);
        }
    }

    handleTouchStart(e) { this.touchStartX = e.changedTouches[0].screenX; }

    handleTouchEnd(e) {
        this.touchEndX = e.changedTouches[0].screenX;
        this.handleSwipe();
    }

    handleSwipe() {
        const diff = this.touchStartX - this.touchEndX;
        if (Math.abs(diff) > 50) {
            if (diff > 0) this.next(); else this.prev();
        }
    }

    next() { if (this.currentIndex < this.totalSlides - 1) this.goTo(this.currentIndex + 1); }
    prev() { if (this.currentIndex > 0) this.goTo(this.currentIndex - 1); }

    goTo(index) {
        if (index < 0 || index >= this.totalSlides) return;
        this.slides[this.currentIndex].classList.remove('active');
        this.slides[this.currentIndex].classList.add(index > this.currentIndex ? 'prev' : 'next');
        this.slides.forEach((slide, i) => {
            if (i !== this.currentIndex) slide.classList.remove('prev', 'next', 'active');
        });
        this.currentIndex = index;
        this.slides[this.currentIndex].classList.remove('prev', 'next');
        this.slides[this.currentIndex].classList.add('active');
        if (this.currentIndex > 0) {
            this.slides[this.currentIndex - 1].classList.add('prev');
        }
        if (this.currentIndex < this.totalSlides - 1) {
            this.slides[this.currentIndex + 1].classList.add('next');
        }
        this.updateProgress();
        this.initCharts(this.slides[this.currentIndex]);
    }

    updateProgress() {
        const progress = ((this.currentIndex + 1) / this.totalSlides) * 100;
        const bar = document.querySelector('.progress-bar');
        if (bar) bar.style.width = progress + '%';
        const indicator = document.querySelector('.page-indicator');
        if (indicator) indicator.textContent = `${this.currentIndex + 1} / ${this.totalSlides}`;
    }

    // === ECharts 初始化 ===
    initCharts(scope) {
        if (typeof echarts === 'undefined') return;
        const containers = (scope || document).querySelectorAll('.echart[data-option]');
        containers.forEach(container => {
            if (container.dataset.initialized === 'true') return;
            try {
                const chart = echarts.init(container);
                const option = JSON.parse(container.dataset.option);
                chart.setOption(option);
                container.dataset.initialized = 'true';
                window.addEventListener('resize', () => chart.resize());
            } catch (e) { console.error('ECharts error:', e); }
        });
    }

    // === Mermaid 初始化 ===
    initMermaid(scope) {
        if (typeof mermaid === 'undefined') return;
        mermaid.initialize({ startOnLoad: false, theme: 'base' });
        const diagrams = (scope || document).querySelectorAll('.mermaid-diagram[data-code]');
        diagrams.forEach(async (container) => {
            if (container.dataset.rendered === 'true') return;
            try {
                const code = container.dataset.code;
                const id = 'mermaid-' + Math.random().toString(36).substring(2, 11);
                const { svg } = await mermaid.render(id, code);
                container.innerHTML = svg;
                container.dataset.rendered = 'true';
            } catch (e) {
                container.innerHTML = '<p style="color:red;">Mermaid 渲染失败: ' + e.message + '</p>';
            }
        });
    }
}

// === 图片预览 ===
class ImagePreview {
    constructor() {
        this.overlay = null;
        this.init();
    }

    init() {
        this.createOverlay();
        document.querySelectorAll('.image-item img').forEach(img => {
            img.addEventListener('click', () => this.show(img.src));
        });
    }

    createOverlay() {
        this.overlay = document.createElement('div');
        this.overlay.className = 'lightbox-overlay';
        this.overlay.innerHTML = `
            <div class="lightbox-content">
                <div class="lightbox-close">&times;</div>
                <img src="" alt="预览">
            </div>`;
        document.body.appendChild(this.overlay);
        this.overlay.querySelector('.lightbox-close').addEventListener('click', () => this.hide());
        this.overlay.addEventListener('click', (e) => {
            if (e.target === this.overlay) this.hide();
        });
    }

    show(src) {
        this.overlay.querySelector('img').src = src;
        this.overlay.classList.add('active');
    }

    hide() { this.overlay.classList.remove('active'); }
}

// === 启动 ===
document.addEventListener('DOMContentLoaded', () => {
    const engine = new SlideEngine();
    window.slideEngine = engine;
    new ImagePreview();
    setTimeout(() => {
        engine.initCharts();
        engine.initMermaid();
    }, 500);
});
