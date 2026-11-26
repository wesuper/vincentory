/**
 * Deck Interaction System (v6)
 * 翻页、顶部进度条、页码、ECharts/Mermaid、图片 Lightbox、折叠分组
 * 演讲者视图：当前页/下一页 16:9 预览、演讲备注、计时、激光笔、圈选、观众屏同步
 *
 * 无第三方依赖也能运行：echarts/mermaid 未加载时自动跳过（内网环境安全）。
 * 演讲者视图只依赖浏览器本地能力（postMessage / BroadcastChannel / localStorage），
 * 不需要账号或服务器。观众屏打开方式见 SKILL.md。
 */

/* global echarts, mermaid */

(function () {
    'use strict';

    var doc = document;
    var body = doc.body;

    function $(sel, root) {
        return (root || doc).querySelector(sel);
    }

    function $all(sel, root) {
        return Array.prototype.slice.call((root || doc).querySelectorAll(sel));
    }

    function esc(value) {
        return String(value == null ? '' : value).replace(/[&<>"']/g, function (ch) {
            return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch];
        });
    }

    function toLines(value) {
        if (Array.isArray(value)) return value.filter(Boolean);
        return value ? [String(value)] : [];
    }

    var params = new URLSearchParams(location.search);
    var MODE = params.get('mode') || 'deck';           // deck | preview | audience
    var SESSION = params.get('session') || '';
    var IS_EMBED = MODE === 'preview';
    var IS_AUDIENCE = MODE === 'audience';

    var PDF_KEY = 'h5-report-presenter:' + location.pathname.replace(/[?#].*$/, '');
    var SYNC_KEY = PDF_KEY + ':sync';

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

            // 补上稳定的 data-slide-id：演讲者备注按它存档，重排不会串页
            this.slides.forEach(function (slide, i) {
                if (!slide.dataset.slideId) {
                    slide.dataset.slideId = (slide.id || 'slide-' + (i + 1))
                        .replace(/^slide-/, '') || 'slide-' + (i + 1);
                }
                slide.classList.toggle('active', i === 0);
                slide.setAttribute('role', 'group');
                slide.setAttribute('aria-roledescription', '幻灯片');
                slide.setAttribute('aria-label', (i + 1) + ' / ' + SlideEngine.slides.length);
            });

            this.bindEvents();
            this.update();
            this.initCharts(this.slides[0]);
            this.initMermaid(this.slides[0]);

            if (MODE === 'audience') body.classList.add('mode-audience');
            if (MODE === 'preview') body.classList.add('mode-preview');
        },

        bindEvents: function () {
            var self = this;
            if (IS_EMBED) return;               // 嵌入预览由 postMessage 驱动，不自己抢键盘

            doc.addEventListener('keydown', function (e) {
                // 只在没有输入焦点、且演讲者视图未接管时处理
                var tag = (e.target && e.target.tagName) || '';
                if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return;
                if (body.classList.contains('presenter-on')) return;
                if ($('.lightbox-overlay.active')) return;

                if (e.key === 'ArrowRight' || e.key === 'PageDown' || e.key === ' ') {
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
                } else if (e.key === 'f' || e.key === 'F') {
                    self.toggleFullscreen();
                } else if ((e.key === 'p' || e.key === 'P') && !IS_AUDIENCE) {
                    e.preventDefault();
                    // 演讲者视图的 keydown 已绑定：不拦住本次事件会让它立刻又被当成"退出"
                    e.stopImmediatePropagation();
                    if (window.Presenter) window.Presenter.enter();
                }
            });

            doc.addEventListener('touchstart', function (e) {
                self.touchX = e.changedTouches[0].screenX;
            }, { passive: true });

            doc.addEventListener('touchend', function (e) {
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

        toggleFullscreen: function () {
            if (IS_EMBED) return;
            if (doc.fullscreenElement && doc.exitFullscreen) {
                doc.exitFullscreen();
            } else if (doc.documentElement.requestFullscreen) {
                doc.documentElement.requestFullscreen().catch(function () {});
            }
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

            if (IS_EMBED) return;               // 预览 iframe 不滚动、不广播
            window.scrollTo(0, 0);
            doc.dispatchEvent(new CustomEvent('deck:change', {
                detail: { index: this.index, total: this.slides.length, slideId: slide.dataset.slideId }
            }));
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

        titleAt: function (i) {
            var s = this.slides[i];
            if (!s) return '';
            var t = s.querySelector('.content-title, .cover-title, .toc-title, .close-thanks');
            var text = t ? t.textContent : '';
            return text.replace(/\s+/g, ' ').trim().slice(0, 120);
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
                    container.dataset.initialized = 'true';
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
                        container.innerHTML = '<p style="color:var(--danger);">Mermaid 渲染失败：' +
                            esc(err && err.message ? err.message : err) + '</p>';
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
            if (IS_EMBED || !$all('.image-item img').length) return;
            this.createOverlay();
            var self = this;
            $all('.image-item img').forEach(function (img) {
                img.style.cursor = 'pointer';
                img.addEventListener('click', function () { self.show(img.src); });
            });
        },

        createOverlay: function () {
            var overlay = doc.createElement('div');
            overlay.className = 'lightbox-overlay';
            overlay.innerHTML = '<div class="lightbox-content">' +
                '<div class="lightbox-close" role="button" tabindex="0" aria-label="关闭">&times;</div>' +
                '<img src="" alt="预览"></div>';
            body.appendChild(overlay);
            this.overlay = overlay;

            overlay.querySelector('.lightbox-close').addEventListener('click', this.hide.bind(this));
            overlay.addEventListener('click', function (e) {
                if (e.target === overlay) this.hide();
            }.bind(this));
            doc.addEventListener('keydown', function (e) {
                if (e.key === 'Escape') this.hide();
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
            if (!title.hasAttribute('tabindex')) title.setAttribute('tabindex', '0');
            if (!title.hasAttribute('role')) title.setAttribute('role', 'button');
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
    // 演讲者视图
    // ============================================================
    var Presenter = {
        el: null,
        active: false,
        mainIndex: 0,
        audience: null,
        channel: null,
        timer: { startedAt: 0, base: 0, running: false, pageBase: 0, pageStartedAt: 0 },
        pagePlannedMs: null,
        notes: [],
        fitObserver: null,
        laser: null,

        // 备注数据源：页面内 SPEAKER_NOTES 常量（按 data-slide-id 对齐）
        readNotes: function () {
            var raw = window.SPEAKER_NOTES;
            return Array.isArray(raw) ? raw : [];
        },

        noteFor: function (slide) {
            var id = slide && slide.dataset.slideId;
            var found = null;
            this.notes.some(function (n) { return n && n.id === id && (found = n); });
            if (found) return found;
            // 缺备注时给出中性占位，不虚构内容
            return {
                id: id || '',
                title: SlideEngine.titleAt(SlideEngine.slides.indexOf(slide)) || slide.dataset.slideId,
                purpose: '—',
                talk: [],
                transition: ''
            };
        },

        savedNote: function (id) {
            try {
                var raw = localStorage.getItem(PDF_KEY + ':note:' + id);
                return raw == null ? null : raw;
            } catch (e) {
                return null;
            }
        },

        enter: function () {
            if (this.active) return;
            this.notes = this.readNotes();
            this.active = true;
            this.screenMode = 'normal';
            this.frozen = null;
            this.mainIndex = SlideEngine.index;

            this.mount();
            body.classList.add('presenter-on');
            this.render();
            this.openAudience();
            this.bindTransport();
            this.fitAll();
        },

        exit: function () {
            if (!this.active) return;
            this.stopLaser();
            this.pauseTimer();
            this.broadcast({ type: 'bye' });
            if (this.audience && !this.audience.closed) {
                try { this.audience.close(); } catch (e) {}
            }
            this.audience = null;
            this.closeChannel();
            if (this.el) this.el.hidden = true;
            body.classList.remove('presenter-on');
            this.active = false;
            // 退出时把主讲页同步回观众窗口（如果还开着），保证不丢失位置
            this.focusMain();
        },

        mount: function () {
            if (this.el) { this.el.hidden = false; return; }
            var root = doc.createElement('div');
            root.className = 'presenter';
            root.setAttribute('role', 'dialog');
            root.setAttribute('aria-modal', 'true');
            root.setAttribute('aria-label', '演讲者视图');
            root.innerHTML = [
                '<div class="pr-top">',
                '<div class="pr-brand">演讲者视图</div>',
                '<div class="pr-meta">',
                '<span class="pr-section" data-pr="section" hidden></span>',
                '<span class="pr-sync" data-pr="sync" data-state="disconnected">观众屏 · 未连接</span>',
                '<button class="pr-btn" type="button" data-pr="reopen">重新打开观众屏</button>',
                '<button class="pr-btn" type="button" data-pr="exit">退出（P）</button>',
                '</div>',
                '</div>',
                '<div class="pr-main">',
                '<div class="pr-stage">',
                '<div class="pr-card">',
                '<div class="pr-card-head"><span>当前页</span><span data-pr="now-label"></span></div>',
                '<div class="pr-viewport"><div class="pr-fit" data-pr="cur-fit">',
                '<iframe title="当前页预览" data-pr="cur"></iframe>',
                '<canvas class="pr-ink" data-pr="ink"></canvas>',
                '</div></div>',
                '</div>',
                '<div class="pr-card">',
                '<div class="pr-card-head"><span>下一页</span><span data-pr="next-label"></span></div>',
                '<div class="pr-viewport"><div class="pr-fit" data-pr="next-fit">',
                '<iframe title="下一页预览" data-pr="next"></iframe>',
                '</div></div>',
                '</div>',
                '</div>',
                '<div class="pr-notes" data-pr="notes"></div>',
                '</div>',
                '<div class="pr-bottom">',
                '<div class="pr-timer"><span class="pr-t-label">已进行</span><strong data-pr="clock">00:00</strong>',
                '<span class="pr-t-hint" data-pr="plan-hint"></span></div>',
                '<div class="pr-timer"><span class="pr-t-label">本页</span><strong data-pr="page-clock">00:00</strong>',
                '<span class="pr-t-hint" data-pr="page-hint"></span></div>',
                '<div class="pr-keys">P 退出 · ← → 翻页 · Home/End 首尾 · L 激光笔 · C 圈选 · X 清除 · B 黑屏 · W 白屏 · F 冻结 · R 计时</div>',
                '<div class="pr-page"><strong data-pr="cur-page">1</strong><span data-pr="total-page">/ 1</span></div>',
                '</div>',
                '<div class="pr-freeze-badge">观众屏已冻结 · F 恢复</div>'
            ].join('');
            body.appendChild(root);
            this.el = root;

            var self = this;
            // 所有按钮只做「显式点击」的备份通道；键盘才是主通道
            root.addEventListener('click', function (e) {
                var btn = e.target.closest('[data-pr]');
                if (!btn) return;
                switch (btn.dataset.pr) {
                    case 'exit': self.exit(); break;
                    case 'reopen': self.openAudience(true); break;
                }
            });
            this.prefillFrames();
        },

        prefillFrames: function () {
            var self = this;
            var cur = $('[data-pr="cur"]', this.el);
            var next = $('[data-pr="next"]', this.el);
            [cur, next].forEach(function (f) {
                f.addEventListener('load', function () {
                    self.postTo(f, { type: 'goto', index: Number(f.dataset.index || 0) });
                });
            });
            // 16:9 等比缩放的容器观察
            if (window.ResizeObserver) {
                this.fitObserver = new ResizeObserver(function () { self.fitAll(); });
                $all('.pr-fit', this.el).forEach(function (box) { self.fitObserver.observe(box.parentNode); });
            }
        },

        // 观众屏 / 预览都用 1600×900 渲染 iframe，用 CSS transform 等比缩放
        syncFrame: function (frame, index) {
            if (!frame) return;
            frame.dataset.index = String(index);
            if (!frame.getAttribute('src')) {
                frame.src = this.frameUrl(index);
            } else {
                this.postTo(frame, { type: 'goto', index: index });
            }
        },

        frameUrl: function (index) {
            var base = location.href.replace(/#.*$/, '').replace(/[?&](start|mode|session)=[^&]*/g, '');
            base = base.replace(/[?&]$/, '');
            var sep = base.indexOf('?') === -1 ? '?' : '&';
            return base + sep + 'mode=preview&session=' + encodeURIComponent(SESSION || 'local') +
                '&start=' + ((index || 0) + 1);
        },

        postTo: function (frame, message) {
            try {
                if (frame.contentWindow) {
                    frame.contentWindow.postMessage(Object.assign({ __deckSync: 1, session: SESSION }, message), '*');
                }
            } catch (e) {}
        },

        render: function () {
            var total = SlideEngine.slides.length;
            var i = this.mainIndex;
            var curSlide = SlideEngine.slides[i];
            var note = this.noteFor(curSlide);
            var el = this.el;

            $('[data-pr="cur-page"]', el).textContent = (i + 1);
            $('[data-pr="total-page"]', el).textContent = '/ ' + total;

            var sectionEl = $('[data-pr="section"]', el);
            if (note.section) {
                sectionEl.textContent = note.section;
                sectionEl.hidden = false;
            } else {
                sectionEl.hidden = true;
            }

            var nowLabel = $('[data-pr="now-label"]', el);
            var nextLabel = $('[data-pr="next-label"]', el);
            nowLabel.textContent = note.title || SlideEngine.titleAt(i);
            nextLabel.textContent = i + 1 < total
                ? (SlideEngine.titleAt(i + 1) || SlideEngine.slides[i + 1].dataset.slideId)
                : '演示结束';

            this.syncFrame($('[data-pr="cur"]', el), i);
            this.syncFrame($('[data-pr="next"]', el), Math.min(i + 1, total - 1));

            this.renderNotes(note);
            this.setPagePlan(note);
            this.fitAll();
            this.applyScreen();
        },

        renderNotes: function (note) {
            var el = this.el;
            var box = $('[data-pr="notes"]', el);
            var custom = this.savedNote(note.id);
            var talk = toLines(note.talk);
            var extras = [
                ['舞台提示', toLines(note.cue)],
                ['互动', toLines(note.interaction)],
                ['表达', toLines(note.delivery)],
                ['翻页时机', toLines(note.advance)],
                ['备用方案', toLines(note.fallback)],
                ['读音', toLines(note.pronunciation)]
            ].filter(function (pair) { return pair[1].length; });

            var html = '';
            html += '<div class="pr-note-title">' + esc(note.title || '—') + '</div>';
            html += '<div class="pr-note-sub">';
            html += '<span>' + (note.section ? esc(note.section) : '') + '</span>';
            html += '<span data-pr="note-time"></span>';
            html += '</div>';
            html += '<div><div class="pr-block-label">本页目的</div><div class="pr-purpose">' + esc(note.purpose || '—') + '</div></div>';

            if (talk.length) {
                html += '<div><div class="pr-block-label">讲述要点</div><ul class="pr-talk">' +
                    talk.map(function (t) { return '<li>' + esc(t) + '</li>'; }).join('') + '</ul></div>';
            }
            if (custom != null && custom.trim()) {
                html += '<div><div class="pr-block-label">现场草稿</div>' +
                    '<div class="pr-purpose" style="white-space:pre-wrap">' + esc(custom) + '</div></div>';
            }
            if (extras.length) {
                html += '<div class="pr-extra">' + extras.map(function (pair) {
                    return '<div class="pr-extra-item"><b>' + pair[0] + '</b>' +
                        pair[1].map(esc).join('<br>') + '</div>';
                }).join('') + '</div>';
            }
            if (note.transition) {
                html += '<div class="pr-transition"><b>转场 →</b> ' + esc(note.transition) + '</div>';
            }
            box.innerHTML = html;

            // 应用上次保存的字号
            var size = 17;
            try { size = Number(localStorage.getItem(PDF_KEY + ':size')) || 17; } catch (e) {}
            box.style.setProperty('--pr-note-size', size + 'px');
        },

        setPagePlan: function (note) {
            var minutes = Number(note.minutes);
            this.pagePlannedMs = (minutes > 0 && isFinite(minutes)) ? Math.round(minutes * 60000) : null;
            this.timer.pageBase = 0;
            this.timer.pageStartedAt = Date.now();
            this.updatePlanHint();
        },

        updatePlanHint: function () {
            if (!this.el) return;
            var plan = $('[data-pr="plan-hint"]', this.el);
            var pageHint = $('[data-pr="page-hint"]', this.el);
            var totalMs = null;
            var sum = 0;
            var complete = this.notes.length > 0;
            this.notes.forEach(function (n) {
                var m = Number(n && n.minutes);
                if (!(m > 0)) complete = false;
                else sum += m * 60000;
            });
            if (complete && SlideEngine.slides.length) {
                totalMs = sum;
                var texts = ['计划 ' + this.dur(totalMs), '剩余 ' + this.dur(Math.max(0, totalMs - this.elapsed()))];
                plan.textContent = texts.join(' · ');
            } else {
                plan.textContent = '';
            }
            pageHint.textContent = this.pagePlannedMs ? ('计划 ' + this.dur(this.pagePlannedMs)) : '';
        },

        // --- 计时 ---
        elapsed: function () {
            return this.timer.base + (this.timer.running ? Date.now() - this.timer.startedAt : 0);
        },

        startTimer: function () {
            if (this.timer.running) return;
            this.timer.running = true;
            this.timer.startedAt = Date.now();
            this.timer.pageStartedAt = Date.now();
        },

        pauseTimer: function () {
            if (!this.timer.running) return;
            this.commitPageTime();
            this.timer.base = this.elapsed();
            this.timer.running = false;
        },

        resetTimer: function () {
            this.timer.base = 0;
            this.timer.startedAt = this.timer.running ? Date.now() : 0;
            this.timer.pageBase = 0;
            this.timer.pageStartedAt = Date.now();
        },

        toggleTimer: function () {
            if (this.timer.running) this.pauseTimer();
            else this.startTimer();
        },

        dur: function (ms) {
            var s = Math.max(0, Math.floor(ms / 1000));
            var m = Math.floor(s / 60);
            var r = s % 60;
            return (m < 10 ? '0' : '') + m + ':' + (r < 10 ? '0' : '') + r;
        },

        tick: function () {
            if (!this.el || !this.active) return;
            var clock = $('[data-pr="clock"]', this.el);
            var pageClock = $('[data-pr="page-clock"]', this.el);
            var pageMs = this.pageElapsedMs();

            clock.textContent = this.dur(this.elapsed());
            pageClock.textContent = this.dur(pageMs);
            clock.classList.toggle('is-running', this.timer.running);
            pageClock.classList.toggle('is-running', this.timer.running);
            pageClock.classList.toggle('is-overtime', !!(this.pagePlannedMs && pageMs > this.pagePlannedMs));

            var noteTime = $('[data-pr="note-time"]', this.el);
            if (noteTime) noteTime.textContent = '本页已讲 ' + this.dur(pageMs);

            var plan = $('[data-pr="plan-hint"]', this.el);
            var rest = this.remainingPlanMs();
            if (plan) {
                plan.textContent = rest == null ? '' :
                    '计划 ' + this.dur(this.totalPlannedMs()) +
                    ' · ' + (rest < 0 ? '超时 ' : '剩余 ') + this.dur(Math.abs(rest));
            }

            // 激光笔自动淡出
            if (this.laser && Date.now() - this.laser.at > 2200) {
                this.laser = null;
                this.drawInk();
            }
        },

        pageElapsedMs: function () {
            return this.timer.pageBase + (this.timer.running ? Date.now() - this.timer.pageStartedAt : 0);
        },

        // 把本页已运行时长累进 pageBase，再把起点推到当前时刻。
        // 计时暂停期间不累计，切页/暂停/重开都走这里。
        commitPageTime: function () {
            if (this.timer.running) this.timer.pageBase += Date.now() - this.timer.pageStartedAt;
            this.timer.pageStartedAt = Date.now();
        },

        pageBaseSec: function () { return this.timer.pageBase; },

        totalPlannedMs: function () {
            var sum = 0;
            for (var i = 0; i < this.notes.length; i++) {
                var m = Number(this.notes[i] && this.notes[i].minutes);
                if (!(m > 0)) return null;
                sum += m * 60000;
            }
            return this.notes.length ? sum : null;
        },

        remainingPlanMs: function () {
            var total = this.totalPlannedMs();
            return total == null ? null : total - this.elapsed();
        },

        // --- 翻页 ---
        next: function () {
            if (this.mainIndex >= SlideEngine.slides.length - 1) return;
            SlideEngine.goTo(this.mainIndex + 1);
        },

        prev: function () {
            if (this.mainIndex <= 0) return;
            SlideEngine.goTo(this.mainIndex - 1);
        },

        first: function () { if (this.mainIndex !== 0) SlideEngine.goTo(0); },
        last: function () { SlideEngine.goTo(SlideEngine.slides.length - 1); },

        onSlideChange: function (detail) {
            if (!this.active) return;
            this.mainIndex = detail.index;
            this.commitPageTime();
            this.render();
            this.laser = null;
            this.render();
        },

        // --- 激光笔 / 圈选 ---
        toggleLaserTool: function (tool) {
            this.tool = this.tool === tool ? 'none' : tool;
            this.circles = this.circles || [];
            if (this.tool !== 'laser') this.laser = null;
            var canvas = $('[data-pr="ink"]', this.el);
            if (canvas) {
                canvas.dataset.tool = this.tool;
                canvas.style.pointerEvents = this.tool === 'none' ? 'none' : 'auto';
            }
            this.drawInk();
        },

        stopLaser: function () {
            this.tool = 'none';
            this.laser = null;
            this.circles = [];
            this.drawInk();
        },

        pointerAt: function (e) {
            var canvas = $('[data-pr="ink"]', this.el);
            if (!canvas) return null;
            var r = canvas.getBoundingClientRect();
            return {
                x: (e.clientX - r.left) / r.width,
                y: (e.clientY - r.top) / r.height
            };
        },

        bindTransport: function () {
            var self = this;
            if (this.transportBound) return;   // 只绑定一次；active 状态由 onSlideChange 控制
            this.transportBound = true;

            doc.addEventListener('deck:change', function (e) { self.onSlideChange(e.detail); });

            // 观众屏回报
            window.addEventListener('message', function (e) {
                var d = e.data;
                if (!d || !d.__deckSync) return;
                if (d.type !== 'ack' || !self.audience) return;
                var mode = self.screenMode || 'normal';
                if (mode === 'black') self.setSyncIcon('black');
                else if (mode === 'white') self.setSyncIcon('white');
                else if (mode === 'frozen') self.setSyncIcon('frozen');
                else self.setSync(d.index === self.mainIndex ? 'connected' : 'stale');
            });

            // 跨窗口 / 同源备用通道
            try {
                this.channel = new BroadcastChannel(SYNC_KEY);
                this.channel.onmessage = function (e) {
                    var d = e.data;
                    if (!d || !d.__deckSync) return;
                    if (d.type === 'ack' && self.audience) {
                        self.setSync(d.index === self.mainIndex ? 'connected' : 'stale');
                    }
                };
            } catch (e) {}

            // 键盘：演讲者视图主通道
            doc.addEventListener('keydown', function (e) {
                if (!self.active) return;
                var tag = (e.target && e.target.tagName) || '';
                if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return;

                switch (e.key) {
                    case 'ArrowRight': case 'PageDown': case ' ':
                        e.preventDefault(); self.next(); break;
                    case 'ArrowLeft': case 'PageUp':
                        e.preventDefault(); self.prev(); break;
                    case 'Home':
                        e.preventDefault(); self.first(); break;
                    case 'End':
                        e.preventDefault(); self.last(); break;
                    case 'p': case 'P':
                        e.preventDefault(); self.exit(); break;
                    case 'l': case 'L':
                        self.toggleLaserTool('laser'); break;
                    case 'c': case 'C':
                        self.toggleLaserTool('circle'); break;
                    case 'x': case 'X': case 'Escape':
                        if (e.key === 'Escape') { e.preventDefault(); self.exit(); break; }
                        self.stopLaser(); break;
                    case 'b': case 'B':
                        self.setScreen('black'); break;
                    case 'w': case 'W':
                        self.setScreen('white'); break;
                    case 'f': case 'F':
                        self.setScreen('frozen'); break;
                    case 'r': case 'R':
                        self.toggleTimer(); break;
                    case '+': case '=':
                        self.setNoteSize(1); break;
                    case '-':
                        self.setNoteSize(-1); break;
                }
            });

            // 鼠标/触控笔：激光点与拖拽圈选（触控板也可用）
            var canvas = $('[data-pr="ink"]', this.el);
            if (canvas) {
                var down = null;
                canvas.addEventListener('pointermove', function (e) {
                    if (self.tool === 'laser') {
                        self.laser = { point: self.pointerAt(e), at: Date.now() };
                        self.drawInk();
                    } else if (self.tool === 'circle' && down) {
                        var p = self.pointerAt(e);
                        down.draft = { x1: down.start.x, y1: down.start.y, x2: p.x, y2: p.y };
                        self.circles = self.circles.slice(0, down.saved);
                        self.circles.push(down.draft);
                        self.drawInk();
                    }
                });
                canvas.addEventListener('pointerdown', function (e) {
                    if (self.tool !== 'circle') return;
                    canvas.setPointerCapture && canvas.setPointerCapture(e.pointerId);
                    down = { start: self.pointerAt(e), saved: self.circles.length };
                });
                canvas.addEventListener('pointerup', function () {
                    down = null;
                });
                canvas.addEventListener('pointerleave', function () {
                    down = null;
                });
            }

            this.tickTimer = setInterval(function () { self.tick(); }, 1000);
        },

        setNoteSize: function (delta) {
            var box = $('[data-pr="notes"]', this.el);
            if (!box) return;
            var cur = Number(getComputedStyle(box).getPropertyValue('--pr-note-size')) || 17;
            var next = Math.min(26, Math.max(13, cur + delta));
            box.style.setProperty('--pr-note-size', next + 'px');
            try { localStorage.setItem(PDF_KEY + ':size', String(next)); } catch (e) {}
        },

        drawInk: function () {
            var canvas = $('[data-pr="ink"]', this.el);
            if (!canvas) return;
            var box = canvas.parentNode;
            var w = box.clientWidth;
            var h = box.clientHeight;
            if (!w || !h) return;
            var dpr = Math.min(window.devicePixelRatio || 1, 2);
            if (canvas.width !== Math.round(w * dpr) || canvas.height !== Math.round(h * dpr)) {
                canvas.width = Math.round(w * dpr);
                canvas.height = Math.round(h * dpr);
            }
            canvas.style.width = w + 'px';
            canvas.style.height = h + 'px';
            var ctx = canvas.getContext('2d');
            ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
            ctx.clearRect(0, 0, w, h);

            (this.circles || []).forEach(function (c) {
                ctx.save();
                ctx.strokeStyle = '#ff4f59';
                ctx.lineWidth = Math.max(2, w * 0.003);
                ctx.beginPath();
                ctx.ellipse((c.x1 + c.x2) / 2 * w, (c.y1 + c.y2) / 2 * h,
                    Math.abs(c.x2 - c.x1) / 2 * w, Math.abs(c.y2 - c.y1) / 2 * h, 0, 0, Math.PI * 2);
                ctx.stroke();
                ctx.restore();
            });
            if (this.laser) {
                var p = this.laser.point;
                var x = p.x * w,
                    y = p.y * h,
                    r = Math.max(5, w * 0.006);
                var g = ctx.createRadialGradient(x, y, 0, x, y, r * 2.6);
                g.addColorStop(0, 'rgba(255,255,255,.98)');
                g.addColorStop(0.25, 'rgba(255,64,72,.95)');
                g.addColorStop(1, 'rgba(255,64,72,0)');
                ctx.fillStyle = g;
                ctx.beginPath();
                ctx.arc(x, y, r * 2.6, 0, Math.PI * 2);
                ctx.fill();
            }
        },

        // 观众屏状态：normal / black / white / frozen。
        // frozen 时演讲者继续翻页，观众屏停在原页，恢复后立即追平。
        setScreen: function (mode) {
            this.screenMode = this.screenMode === mode && mode !== 'normal' ? 'normal' : mode;
            body.classList.toggle('audience-black', this.screenMode === 'black');
            body.classList.toggle('audience-frozen', this.screenMode === 'frozen');
            this.applyScreen();
        },

        applyScreen: function () {
            var mode = this.screenMode || 'normal';
            if (mode !== 'frozen') this.frozen = null;
            if (mode === 'frozen' && !this.frozen) {
                this.frozen = { index: this.mainIndex };
            }
            this.broadcast({
                type: 'screen',
                mode: mode,
                index: this.mainIndex,
                frozenIndex: this.frozen ? this.frozen.index : this.mainIndex
            });
            if (mode === 'black') this.setSyncIcon('black');
            else if (mode === 'white') this.setSyncIcon('white');
            else if (mode === 'frozen') this.setSyncIcon('frozen');
            else this.setSyncIcon('stale');
        },

        // --- 观众屏 ---
        openAudience: function (reopen) {
            var self = this;
            if (this.audience && !this.audience.closed) {
                try { this.audience.focus(); } catch (e) {}
                this.broadcast({ type: 'goto', index: this.mainIndex });
                return;
            }
            var url = location.href.replace(/#.*$/, '') +
                (location.search ? '&' : '?') + 'mode=audience&session=' + encodeURIComponent(SESSION || 'local');
            var popup = window.open(url, 'h5-report-audience-' + (SESSION || 'local'),
                'width=1280,height=760');
            if (!popup) {
                this.setSyncIcon('blocked');
                return;
            }
            this.audience = popup;
            this.setSyncIcon('stale');
            if (reopen) this.broadcast({ type: 'goto', index: this.mainIndex });
            // 观众窗口刷新后回来要重新对齐
            var poll = setInterval(function () {
                if (!self.audience || self.audience.closed) {
                    clearInterval(poll);
                    if (self.active) self.setSyncIcon('disconnected');
                    return;
                }
                self.applyScreen();
            }, 2000);
        },

        setSync: function (state) { this.setSyncIcon(state); },

        setSyncIcon: function (state) {
            if (!this.el) return;
            var el = $('[data-pr="sync"]', this.el);
            if (!el) return;
            var map = {
                connected: '观众屏 · 已同步',
                stale: '观众屏 · 连接中',
                black: '观众屏 · 黑屏',
                white: '观众屏 · 白屏',
                frozen: '观众屏 · 已冻结',
                blocked: '观众屏 · 弹窗被拦截',
                disconnected: '观众屏 · 未连接'
            };
            var key = map[state] ? state : 'stale';
            el.dataset.state = key;
            el.textContent = map[key];
        },

        broadcast: function (message) {
            var payload = Object.assign({ __deckSync: 1, session: SESSION, index: this.mainIndex }, message);
            try {
                if (this.audience && !this.audience.closed) {
                    this.audience.postMessage(payload, '*');
                }
            } catch (e) {}
            try { if (this.channel) this.channel.postMessage(payload); } catch (e) {}
        },

        closeChannel: function () {
            try { if (this.channel) this.channel.close(); } catch (e) {}
            this.channel = null;
        },

        // 16:9 等比：iframe 固定 1600×900，容器按可用空间缩放
        fitAll: function () {
            if (!this.el) return;
            var self = this;
            $all('.pr-fit', this.el).forEach(function (box) {
                var host = box.parentNode;
                var aw = host.clientWidth;
                var ah = host.clientHeight;
                if (!aw || !ah) return;
                var scale = Math.min(aw / 1600, ah / 900);
                var w = Math.round(1600 * scale);
                var h = Math.round(900 * scale);
                box.style.width = w + 'px';
                box.style.height = h + 'px';
                var frame = box.querySelector('iframe');
                if (frame) frame.style.transform = 'scale(' + scale + ')';
                var canvas = box.querySelector('canvas');
                if (canvas) self.drawInk();
            });
        },

        // 退出演讲者时，把观众窗口的当前页对齐
        focusMain: function () {
            try {
                if (window.opener && MODE === 'audience') {
                    window.opener.postMessage({ __deckSync: 1, type: 'bye' }, '*');
                }
            } catch (e) {}
        }
    };

    // ============================================================
    // 观众屏 / 预览：接收主窗口指令
    // ============================================================
    function initSlave() {
        var curtain = doc.createElement('div');
        curtain.className = 'audience-curtain';
        curtain.textContent = '演示结束';
        body.appendChild(curtain);

        // 预览/观众屏都按 URL 参数先定位
        var start = Number(params.get('start'));
        if (start > 1 && start <= SlideEngine.slides.length) {
            SlideEngine.goTo(start - 1);
        }

        window.addEventListener('message', function (e) {
            var d = e.data;
            if (!d || !d.__deckSync) return;
            if (d.session && SESSION && d.session !== SESSION) return;

            if (d.type === 'screen') {
                var mode = d.mode || 'normal';
                body.classList.toggle('audience-black', mode === 'black');
                body.classList.toggle('audience-white', mode === 'white');
                body.classList.toggle('audience-frozen', mode === 'frozen');
                if (mode === 'frozen') {
                    // 冻结期间不跟页；恢复时用最新 index 追平
                    ack();
                } else if (typeof d.index === 'number') {
                    SlideEngine.goTo(d.index);
                    SlideEngine.goTo(d.index); // 幂等：目标页相同时自行忽略
                    ack();
                }
            } else if (d.type === 'goto') {
                curtain.classList.remove('is-on');
                if (typeof d.index === 'number') SlideEngine.goTo(d.index);
                ack();
            } else if (d.type === 'bye') {
                if (MODE === 'audience') {
                    curtain.classList.add('is-on');
                    try { window.close(); } catch (err) {}
                }
            }
        });

        function ack() {
            try {
                if (window.opener) {
                    window.opener.postMessage({
                        __deckSync: 1, type: 'ack', index: SlideEngine.index,
                        black: body.classList.contains('audience-black'),
                        white: body.classList.contains('audience-white'),
                        frozen: body.classList.contains('audience-frozen'), session: SESSION
                    }, '*');
                }
            } catch (e) {}
        }

        // 观众屏心跳：连黑屏/暂停状态也要回报，避免两端状态判断不一致
        if (MODE === 'audience') {
            setInterval(ack, 1500);
        }
    }

    // ============================================================
    // 启动
    // ============================================================
    function boot() {
        SlideEngine.init();
        ImagePreview.init();
        initFoldSections();
        window.slideEngine = SlideEngine;
        window.Presenter = Presenter;

        if (IS_EMBED || IS_AUDIENCE) {
            initSlave();
            return;
        }

        // 右下角入口与主窗口导航保持一致，不额外悬浮抢眼按钮
        var nav = $('.navigation');
        if (nav) {
            var btn = doc.createElement('button');
            btn.className = 'nav-btn presenter-btn';
            btn.type = 'button';
            btn.title = '演讲者视图（P）';
            btn.setAttribute('aria-label', '演讲者视图（P）');
            btn.textContent = 'P';
            nav.insertBefore(btn, nav.firstChild);
            btn.addEventListener('click', function () { Presenter.enter(); });
        }
    }

    if (doc.readyState === 'loading') {
        doc.addEventListener('DOMContentLoaded', boot);
    } else {
        boot();
    }
})();
