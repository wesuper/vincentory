/**
 * Deck Interaction System
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
    // 键盘是主通道：讲者站在屏幕前或拿翻页笔，全程不必碰鼠标。
    // 视图固定深色，不跟随页面主题——全黑会议室里浅色备注栏刺眼。
    // ============================================================
    var Presenter = {
        el: null,
        active: false,
        mainIndex: 0,
        audience: null,
        channel: null,
        timer: { startedAt: 0, base: 0, running: false, pageBase: 0, pageStartedAt: 0 },
        pagePlannedMs: null,
        pageTimes: [],
        notes: [],
        fitObserver: null,
        laser: null,
        circles: [],
        tool: 'none',
        layout: 'balanced',
        overviewOn: false,
        dialogOpen: false,
        rehearsalOn: false,
        sync: { state: 'disconnected', lastAckAt: 0, ackIndex: -1, openedAt: 0 },
        saveTimer: 0,
        renderedNoteId: '',

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

        // 讲者在演讲者视图里改过的备注，按 data-slide-id 存档；改页不串页
        savedNote: function (id) {
            try {
                var raw = localStorage.getItem(PDF_KEY + ':note:' + id);
                return raw == null ? null : raw;
            } catch (e) {
                return null;
            }
        },

        storeNote: function (id, value) {
            try { localStorage.setItem(PDF_KEY + ':note:' + id, value); } catch (e) {}
        },

        enter: function () {
            if (this.active) return;
            this.notes = this.readNotes();
            try {
                var saved = localStorage.getItem(PDF_KEY + ':layout');
                if (saved) this.layout = saved;
            } catch (e) {}
            this.active = true;
            this.screenMode = 'normal';
            this.frozen = null;
            this.mainIndex = SlideEngine.index;
            this.pageTimes = [];
            this.circles = [];
            this.tool = 'none';
            this.overviewOn = false;
            this.dialogOpen = false;
            this.rehearsalOn = false;

            this.mount();
            body.classList.add('presenter-on');
            this.render();
            this.openAudience();
            this.bindTransport();
            this.fitAll();
        },

        exit: function () {
            if (!this.active) return;
            if (this.rehearsalOn) this.finishRehearsal(false);
            this.stopLaser();
            this.pauseTimer();
            this.broadcast({ type: 'bye' });
            if (this.audience && !this.audience.closed) {
                try { this.audience.close(); } catch (e) {}
            }
            this.audience = null;
            this.sync.state = 'disconnected';
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
            root.dataset.layout = this.layout;
            root.innerHTML = [
                '<div class="pr-top">',
                '<div class="pr-brand">演讲者视图',
                '<span class="pr-plan" data-pr="plan"></span>',
                '</div>',
                '<div class="pr-meta">',
                '<span class="pr-section" data-pr="section" hidden></span>',
                '<span class="pr-sync" data-pr="sync" data-state="disconnected">观众屏 · 未连接</span>',
                '<button class="pr-btn" type="button" data-pr="preflight">检查</button>',
                '<button class="pr-btn" type="button" data-pr="settings">设置</button>',
                '<button class="pr-btn" type="button" data-pr="reopen">重新打开观众屏</button>',
                '<button class="pr-btn" type="button" data-pr="exit">退出（P）</button>',
                '</div>',
                '</div>',
                '<div class="pr-main">',
                '<div class="pr-stage">',
                '<div class="pr-card">',
                '<div class="pr-card-head">',
                '<span>当前页 <button class="pr-mini" type="button" data-pr="grid" aria-pressed="false">宫格 G</button></span>',
                '<span class="pr-tools">',
                '<button class="pr-mini" type="button" data-pr="tool" data-tool="laser" title="激光笔（L）">激光</button>',
                '<button class="pr-mini" type="button" data-pr="tool" data-tool="circle" title="圈选（C）">圈选</button>',
                '<button class="pr-mini" type="button" data-pr="ink-clear" title="清除标注（X）">清除</button>',
                '</span>',
                '<span data-pr="now-label"></span>',
                '</div>',
                '<div class="pr-viewport"><div class="pr-fit" data-pr="cur-fit">',
                '<iframe title="当前页预览" data-pr="cur"></iframe>',
                '<canvas class="pr-ink" data-pr="ink"></canvas>',
                '</div></div>',
                '</div>',
                '<div class="pr-card pr-next">',
                '<div class="pr-card-head"><span>下一页</span><span data-pr="next-label"></span></div>',
                '<div class="pr-viewport"><div class="pr-fit" data-pr="next-fit">',
                '<iframe title="下一页预览" data-pr="next"></iframe>',
                '</div></div>',
                '</div>',
                // 宫格替换的是「预览区」，不是备注区：问答时讲者还要看着备注决定跳哪页
                '<div class="pr-overview" data-pr="overview" hidden>',
                '<div class="pr-overview-head"><strong>选择页面</strong>',
                '<button class="pr-mini" type="button" data-pr="grid-close">返回预览</button></div>',
                '<div class="pr-overview-grid" data-pr="overview-grid"></div>',
                '</div>',
                '</div>',
                '<div class="pr-side">',
                '<div class="pr-side-main">',
                '<div class="pr-notes" data-pr="notes"></div>',
                '<div class="pr-draft" data-pr="draft-box">',
                '<div class="pr-draft-head"><span class="pr-block-label">现场草稿</span>',
                '<span class="pr-draft-tools">',
                '<span class="pr-saved" data-pr="saved"></span>',
                '<button class="pr-mini" type="button" data-pr="size" data-delta="-1" title="缩小备注字号">A−</button>',
                '<button class="pr-mini" type="button" data-pr="size" data-delta="1" title="放大备注字号">A+</button>',
                '</span></div>',
                '<textarea class="pr-draft-input" data-pr="draft" id="pr-draft-input" name="pr-draft" ' +
                'spellcheck="false" aria-label="本页现场草稿" ' +
                'placeholder="临时提醒，例如「领导可能追问口径」"></textarea>',
                '</div>',
                '</div>',
                '</div>',
                '</div>',
                '<div class="pr-bottom">',
                '<div class="pr-timers">',
                '<div class="pr-timer"><span class="pr-t-label">已进行</span><strong data-pr="clock">00:00</strong></div>',
                '<div class="pr-timer"><span class="pr-t-label">本页</span><strong data-pr="page-clock">00:00</strong>',
                '<span class="pr-t-hint" data-pr="page-hint"></span></div>',
                '<div class="pr-timer"><span class="pr-t-label" data-pr="budget-label">计划</span><strong data-pr="budget">—</strong>',
                '<span class="pr-t-hint" data-pr="budget-hint"></span></div>',
                '</div>',
                '<div class="pr-transport">',
                '<button class="pr-btn" type="button" data-pr="first">首页</button>',
                '<button class="pr-btn" type="button" data-pr="prev">上一页</button>',
                '<button class="pr-btn" type="button" data-pr="next">下一页</button>',
                '<button class="pr-btn" type="button" data-pr="last">尾页</button>',
                '<span class="pr-sep"></span>',
                '<button class="pr-btn" type="button" data-pr="timer">开始计时</button>',
                '<button class="pr-btn" type="button" data-pr="timer-reset">重置计时</button>',
                '<button class="pr-btn" type="button" data-pr="rehearsal">排练</button>',
                '</div>',
                '<div class="pr-page"><strong data-pr="cur-page">1</strong><span data-pr="total-page">/ 1</span>',
                '<span class="pr-pct" data-pr="pct"></span></div>',
                '</div>',
                '<div class="pr-dialog" data-pr="dialog" hidden>',
                '<div class="pr-dialog-panel" role="dialog" aria-modal="true">',
                '<div class="pr-dialog-head"><strong data-pr="dialog-title"></strong>',
                '<button class="pr-mini" type="button" data-pr="dialog-close">关闭</button></div>',
                '<div class="pr-dialog-body" data-pr="dialog-body"></div>',
                '</div>',
                '</div>',
                '<div class="pr-freeze-badge">观众屏已冻结 · F 恢复</div>'
            ].join('');
            body.appendChild(root);
            this.el = root;

            var self = this;
            root.addEventListener('click', function (e) {
                var btn = e.target.closest('[data-pr]');
                if (!btn) return;
                var action = btn.dataset.pr;
                if (btn.dataset.tool) { self.setTool(btn.dataset.tool); return; }
                switch (action) {
                    case 'exit': self.exit(); break;
                    case 'reopen': self.openAudience(true); break;
                    case 'grid': case 'grid-close': self.toggleOverview(); break;
                    case 'tool': self.setTool(btn.dataset.tool); break;
                    case 'ink-clear': self.clearInk(); break;
                    case 'first': self.first(); break;
                    case 'prev': self.prev(); break;
                    case 'next': self.next(); break;
                    case 'route-next': self.nextCore(); break;
                    case 'last': self.last(); break;
                    case 'timer': self.toggleTimer(); break;
                    case 'timer-reset': self.resetTimer(); break;
                    case 'rehearsal': self.toggleRehearsal(); break;
                    case 'preflight': self.openPreflight(); break;
                    case 'settings': self.openSettings(); break;
                    case 'dialog-close': self.closeDialog(); break;
                }
            });
            var dialog = $('[data-pr="dialog"]', root);
            dialog.addEventListener('click', function (e) {
                if (e.target === dialog) self.closeDialog();
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
            if (!this.el) return;
            var total = SlideEngine.slides.length;
            var i = this.mainIndex;
            var curSlide = SlideEngine.slides[i];
            var note = this.noteFor(curSlide);
            var el = this.el;

            $('[data-pr="cur-page"]', el).textContent = (i + 1);
            $('[data-pr="total-page"]', el).textContent = '/ ' + total;
            var pct = $('[data-pr="pct"]', el);
            if (pct) pct.textContent = Math.round(((i + 1) / total) * 100) + '%';

            var sectionEl = $('[data-pr="section"]', el);
            if (note.section) {
                sectionEl.textContent = note.section + this.sectionProgress(note.section);
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
            this.updateTransport();
            this.tick();
            this.fitAll();
            this.applyScreen();
            if (this.overviewOn) this.buildOverview();
        },

        // 章节内进度：有 section 的页面连续成组时显示「2/5」
        sectionProgress: function (section) {
            var mine = [], i, n;
            for (i = 0; i < SlideEngine.slides.length; i++) {
                n = this.noteFor(SlideEngine.slides[i]);
                if (n.section === section) mine.push(i);
            }
            if (mine.length < 2) return '';
            return ' · ' + (mine.indexOf(this.mainIndex) + 1) + '/' + mine.length;
        },

        nextCoreIndex: function () {
            var route = window.PRESENTATION_ROUTE;
            if (!route || !Array.isArray(route.core_slide_ids)) return -1;
            for (var i = this.mainIndex + 1; i < SlideEngine.slides.length; i++) {
                if (route.core_slide_ids.indexOf(SlideEngine.slides[i].dataset.slideId) !== -1) return i;
            }
            return -1;
        },

        nextCore: function () {
            var target = this.nextCoreIndex();
            if (target >= 0) SlideEngine.goTo(target);
        },

        renderNotes: function (note) {
            var el = this.el;
            var box = $('[data-pr="notes"]', el);
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
            html += '<div class="pr-note-sub"><span>' + (note.section ? esc(note.section) : '') + '</span>' +
                '<span data-pr="note-time"></span></div>';
            html += '<div><div class="pr-block-label">本页目的</div>' +
                '<div class="pr-purpose">' + esc(note.purpose || '—') + '</div></div>';

            var route = window.PRESENTATION_ROUTE;
            if (route && Array.isArray(route.core_slide_ids) && route.core_slide_ids.length) {
                var isCore = route.core_slide_ids.indexOf(note.id) !== -1;
                var target = this.nextCoreIndex();
                html += '<div class="pr-route"><b>压缩路线 · ' +
                    (isCore ? '核心页' : '可选深挖页') + '</b><span> 核心页备注预算 ' +
                    esc(String(route.short_minutes)) + ' 分钟</span>';
                if (target >= 0 && target > this.mainIndex + 1) {
                    html += '<button type="button" class="pr-btn" data-pr="route-next">跳到下一核心页（第 ' +
                        (target + 1) + ' 页）</button>';
                }
                html += '</div>';
            }
            if (talk.length) {
                html += '<div><div class="pr-block-label">讲述要点</div><ul class="pr-talk">' +
                    talk.map(function (t) { return '<li>' + esc(t) + '</li>'; }).join('') + '</ul></div>';
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
            box.scrollTop = 0;

            this.renderDraft(note);

            // 应用上次保存的字号
            box.style.setProperty('--pr-note-size', this.noteSize() + 'px');
            this.renderedNoteId = note.id;
        },

        // 现场草稿固定在备注栏下方，不随备注正文滚动——
        // 讲者临时补的那一句必须永远在最顺手的位置，翻到页尾也能写。
        renderDraft: function (note) {
            var self = this;
            var draft = $('[data-pr="draft"]', this.el);
            if (!draft) return;
            var saved = this.savedNote(note.id);
            draft.value = saved == null ? '' : saved;
            draft.oninput = function () { self.queueNoteSave(note.id); };
            draft.onkeydown = function (e) {
                // 编辑备注时方向键属于光标，不是翻页
                e.stopPropagation();
            };
            if (this._boundSize) return;
            this._boundSize = true;
            $all('[data-pr="size"]', this.el).forEach(function (b) {
                b.addEventListener('click', function () {
                    self.setNoteSize(Number(b.dataset.delta));
                });
            });
        },

        queueNoteSave: function (id) {
            var self = this;
            var saved = $('[data-pr="saved"]', this.el);
            if (saved) saved.textContent = '保存中…';
            clearTimeout(this.saveTimer);
            this.saveTimer = setTimeout(function () {
                var box = $('[data-pr="draft"]', self.el);
                self.storeNote(id, box ? box.value : '');
                if (saved) saved.textContent = '已保存';
            }, 300);
        },

        noteSize: function () {
            var size = 17;
            try { size = Number(localStorage.getItem(PDF_KEY + ':size')) || 17; } catch (e) {}
            return size;
        },

        setNoteSize: function (delta) {
            var box = $('[data-pr="notes"]', this.el);
            if (!box) return;
            var next = Math.min(26, Math.max(13, this.noteSize() + delta));
            box.style.setProperty('--pr-note-size', next + 'px');
            try { localStorage.setItem(PDF_KEY + ':size', String(next)); } catch (e) {}
        },

        setPagePlan: function (note) {
            var minutes = Number(note.minutes);
            this.pagePlannedMs = (minutes > 0 && isFinite(minutes)) ? Math.round(minutes * 60000) : null;
            // 不在这里清零：切页由 onSlideChange 统一提交并清零，避免读者在 render 里丢时间
            this.updatePlanHint();
        },

        updatePlanHint: function () {
            if (!this.el) return;
            var plan = $('[data-pr="plan"]', this.el);
            var pageHint = $('[data-pr="page-hint"]', this.el);
            var total = this.totalPlannedMs();
            if (plan) {
                plan.textContent = total == null ? '' :
                    '总计划 ' + this.dur(total) + ' · 预计 ' +
                    this.clockTime(Date.now() + Math.max(0, total - this.elapsed()));
            }
            pageHint.textContent = this.pagePlannedMs ? ('计划 ' + this.dur(this.pagePlannedMs)) : '';
        },

        // --- 计时 ---
        elapsed: function () {
            return this.timer.base + (this.timer.running ? Date.now() - this.timer.startedAt : 0);
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

        startTimer: function () {
            if (this.timer.running) return;
            this.timer.running = true;
            this.timer.startedAt = Date.now();
            this.timer.pageStartedAt = Date.now();
            this.tick();
        },

        pauseTimer: function () {
            if (!this.timer.running) return;
            this.commitPageTime();
            this.timer.base = this.elapsed();
            this.timer.running = false;
            this.tick();
        },

        resetTimer: function () {
            this.commitPageTime();
            this.timer.base = 0;
            this.timer.pageBase = 0;
            this.timer.startedAt = this.timer.running ? Date.now() : 0;
            this.timer.pageStartedAt = Date.now();
            this.pageTimes = [];
            this.tick();
        },

        toggleTimer: function () {
            if (this.timer.running) this.pauseTimer();
            else this.startTimer();
            this.updateTransport();
        },

        dur: function (ms) {
            var s = Math.max(0, Math.floor(ms / 1000));
            var m = Math.floor(s / 60);
            var r = s % 60;
            return (m < 10 ? '0' : '') + m + ':' + (r < 10 ? '0' : '') + r;
        },

        signed: function (ms) {
            return (ms >= 0 ? '+' : '−') + this.dur(Math.abs(ms));
        },

        clockTime: function (ts) {
            var d = new Date(ts);
            return (d.getHours() < 10 ? '0' : '') + d.getHours() + ':' +
                (d.getMinutes() < 10 ? '0' : '') + d.getMinutes();
        },

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

        updateTransport: function () {
            var el = this.el;
            if (!el) return;
            var btn = $('[data-pr="timer"]', el);
            if (btn) btn.textContent = this.timer.running ? '暂停计时'
                : (this.elapsed() ? '继续计时' : '开始计时');
            var reh = $('[data-pr="rehearsal"]', el);
            if (reh) {
                reh.textContent = this.rehearsalOn ? '结束排练' : '排练';
                reh.classList.toggle('is-on', this.rehearsalOn);
            }
            var total = SlideEngine.slides.length;
            var first = $('[data-pr="first"]', el);
            var prev = $('[data-pr="prev"]', el);
            var next = $('[data-pr="next"]', el);
            var last = $('[data-pr="last"]', el);
            if (first) first.disabled = this.mainIndex === 0;
            if (prev) prev.disabled = this.mainIndex === 0;
            if (next) next.disabled = this.mainIndex >= total - 1;
            if (last) last.textContent = this.mainIndex >= total - 1 ? '重新开始' : '尾页';
            var grid = $('[data-pr="grid"]', el);
            if (grid) grid.setAttribute('aria-pressed', String(this.overviewOn));
            $all('[data-pr="tool"]', el).forEach(function (b) {
                b.classList.toggle('is-on', b.dataset.tool === this.tool);
            }, this);
        },

        tick: function () {
            if (!this.el || !this.active) return;
            var el = this.el;
            var clock = $('[data-pr="clock"]', el);
            var pageClock = $('[data-pr="page-clock"]', el);
            var pageMs = this.pageElapsedMs();

            clock.textContent = this.dur(this.elapsed());
            pageClock.textContent = this.dur(pageMs);
            clock.classList.toggle('is-running', this.timer.running);
            pageClock.classList.toggle('is-running', this.timer.running);
            pageClock.classList.toggle('is-overtime', !!(this.pagePlannedMs && pageMs > this.pagePlannedMs));

            var noteTime = $('[data-pr="note-time"]', el);
            if (noteTime) noteTime.textContent = '本页已讲 ' + this.dur(pageMs);

            // 预算格：没设 minutes 显示横杠，不猜
            var budget = $('[data-pr="budget"]', el);
            var budgetLabel = $('[data-pr="budget-label"]', el);
            var budgetHint = $('[data-pr="budget-hint"]', el);
            var rest = this.remainingPlanMs();
            if (rest == null) {
                if (budgetLabel) budgetLabel.textContent = '计划';
                budget.textContent = '—';
                budget.classList.remove('is-overtime');
                if (budgetHint) budgetHint.textContent = '未设时长';
            } else {
                if (budgetLabel) budgetLabel.textContent = rest < 0 ? '超时' : '剩余';
                budget.textContent = this.dur(Math.abs(rest));
                budget.classList.toggle('is-overtime', rest < 0);
                if (budgetHint) budgetHint.textContent = '';
            }
            this.updatePlanHint();

            // 激光笔自动淡出
            if (this.laser && Date.now() - this.laser.at > 2200) {
                this.laser = null;
                this.drawInk();
                this.sendInk();
            }
        },

        // --- 排练：记录每页真实用时，结束后给对比表 ---
        toggleRehearsal: function () {
            if (this.rehearsalOn) { this.finishRehearsal(true); return; }
            this.rehearsalOn = true;
            this.pageTimes = [];
            this.resetTimer();
            this.startTimer();
            this.updateTransport();
        },

        finishRehearsal: function (showSummary) {
            if (!this.rehearsalOn) return;
            // 收尾这一页也要入账：recordPageTime 只在上一次翻页时被调用，
            // 不补最后这一页，摘要里就少了讲者真正停最久的那一页。
            this.recordPageTime(this.mainIndex);
            this.commitPageTime();
            var total = this.elapsed();
            var result = {
                at: Date.now(),
                totalMs: total,
                pages: this.pageTimes.slice()
            };
            this.rehearsalOn = false;
            this.pauseTimer();
            this.saveRehearsal(result);
            this.updateTransport();
            if (showSummary) this.openRehearsalSummary(result);
        },

        rehearsalHistory: function () {
            try {
                var raw = localStorage.getItem(PDF_KEY + ':rehearsals');
                var arr = raw ? JSON.parse(raw) : [];
                return Array.isArray(arr) ? arr : [];
            } catch (e) {
                return [];
            }
        },

        saveRehearsal: function (result) {
            try {
                var hist = this.rehearsalHistory();
                hist.unshift(result);
                localStorage.setItem(PDF_KEY + ':rehearsals', JSON.stringify(hist.slice(0, 5)));
            } catch (e) {}
        },

        recordPageTime: function (index) {
            var ms = this.pageElapsedMs();
            var existing = null;
            for (var i = 0; i < this.pageTimes.length; i++) {
                if (this.pageTimes[i].index === index) existing = this.pageTimes[i];
            }
            if (existing) existing.ms += ms;
            else this.pageTimes.push({ index: index, ms: ms });
        },

        openRehearsalSummary: function (result) {
            var self = this;
            var rows = result.pages.slice().sort(function (a, b) { return a.index - b.index; }).map(function (p) {
                var note = self.notes[p.index] || {};
                var planned = Number(note.minutes) > 0 ? Number(note.minutes) * 60000 : null;
                var title = note.title || SlideEngine.titleAt(p.index) || ('第 ' + (p.index + 1) + ' 页');
                return '<tr><td>' + (p.index + 1) + '</td><td>' + esc(title) + '</td><td>' +
                    self.dur(p.ms) + '</td><td>' +
                    (planned == null ? '—' : self.signed(p.ms - planned)) + '</td></tr>';
            }).join('');
            var hist = this.rehearsalHistory().slice(1).map(function (h) {
                return '<div class="pr-dialog-row"><span>' + new Date(h.at).toLocaleString('zh-CN') +
                    '</span><strong>' + self.dur(h.totalMs) + '</strong></div>';
            }).join('');
            this.openDialog('排练记录',
                '<div class="pr-dialog-section"><div class="pr-dialog-row"><span>本次总时长</span><strong>' +
                this.dur(result.totalMs) + '</strong></div>' +
                '<table class="pr-summary"><thead><tr><th>#</th><th>页面</th><th>实际</th><th>与计划相比</th></tr></thead>' +
                '<tbody>' + (rows || '<tr><td colspan="4">没有记录到页面用时</td></tr>') + '</tbody></table></div>' +
                (hist ? '<div class="pr-dialog-section"><h4>最近几次排练</h4>' + hist + '</div>' : '') +
                '<p class="pr-muted">只做数据汇总，不评价讲得好不好。</p>');
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
        last: function () {
            var total = SlideEngine.slides.length;
            SlideEngine.goTo(this.mainIndex >= total - 1 ? 0 : total - 1);
        },

        onSlideChange: function (detail) {
            if (!this.active) return;
            if (this.rehearsalOn) this.recordPageTime(this.mainIndex);
            this.mainIndex = detail.index;
            this.commitPageTime();
            this.timer.pageBase = 0;
            this.circles = [];
            this.laser = null;
            this.render();
            this.sendInk();
        },

        // --- 宫格选页：问答时"回到第 2 页那张表" ---
        toggleOverview: function (force) {
            this.overviewOn = typeof force === 'boolean' ? force : !this.overviewOn;
            var el = this.el;
            var stage = $('.pr-stage', el);
            var box = $('[data-pr="overview"]', el);
            if (stage) stage.classList.toggle('is-overview', this.overviewOn);
            if (box) box.hidden = !this.overviewOn;
            // 备注保持可见：讲者点选页面时往往正需要看着备注决定跳哪一页
            if (this.overviewOn) this.buildOverview();
            else this.fitAll();
            this.updateTransport();
        },

        buildOverview: function () {
            var grid = $('[data-pr="overview-grid"]', this.el);
            if (!grid) return;
            var self = this;
            var total = SlideEngine.slides.length;
            grid.innerHTML = SlideEngine.slides.map(function (slide, i) {
                var note = self.noteFor(slide);
                var title = note.title || SlideEngine.titleAt(i) || slide.dataset.slideId;
                var planned = Number(note.minutes) > 0 ? self.dur(Number(note.minutes) * 60000) : '—';
                return '<button type="button" class="pr-ov-page' + (i === self.mainIndex ? ' is-current' : '') +
                    '" data-ov="' + i + '">' +
                    '<span class="pr-ov-no">' + (i + 1) + ' / ' + total + '</span>' +
                    '<span class="pr-ov-title">' + esc(title) + '</span>' +
                    '<span class="pr-ov-meta"><span>' + esc(note.section || '未分组') + '</span>' +
                    '<span>' + planned + '</span></span></button>';
            }).join('');
            $all('[data-ov]', grid).forEach(function (btn) {
                btn.addEventListener('click', function () {
                    var target = Number(btn.dataset.ov);
                    self.toggleOverview(false);
                    SlideEngine.goTo(target);
                });
            });
            var cur = $('.pr-ov-page.is-current', grid);
            if (cur && cur.scrollIntoView) cur.scrollIntoView({ block: 'nearest' });
        },

        // --- 激光笔 / 圈选 ---
        setTool: function (tool) {
            this.tool = this.tool === tool ? 'none' : tool;
            if (this.tool !== 'laser') this.laser = null;
            var canvas = $('[data-pr="ink"]', this.el);
            if (canvas) {
                canvas.dataset.tool = this.tool;
                canvas.style.pointerEvents = this.tool === 'none' ? 'none' : 'auto';
            }
            this.updateTransport();
            this.drawInk();
            this.sendInk();
        },

        clearInk: function () {
            this.circles = [];
            this.laser = null;
            this.drawInk();
            this.sendInk();
        },

        stopLaser: function () {
            this.tool = 'none';
            this.laser = null;
            this.circles = [];
            this.drawInk();
        },

        // 坐标归一化后传给观众屏：两端窗口尺寸不同也不会错位
        sendInk: function () {
            this.broadcast({
                type: 'ink',
                index: this.mainIndex,
                laser: this.laser ? this.laser.point : null,
                circles: this.circles
            });
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

        drawInk: function () {
            var canvas = $('[data-pr="ink"]', this.el);
            if (!canvas) return;
            drawInkLayer(canvas, this.circles, this.laser ? this.laser.point : null);
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
                if (d.type !== 'ack') return;
                self.sync.lastAckAt = Date.now();
                self.sync.ackIndex = Number(d.index);
                self.updateSync();
            });

            // 跨窗口 / 同源备用通道
            try {
                this.channel = new BroadcastChannel(SYNC_KEY);
                this.channel.onmessage = function (e) {
                    var d = e.data;
                    if (!d || !d.__deckSync || d.type !== 'ack') return;
                    self.sync.lastAckAt = Date.now();
                    self.sync.ackIndex = Number(d.index);
                    self.updateSync();
                };
            } catch (e) {}

            // 键盘：演讲者视图主通道
            doc.addEventListener('keydown', function (e) {
                if (!self.active) return;
                var tag = (e.target && e.target.tagName) || '';
                if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return;

                if (self.dialogOpen) {
                    if (e.key === 'Escape') { e.preventDefault(); self.closeDialog(); }
                    return;
                }
                if (e.key === '?') { e.preventDefault(); self.openShortcuts(); return; }
                if (e.key === 'Escape') {
                    e.preventDefault();
                    if (self.tool !== 'none') self.setTool(self.tool);
                    else if (self.overviewOn) self.toggleOverview(false);
                    else self.exit();
                    return;
                }
                if (self.overviewOn) {
                    // 宫格里方向键仍可翻页，翻页后网格跟着重建
                    if (e.key === 'ArrowRight' || e.key === 'PageDown') { e.preventDefault(); self.next(); }
                    else if (e.key === 'ArrowLeft' || e.key === 'PageUp') { e.preventDefault(); self.prev(); }
                    return;
                }

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
                    case 'g': case 'G':
                        e.preventDefault(); self.toggleOverview(); break;
                    case 'l': case 'L':
                        e.preventDefault(); self.setTool('laser'); break;
                    case 'c': case 'C':
                        e.preventDefault(); self.setTool('circle'); break;
                    case 'x': case 'X':
                        e.preventDefault(); self.clearInk(); break;
                    case 'b': case 'B':
                        self.setScreen('black'); break;
                    case 'w': case 'W':
                        self.setScreen('white'); break;
                    case 'f': case 'F':
                        self.setScreen('frozen'); break;
                    case 'r': case 'R':
                        self.toggleRehearsal(); break;
                    case 't': case 'T':
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
                        self.sendInk();
                    } else if (self.tool === 'circle' && down) {
                        var p = self.pointerAt(e);
                        down.draft = { x1: down.start.x, y1: down.start.y, x2: p.x, y2: p.y };
                        self.circles = self.circles.slice(0, down.saved);
                        self.circles.push(down.draft);
                        self.drawInk();
                        self.sendInk();
                    }
                });
                canvas.addEventListener('pointerdown', function (e) {
                    if (self.tool !== 'circle') return;
                    canvas.setPointerCapture && canvas.setPointerCapture(e.pointerId);
                    down = { start: self.pointerAt(e), saved: self.circles.length };
                });
                canvas.addEventListener('pointerup', function () { down = null; });
                canvas.addEventListener('pointerleave', function () { down = null; });
            }

            this.tickTimer = setInterval(function () { self.tick(); }, 1000);
            this.heartbeat = setInterval(function () { self.updateSync(); }, 1000);
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
            if (mode === 'frozen' && !this.frozen) this.frozen = { index: this.mainIndex };
            this.broadcast({
                type: 'screen',
                mode: mode,
                index: this.mainIndex,
                frozenIndex: this.frozen ? this.frozen.index : this.mainIndex
            });
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
                this.sync.state = 'blocked';
                this.updateSync();
                return;
            }
            this.audience = popup;
            this.sync.openedAt = Date.now();
            this.sync.lastAckAt = 0;
            this.sync.ackIndex = -1;
            this.updateSync();
            if (reopen) this.broadcast({ type: 'goto', index: this.mainIndex });
            // 观众窗口刷新后回来要重新对齐
            var poll = setInterval(function () {
                if (!self.audience || self.audience.closed) {
                    clearInterval(poll);
                    self.audience = null;
                    self.updateSync();
                    return;
                }
                self.applyScreen();
            }, 2000);
        },

        updateSync: function () {
            var el = this.el;
            if (!el) return;
            var state;
            if (this.sync.state === 'blocked') state = 'blocked';
            else if (!this.audience || this.audience.closed) state = 'disconnected';
            else if (this.screenMode === 'black') state = 'black';
            else if (this.screenMode === 'white') state = 'white';
            else if (this.screenMode === 'frozen') state = 'frozen';
            else if (!this.sync.lastAckAt) {
                state = Date.now() - this.sync.openedAt < 2600 ? 'connecting' : 'disconnected';
            } else if (Date.now() - this.sync.lastAckAt > 4000) state = 'disconnected';
            else if (this.sync.ackIndex !== this.mainIndex) state = 'unsynced';
            else state = 'synced';

            var map = {
                connected: '观众屏 · 已同步',
                synced: '观众屏 · 已同步',
                stale: '观众屏 · 连接中',
                connecting: '观众屏 · 连接中',
                unsynced: '观众屏 · 未同步',
                black: '观众屏 · 黑屏',
                white: '观众屏 · 白屏',
                frozen: '观众屏 · 已冻结',
                blocked: '观众屏 · 弹窗被拦截',
                disconnected: '观众屏 · 未连接'
            };
            var node = $('[data-pr="sync"]', el);
            if (!node) return;
            node.dataset.state = map[state] ? state : 'connecting';
            node.textContent = map[state] || map.connecting;
        },

        broadcast: function (message) {
            var payload = Object.assign({ __deckSync: 1, session: SESSION, index: this.mainIndex }, message);
            try {
                if (this.audience && !this.audience.closed) this.audience.postMessage(payload, '*');
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

        // --- 演前检查：只看浏览器能确认的软件状态 ---
        openPreflight: function () {
            var self = this;
            var frame = $('[data-pr="cur"]', this.el);
            var rect = frame ? frame.getBoundingClientRect() : null;
            var images = $all('img');
            var loaded = images.filter(function (img) { return img.complete && img.naturalWidth > 0; });
            var checks = [
                {
                    label: '观众屏连接',
                    ok: this.audience && !this.audience.closed,
                    detail: $('[data-pr="sync"]', this.el).textContent
                },
                {
                    label: '弹窗权限',
                    ok: this.sync.state !== 'blocked',
                    detail: this.sync.state === 'blocked' ? '浏览器拦截了观众窗口，请允许弹窗后点「重新打开观众屏」' : '未检测到拦截'
                },
                {
                    label: '全屏',
                    ok: !!doc.fullscreenElement,
                    warn: true,
                    detail: doc.fullscreenElement ? '已全屏' : '未全屏，可在汇报前按 F 进入'
                },
                {
                    label: '字体',
                    ok: !doc.fonts || doc.fonts.status === 'loaded',
                    detail: doc.fonts ? ('状态：' + doc.fonts.status) : '浏览器不提供字体状态'
                },
                {
                    label: '图片资源',
                    ok: images.length === 0 || loaded.length === images.length,
                    detail: loaded.length + ' / ' + images.length + ' 已加载'
                },
                {
                    label: '当前页 16:9',
                    ok: !!(rect && rect.height && Math.abs(rect.width / rect.height - 16 / 9) < 0.01),
                    detail: rect ? (Math.round(rect.width) + ' × ' + Math.round(rect.height)) : '尚未渲染'
                },
                {
                    label: '备注覆盖',
                    ok: this.notes.length === SlideEngine.slides.length,
                    detail: this.notes.length + ' 条备注 / ' + SlideEngine.slides.length + ' 页'
                }
            ];
            var rows = checks.map(function (c) {
                var state = c.ok ? '正常' : (c.warn ? '建议' : '异常');
                var cls = c.ok ? 'is-ok' : (c.warn ? 'is-warn' : 'is-bad');
                return '<div class="pr-check ' + cls + '"><span class="pr-check-dot"></span>' +
                    '<span><strong>' + c.label + '</strong><br>' +
                    '<span class="pr-muted">' + esc(c.detail) + '</span></span>' +
                    '<strong>' + state + '</strong></div>';
            }).join('');
            this.openDialog('演前检查',
                '<div class="pr-dialog-section">' + rows + '</div>' +
                '<div class="pr-dialog-section"><button class="pr-btn" type="button" data-acts="recheck">重新检查</button> ' +
                '<button class="pr-btn" type="button" data-acts="fullscreen">进入全屏</button></div>' +
                '<p class="pr-muted">这里只能确认浏览器与观众页面的软件状态，无法确认 HDMI、转接器或投影线是否物理连接——现场仍要目视核对一次外接屏。</p>');
            $('[data-acts="recheck"]', this.el).addEventListener('click', function () { self.openPreflight(); });
            $('[data-acts="fullscreen"]', this.el).addEventListener('click', function () {
                if (doc.documentElement.requestFullscreen) {
                    doc.documentElement.requestFullscreen().then(function () { self.openPreflight(); })
                        .catch(function () {});
                }
            });
        },

        openSettings: function () {
            var self = this;
            this.openDialog('演示设置',
                '<div class="pr-dialog-section"><h4>演讲者布局</h4>' +
                '<div class="pr-seg">' +
                ['balanced|均衡', 'slides|页面优先', 'notes|备注优先'].map(function (pair) {
                    var v = pair.split('|');
                    return '<button class="pr-btn' + (self.layout === v[0] ? ' is-on' : '') +
                        '" type="button" data-layout="' + v[0] + '">' + v[1] + '</button>';
                }).join('') +
                '</div><p class="pr-muted">备注栏字太小或幻灯片看不清时切换比例。</p></div>' +
                '<div class="pr-dialog-section"><button class="pr-btn" type="button" data-acts="shortcuts">查看快捷键</button></div>');
            $all('[data-layout]', this.el).forEach(function (btn) {
                btn.addEventListener('click', function () {
                    self.setLayout(btn.dataset.layout);
                    self.openSettings();
                });
            });
            $('[data-acts="shortcuts"]', this.el).addEventListener('click', function () { self.openShortcuts(); });
        },

        setLayout: function (layout) {
            this.layout = ['balanced', 'slides', 'notes'].indexOf(layout) === -1 ? 'balanced' : layout;
            if (this.el) this.el.dataset.layout = this.layout;
            try { localStorage.setItem(PDF_KEY + ':layout', this.layout); } catch (e) {}
            var self = this;
            requestAnimationFrame(function () { self.fitAll(); });
        },

        openShortcuts: function () {
            var items = [
                ['→ / PageDown / Space', '下一页'],
                ['← / PageUp', '上一页'],
                ['Home / End', '首页 / 尾页'],
                ['G / Esc', '宫格选页；再按返回预览'],
                ['L / C / X', '激光笔 / 圈选 / 清除'],
                ['B / W / F', '观众屏黑屏 / 白屏 / 冻结'],
                ['T / R', '开始暂停计时 / 开始结束排练'],
                ['+ / -', '备注字号'],
                ['?', '这张快捷键表'],
                ['P', '退出演讲者视图']
            ];
            this.openDialog('快捷键',
                '<div class="pr-shortcuts">' + items.map(function (p) {
                    return '<kbd>' + p[0] + '</kbd><span>' + p[1] + '</span>';
                }).join('') + '</div>' +
                '<p class="pr-muted">编辑备注时方向键归光标，不会翻页。</p>');
        },

        openDialog: function (title, html) {
            var dlg = $('[data-pr="dialog"]', this.el);
            if (!dlg) return;
            $('[data-pr="dialog-title"]', this.el).textContent = title;
            $('[data-pr="dialog-body"]', this.el).innerHTML = html;
            dlg.hidden = false;
            this.dialogOpen = true;
        },

        closeDialog: function () {
            var dlg = $('[data-pr="dialog"]', this.el);
            if (dlg) dlg.hidden = true;
            this.dialogOpen = false;
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

    // 标注层绘制：演讲者预览与观众屏共用，坐标已归一化
    function drawInkLayer(canvas, circles, laserPoint) {
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

        (circles || []).forEach(function (c) {
            ctx.save();
            ctx.strokeStyle = '#ff4f59';
            ctx.lineWidth = Math.max(2, w * 0.003);
            ctx.beginPath();
            ctx.ellipse((c.x1 + c.x2) / 2 * w, (c.y1 + c.y2) / 2 * h,
                Math.abs(c.x2 - c.x1) / 2 * w, Math.abs(c.y2 - c.y1) / 2 * h, 0, 0, Math.PI * 2);
            ctx.stroke();
            ctx.restore();
        });
        if (laserPoint) {
            var x = laserPoint.x * w;
            var y = laserPoint.y * h;
            var r = Math.max(5, w * 0.006);
            var g = ctx.createRadialGradient(x, y, 0, x, y, r * 2.6);
            g.addColorStop(0, 'rgba(255,255,255,.98)');
            g.addColorStop(0.25, 'rgba(255,64,72,.95)');
            g.addColorStop(1, 'rgba(255,64,72,0)');
            ctx.fillStyle = g;
            ctx.beginPath();
            ctx.arc(x, y, r * 2.6, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    // ============================================================
    // 观众屏 / 预览：接收主窗口指令
    // ============================================================
    function initSlave() {
        var curtain = doc.createElement('div');
        curtain.className = 'audience-curtain';
        curtain.textContent = '演示结束';
        body.appendChild(curtain);

        // 观众屏也要能看见讲者的激光笔与圈选：坐标是归一化的，尺寸不同也不跑位
        var inkLayer = null;
        if (IS_AUDIENCE) {
            inkLayer = doc.createElement('canvas');
            inkLayer.className = 'audience-ink';
            inkLayer.setAttribute('aria-hidden', 'true');
            body.appendChild(inkLayer);
        }

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
            } else if (d.type === 'ink') {
                if (MODE === 'audience' && Number(d.index) === SlideEngine.index) {
                    drawInkLayer(inkLayer, d.circles || [], d.laser || null);
                }
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
            // 翻页时清掉上一页的标注，避免圈选残留在新页面上
            doc.addEventListener('deck:change', function () {
                if (inkLayer) drawInkLayer(inkLayer, [], null);
            });
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
