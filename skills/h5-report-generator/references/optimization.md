# 性能优化建议

本指南提供H5汇报材料的加载优化和性能提升技巧，确保在各种网络环境下都能快速展示。

## 加载优化

### 1. CDN配置优化

使用稳定的CDN资源，减少加载时间：

```html
<!-- 使用jsdelivr或unpkg等稳定CDN -->
<script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
```

### 2. 资源压缩

```html
<!-- 使用minified版本 -->
<script src="echarts.min.js"></script>
<link rel="stylesheet" href="styles.min.css">
```

### 3. 异步加载

```javascript
// 异步加载ECharts
function loadECharts() {
    return new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js';
        script.onload = resolve;
        script.onerror = reject;
        document.head.appendChild(script);
    });
}

// 异步加载Mermaid
function loadMermaid() {
    return new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js';
        script.onload = resolve;
        script.onerror = reject;
        document.head.appendChild(script);
    });
}

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', async function() {
    showLoading();
    try {
        await Promise.all([loadECharts(), loadMermaid()]);
        initPresentation();
    } catch (error) {
        console.error('加载失败:', error);
    } finally {
        hideLoading();
    }
});

function showLoading() {
    const loader = document.createElement('div');
    loader.id = 'page-loader';
    loader.innerHTML = '<div class="loader">加载中...</div>';
    loader.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(255,255,255,0.9);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        color: #0066cc;
        z-index: 9999;
    `;
    document.body.appendChild(loader);
}

function hideLoading() {
    const loader = document.getElementById('page-loader');
    if (loader) loader.remove();
}
```

### 4. 预加载关键资源

```html
<!-- 预加载下一张幻灯片可能需要的资源 -->
<link rel="preload" href="next-slide-content.html" as="document">
<link rel="dns-prefetch" href="cdn.jsdelivr.net">
```

## 图片优化

### 1. WebP格式

```html
<!-- 使用WebP格式，兼容回退 -->
<picture>
    <source srcset="image.webp" type="image/webp">
    <img src="image.jpg" alt="描述" style="max-width: 100%; height: auto;">
</picture>
```

### 2. 懒加载

```html
<!-- 图片懒加载 -->
<img data-src="image1.jpg" alt="图片1" class="lazy-load">
<img data-src="image2.jpg" alt="图片2" class="lazy-load">

<script>
// 懒加载实现
function lazyLoad() {
    const images = document.querySelectorAll('.lazy-load');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy-load');
                img.classList.add('loaded');
                observer.unobserve(img);
            }
        });
    });

    images.forEach(img => imageObserver.observe(img));
}
document.addEventListener('DOMContentLoaded', lazyLoad);
</script>
```

### 3. 图片压缩

使用合适的图片质量和尺寸：

```html
<!-- 响应式图片 -->
<img src="image-400.jpg"
     srcset="image-400.jpg 400w, image-800.jpg 800w, image-1200.jpg 1200w"
     sizes="(max-width: 768px) 400px, (max-width: 1024px) 800px, 1200px"
     alt="描述">
```

## CSS优化

### 1. CSS变量复用

```css
:root {
    /* 提前定义所有颜色变量 */
    --primary: #0066cc;
    --secondary: #4da6ff;
    --accent: #e63946;
    --light-bg: #f0f7ff;
    --card-bg: rgba(255, 255, 255, 0.95);
    --shadow: 0 10px 40px rgba(0, 102, 204, 0.1);
}
```

### 2. 关键CSS内联

```html
<style>
/* 关键CSS内联 */
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    margin: 0;
    padding: 0;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.slide { display: none; min-height: 100vh; padding: 40px 60px; }
.slide.active { display: block; }
</style>

<!-- 完整CSS在DOM加载后加载 -->
<link rel="preload" href="full-styles.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
<noscript><link rel="stylesheet" href="full-styles.css"></noscript>
```

### 3. 选择器优化

```css
/* 避免过度嵌套 */
.slide .column-card { /* OK */ }

/* 避免使用通用选择器 */
* { /* 不推荐 */ }

/* 优先使用class选择器 */
.column-card { /* 推荐 */ }
```

## JavaScript优化

### 1. 事件委托

```javascript
// 使用事件委托优化性能
document.addEventListener('click', function(e) {
    if (e.target.matches('.nav-btn')) {
        handleNavClick(e.target);
    }
});

// 替换多个独立监听器
// document.querySelectorAll('.nav-btn').forEach(btn => {
//     btn.addEventListener('click', handleNavClick);
// });
```

### 2. 防抖处理

```javascript
// 窗口大小改变防抖
let resizeTimer;
window.addEventListener('resize', function() {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function() {
        handleResize();
    }, 250);
});

// 滚动防抖
let scrollTimer;
window.addEventListener('scroll', function() {
    clearTimeout(scrollTimer);
    scrollTimer = setTimeout(function() {
        handleScroll();
    }, 100);
});
```

### 3. 虚拟滚动

```javascript
// 长列表优化
class VirtualList {
    constructor(container, itemHeight, renderItem) {
        this.container = container;
        this.itemHeight = itemHeight;
        this.renderItem = renderItem;
        this.visibleCount = Math.ceil(container.clientHeight / itemHeight) + 2;
        this.data = [];
        this.startIndex = 0;
        this.endIndex = this.visibleCount;
        this.update();
    }
    setData(data) {
        this.data = data;
        this.update();
    }
    update() {
        const start = this.startIndex;
        const end = Math.min(end, this.data.length);
        this.container.innerHTML = '';
        for (let i = start; i < end; i++) {
            const item = this.renderItem(this.data[i], i);
            this.container.appendChild(item);
        }
    }
}
```

## 动画优化

### 1. 使用transform替代position

```css
/* 推荐：使用transform */
.slide {
    transition: transform 0.3s ease;
}
.slide.active {
    transform: translateX(0);
}

/* 避免：修改left/top引起重绘 */
.animated {
    /* 不好 */
    left: 100px;
    /* 好 */
    transform: translateX(100px);
}
```

### 2. 硬件加速

```css
/* 触发硬件加速 */
.column-card {
    transform: translateZ(0);
    /* 或 */
    will-change: transform;
}

/* 动画优化 */
@media (prefers-reduced-motion: reduce) {
    .column-card {
        transition: none;
    }
}
```

### 3. 减少重绘重排

```javascript
// 批量DOM操作
const container = document.createDocumentFragment();
for (let i = 0; i < 100; i++) {
    const div = document.createElement('div');
    div.textContent = i;
    container.appendChild(div);
}
document.body.appendChild(container);

// 替换单独添加
// for (let i = 0; i < 100; i++) {
//     document.body.appendChild(div);  // 会导致100次重排
// }
```

## 网络优化

### 1. HTTP缓存

```html
<!-- 静态资源缓存 -->
<meta http-equiv="Cache-Control" content="max-age=31536000">

<!-- Service Worker缓存 -->
<script>
// 注册Service Worker
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('sw.js');
}
</script>
```

### 2. 预取预加载

```html
<!-- 预取下一页可能访问的资源 -->
<link rel="prefetch" href="data.json">
<link rel="prefetch" href="images/slide2.jpg">

<!-- 预加载关键资源 -->
<link rel="preload" href="critical.css" as="style">
```

### 3. 本地存储

```javascript
// 使用localStorage缓存数据
function cacheData(key, data) {
    localStorage.setItem(key, JSON.stringify({
        data: data,
        timestamp: Date.now()
    }));
}

function getCachedData(key, maxAge = 3600000) {
    const cached = localStorage.getItem(key);
    if (!cached) return null;
    const { data, timestamp } = JSON.parse(cached);
    if (Date.now() - timestamp > maxAge) {
        localStorage.removeItem(key);
        return null;
    }
    return data;
}
```

## 打包建议

### 1. 资源合并

```html
<!-- 合并JS文件 -->
<script src="bundle.min.js"></script>
<link rel="stylesheet" href="bundle.min.css">
```

### 2. Tree shaking

```javascript
// 只导入需要的函数
import { debounce } from 'lodash-es/debounce';

// 避免导入整个lodash
// import _ from 'lodash';  // 不推荐
```

### 3. 资源按需加载

```javascript
// 路由懒加载
function loadSlide(slideId) {
    return import(`./slides/${slideId}.js`)
        .then(module => module.init());
}
```

## 监控与调试

### 1. 性能指标

```javascript
// 加载性能监控
window.addEventListener('load', function() {
    const timing = performance.getEntriesByType('navigation')[0];
    console.log('加载时间:', timing.loadEventEnd - timing.loadEventStart);
    console.log('DOM解析时间:', timing.domContentLoadedEventEnd - timing.domContentLoadedEventStart);
});

// LCP指标
new PerformanceObserver((entryList) => {
    for (const entry of entryList.getEntries()) {
        console.log('LCP:', entry.startTime);
    }
}).observe({ entryTypes: ['largest-contentful-paint'] });
```

### 2. 内存监控

```javascript
// 监控内存使用
setInterval(() => {
    if (performance.memory) {
        console.log('内存使用:', performance.memory.usedJSHeapSize / 1024 / 1024, 'MB');
    }
}, 5000);
```

### 3. 错误监控

```javascript
// 全局错误捕获
window.addEventListener('error', function(e) {
    console.error('脚本错误:', e.error);
});

window.addEventListener('unhandledrejection', function(e) {
    console.error('未处理的Promise错误:', e.reason);
});
```

## 最佳实践清单

- ✅ 使用CDN加速资源加载
- ✅ 压缩和合并JS/CSS文件
- ✅ 图片使用WebP格式并压缩
- ✅ 实现图片懒加载
- ✅ 使用CSS transform进行动画
- ✅ 避免频繁DOM操作
- ✅ 使用事件委托减少监听器
- ✅ 实现防抖优化窗口事件
- ✅ 代码分割和按需加载
- ✅ 使用Browser缓存
- ✅ 实现预取预加载
- ✅ 监控加载性能和错误
- ✅ 针对移动设备进行优化
- ✅ 使用localStorage缓存数据
- ✅ 减少重绘重排操作
- ✅ 实现虚拟滚动（长列表）
- ✅ 优先使用系统字体
- ❌ 避免阻塞式脚本加载
- ❌ 避免使用过深的选择器
- ❌ 避免频繁的颜色/布局变化
- ❌ 避免加载过大图片
- ❌ 避免在动画中修改布局属性