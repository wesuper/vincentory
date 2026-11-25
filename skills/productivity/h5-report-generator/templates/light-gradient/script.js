/**
 * Light Gradient Theme — Interaction System (v5)
 * 幻灯片切换、顶部进度条、页码、ECharts/Mermaid 渲染、图片 Lightbox、折叠分组
 *
 * 无第三方依赖也能运行：echarts/mermaid 未加载时自动跳过（内网环境安全）。
 */

/* global echarts, mermaid */

(function () {
    'use strict';

    function $(sel, root) {
        return (root || document).querySelector(sel);
    }

    function $all(sel, root) {
        return Array.prototype.slice.call((root || document).querySelectorAll(sel));
    }

    // ============================================================
    // 幻灯片引擎：页面顺序 = DOM 顺序，无需维护 slideOrder 数组
    // ============================================================
    var SlideEngine = {
        slides: [],
        index: 0,
        touchX: 0,

        init: function () {
            this.slides = $all('.slide');
            if (!this.slides.length) return;

            this.slides.forEach(function (slide, i) {
                slide.classList.toggle('active', i === 0);
            });

            this.bindEvents();
            this.update();
            this.initCharts(this.slides[0]);
            this.initMermaid(this.slides[0]);
        },

        bindEvents: function () {
            var self = this;

            document.addEventListener('keydown', function (e) {
                // 只在没有输入焦点时接管方向键
                var tag = (e.target && e.target.tagName) || '';
                if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return;

                if (e.key === 'ArrowRight' || e.key === 'PageDown') {
                    e.preventDefault();
                    self.next();
                } else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
                    e.preventDefault();
                    self.prev();
                } else if (e.key === 'Home') {
                    e.preventDefault();
                    self.goTo(0);
                } else if (e.key === 'End') {
                    e.preventDefault();
                    self.goTo(self.slides.length - 1);
                }
            });

            document.addEventListener('touchstart', function (e) {
                self.touchX = e.changedTouches[0].screenX;
            }, { passive: true });

            document.addEventListener('touchend', function (e) {
                var diff = self.touchX - e.changedTouches[0].screenX;
                if (Math.abs(diff) > 50) {
                    if (diff > 0) self.next();
                    else self.prev();
                }
            }, { passive: true });

            $all('.nav-btn').forEach(function (btn) {
                btn.addEventListener('click', function (e) {
                    var action = e.currentTarget.dataset.action;
                    if (action === 'prev') self.prev();
                    else if (action === 'next') self.next();
                });
            });
        },

        next: function () {
            if (this.index < this.slides.length - 1) this.goTo(this.index + 1);
        },

        prev: function () {
            if (this.index > 0) this.goTo(this.index - 1);
        },

        goTo: function (target) {
            if (target < 0 || target >= this.slides.length || target === this.index) return;

            this.slides[this.index].classList.remove('active');
            this.index = target;
            var slide = this.slides[this.index];
            slide.classList.add('active');

            this.update();
            this.initCharts(slide);
            this.initMermaid(slide);

            // 切页后回到页首，避免长页残留滚动位置
            window.scrollTo(0, 0);
        },

        update: function () {
            var total = this.slides.length;
            var current = this.index + 1;

            var bar = $('.progress-bar');
            if (bar) bar.style.width = (current / total * 100) + '%';

            var indicator = $('.page-indicator');
            if (indicator) {
                var cur = $('#currentPage');
                var tot = $('#totalPages');
                if (cur && tot) {
                    cur.textContent = current;
                    tot.textContent = total;
                } else {
                    indicator.textContent = current + ' / ' + total;
                }
            }

            var prevBtn = $('#prevBtn');
            var nextBtn = $('#nextBtn');
            if (prevBtn) prevBtn.disabled = current === 1;
            if (nextBtn) nextBtn.disabled = current === total;
        },

        // === ECharts：只初始化可见页，避免 display:none 下尺寸为 0 ===
        initCharts: function (scope) {
            var ec = window.echarts;
            if (!ec) return;
            $all('.echart[data-option]', scope).forEach(function (container) {
                if (container.dataset.initialized === 'true') return;
                if (!container.clientWidth || !container.clientHeight) return;
                try {
                    var chart = ec.init(container);
                    chart.setOption(JSON.parse(container.dataset.option));
                    if (ec.resize) {
                        window.addEventListener('resize', function () { ec.resize(chart); });
                    }
                } catch (err) {
                    console.error('ECharts error:', err);
                }
            });
        },

        // === Mermaid：data-code 属性或裸 <pre class="mermaid"> 均可 ===
        initMermaid: function (scope) {
            var mm = window.mermaid;
            if (!mm) return;
            if (!this.mermaidReady) {
                mm.initialize({ startOnLoad: false, theme: 'base', flowchart: { useMaxWidth: true, htmlLabels: true } });
                this.mermaidReady = true;
            }
            $all('.mermaid-diagram[data-code]', scope).forEach(function (container) {
                if (container.dataset.rendered === 'true') return;
                var id = 'mermaid-' + Math.random().toString(36).slice(2, 11);
                Promise.resolve(mm.render(id, container.dataset.code))
                    .then(function (result) {
                        container.innerHTML = result.svg;
                        container.dataset.rendered = 'true';
                    })
                    .catch(function (err) {
                        container.innerHTML = '<p style="color:#c62828;">Mermaid 渲染失败：' +
                            String(err && err.message ? err.message : err) + '</p>';
                    });
            });
        }
    };

    // ============================================================
    // 图片 Lightbox
    // ============================================================
    var ImagePreview = {
        overlay: null,

        init: function () {
            if (!$all('.image-item img').length) return;
            this.createOverlay();
            var self = this;
            $all('.image-item img').forEach(function (img) {
                img.style.cursor = 'pointer';
                img.addEventListener('click', function () { self.show(img.src); });
            });
        },

        createOverlay: function () {
            var overlay = document.createElement('div');
            overlay.className = 'lightbox-overlay';
            overlay.innerHTML = '<div class="lightbox-content">' +
                '<div class="lightbox-close">&times;</div>' +
                '<img src="" alt="预览"></div>';
            document.body.appendChild(overlay);
            this.overlay = overlay;

            overlay.querySelector('.lightbox-close').addEventListener('click', this.hide.bind(this));
            overlay.addEventListener('click', function (e) {
                if (e.target === overlay) this.hide();
            }.bind(this));
        },

        show: function (src) {
            if (!this.overlay) return;
            this.overlay.querySelector('img').src = src;
            this.overlay.classList.add('active');
        },

        hide: function () {
            if (this.overlay) this.overlay.classList.remove('active');
        }
    };

    // ============================================================
    // 折叠分组（点击标题折叠，默认展开）
    // ============================================================
    function initFoldSections() {
        $all('.fold-title').forEach(function (title) {
            function toggle() {
                var section = title.closest('.fold-section');
                if (section) section.classList.toggle('collapsed');
            }
            title.addEventListener('click', toggle);
            title.addEventListener('keydown', function (e) {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    toggle();
                }
            });
        });
    }

    // ============================================================
    // 启动
    // ============================================================
    function boot() {
        SlideEngine.init();
        ImagePreview.init();
        initFoldSections();
        window.slideEngine = SlideEngine;
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', boot);
    } else {
        boot();
    }
})();
