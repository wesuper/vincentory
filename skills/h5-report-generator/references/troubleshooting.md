# 故障排查手册

本手册汇总了H5汇报材料制作过程中的常见问题和解决方案。

> **v5 变更提示**：页面顺序改为按 DOM 顺序自动发现，**不再维护 `slideOrder` 数组**。下文涉及 `slideOrder` 的内容仅用于排查旧版（v4）产物。

## 导航问题

### Q1: 页面无法导航，点击按钮无响应

**症状**：
- 点击左右箭头按钮没有反应
- 键盘左右键不能切换页面

**排查步骤**：
1. **检查JavaScript错误**：
   ```javascript
   // 打开浏览器控制台（F12）
   // 查看是否有红颜色的错误信息
   ```

2. **验证slideOrder数组**：
   ```javascript
   const slideOrder = [
       'slide-cover',      // 确保ID存在
       'slide-toc1',
       'slide1'
   ];
   // 检查HTML中对应的div id是否一致
   ```

3. **确认DOM元素存在**：
   ```javascript
   // 在控制台中执行
   console.log(document.getElementById('slide-cover')); // 应返回元素
   console.log(document.getElementById('slide-toc1'));  // 应返回元素
   ```

**解决方案**：
```javascript
// 确保函数存在且正确绑定
function changeSlide(direction) {
    console.log('切换页面:', direction); // 调试日志
    currentSlide += direction;
    showSlide(currentSlide);
}

// 检查按钮事件绑定
document.getElementById('prevBtn').onclick = function() {
    changeSlide(-1);
};
document.getElementById('nextBtn').onclick = function() {
    changeSlide(1);
};
```

### Q2: 页面数量显示错误

**症状**：显示 "1 / 0" 或总页数不正确

**原因**：slideOrder数组为空或未定义

**解决方案**：
```javascript
// 确保slideOrder正确初始化
const slideOrder = [
    'slide-cover',
    'slide-toc1',
    'slide1',
    // ... 至少包含1个元素
];

// 在showSlide函数中添加验证
function showSlide(n) {
    if (!slideOrder || slideOrder.length === 0) {
        console.error('slideOrder未初始化');
        return;
    }
    // ... 其他逻辑
}
```

## 样式问题

### Q3: 文字显示不清楚，太小

**症状**：文字太小，难以阅读

**解决方案**：
```css
/* 在模板中添加响应式字体 */
.column-features li {
    font-size: 14px;  /* 确保不低于14px */
}

/* 添加响应式调整 */
@media (max-width: 768px) {
    .column-features li {
        font-size: 16px;  /* 移动端适当放大 */
    }
}
```

### Q4: 颜色显示不一致

**症状**：在不同设备上颜色差异明显

**解决方案**：
```css
/* 使用CSS变量确保一致性 */
:root {
    --primary-blue: #0066cc;
}

/* 使用具体数值而非变量作为回退 */
.column-header h3 {
    color: var(--primary-blue, #0066cc);  /* 变量+回退 */
}
```

### Q5: 移动端显示错乱

**症状**：在手机上布局乱掉

**解决方案**：
```html
<!-- 确保viewport设置正确 -->
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<style>
/* 添加响应式断点 */
.three-columns {
    grid-template-columns: repeat(3, 1fr);  /* 桌面 */
}

@media (max-width: 1024px) {
    .three-columns {
        grid-template-columns: repeat(2, 1fr);  /* 平板 */
    }
}

@media (max-width: 768px) {
    .three-columns {
        grid-template-columns: 1fr;  /* 手机 */
    }
}
</style>
```

## 图表问题

### Q6: ECharts图表不显示

**症状**：图表区域空白

**排查步骤**：
1. **检查容器尺寸**：
   ```javascript
   <div id="chart" style="height: 400px;"></div>
   // 必须设置高度
   ```

2. **检查数据格式**：
   ```javascript
   // 控制台输出数据验证
   console.log(option);
   // 确保数据格式正确
   ```

3. **检查初始化时机**：
   ```javascript
   // 确保在DOM加载后初始化
   document.addEventListener('DOMContentLoaded', function() {
       var chartDom = document.getElementById('chart');
       var myChart = echarts.init(chartDom);
       myChart.setOption(option);
   });
   ```

**解决方案**：
```html
<!-- 完整示例 -->
<div id="chart-bar" style="height: 400px; width: 100%;"></div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    var chartDom = document.getElementById('chart-bar');
    if (!chartDom) {
        console.error('图表容器不存在');
        return;
    }
    var myChart = echarts.init(chartDom);

    var option = {
        title: { text: '示例图表' },
        xAxis: { type: 'category', data: ['A', 'B', 'C'] },
        yAxis: { type: 'value' },
        series: [{ type: 'bar', data: [10, 20, 30] }]
    };

    myChart.setOption(option);

    // 响应式处理
    window.addEventListener('resize', function() {
        myChart.resize();
    });
});
</script>
```

### Q7: Mermaid流程图不渲染

**症状**：显示原始代码而不是流程图

**解决方案**：
```javascript
// 1. 确保Mermaid正确初始化
mermaid.initialize({
    startOnLoad: false,  // 必须设置
    theme: 'default'
});

// 2. 手动渲染
document.addEventListener('DOMContentLoaded', async function() {
    await mermaid.run();
});

// 3. 检查语法
<div class="mermaid">
graph LR
    A[节点A] --> B[节点B]  <!-- 语法错误：缺少空格 -->
</div>

<!-- 正确语法 -->
<div class="mermaid">
graph LR
    A[节点A] --> B[节点B]
</div>
```

### Q8: 动态加载的图表尺寸错误

**症状**：图表显示不全或尺寸不合适

**解决方案**：
```javascript
// 延迟初始化，确保容器已渲染
setTimeout(function() {
    var chart = echarts.init(document.getElementById('chart'));
    chart.setOption(option);
    chart.resize();
}, 100);
```

## 内容问题

### Q9: 特殊字符显示乱码

**症状**：中文或特殊符号变成问号

**解决方案**：
```html
<!-- 确保字符编码正确 -->
<meta charset="UTF-8">

<!-- HTML实体编码 -->
<p>成本：&yen;100万</p>
<p>税率：10&percnt;</p>
<p>大于号：&gt; 小于号：&lt;</p>
```

### Q10: 图片无法显示

**症状**：图片显示为破图图标

**解决方案**：
```html
<!-- 检查路径 -->
<img src="images/logo.png" alt="Logo">

<!-- 添加错误处理 -->
<img src="images/logo.png"
     alt="Logo"
     onerror="this.src='images/default.png';">

<!-- 懒加载 -->
<img data-src="images/logo.png" class="lazy-load">
<script>
document.addEventListener('DOMContentLoaded', function() {
    const img = document.querySelector('img[data-src]');
    if (img.complete) {
        img.src = img.dataset.src;
    } else {
        img.onload = function() {
            this.src = this.dataset.src;
        };
    }
});
</script>
```

## 性能问题

### Q11: 页面加载很慢

**症状**：打开页面等待很久

**解决方案**：
```html
<!-- 1. 优化图片 -->
<!-- 使用压缩后的WebP格式 -->

<!-- 2. 减少外部依赖 -->
<!-- 减少不必要的CDN资源 -->

<!-- 3. 异步加载非关键资源 -->
<script>
// 延迟加载非关键JavaScript
setTimeout(function() {
    const script = document.createElement('script');
    script.src = 'optional-script.js';
    document.head.appendChild(script);
}, 1000);
</script>

<!-- 4. 添加loading状态 -->
<div id="loader">加载中...</div>
<script>
function hideLoader() {
    document.getElementById('loader').style.display = 'none';
}
document.addEventListener('DOMContentLoaded', hideLoader);
</script>
```

### Q12: 动画卡顿

**症状**：切换页面时有卡顿

**解决方案**：
```css
/* 启用硬件加速 */
.slide {
    transform: translateZ(0);
    will-change: transform;
}

/* 简化动画 */
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }  /* 移除transform */
}

/* 减少阴影计算 */
@media (max-width: 768px) {
    .column-card {
        box-shadow: none;  /* 移动端禁用阴影 */
    }
}
```

## 兼容性问题

### Q13: 在某些浏览器不兼容

**症状**：在旧版Safari/Chrome上显示异常

**解决方案**：
```html
<!-- 添加浏览器兼容性检测 -->
<script>
// 检测ES6支持
if (!String.prototype.includes) {
    console.warn('浏览器不支持ES6');
    // 降级方案
}

<!-- CSS Grid降级 -->
.three-columns {
    display: flex;  /* Grid不支持时使用flex */
    flex-wrap: wrap;
}

@supports (display: grid) {
    .three-columns {
        display: grid;  /* 支持时使用grid */
    }
}
</script>
```

### Q14: 触摸设备操作异常

**症状**：在平板上滑动无响应

**解决方案**：
```javascript
// 添加触摸事件
let startX = 0;
let endX = 0;

document.addEventListener('touchstart', function(e) {
    startX = e.touches[0].clientX;
});

document.addEventListener('touchend', function(e) {
    endX = e.changedTouches[0].clientX;
    handleSwipe();
});

function handleSwipe() {
    const threshold = 50;
    const diff = startX - endX;
    if (Math.abs(diff) > threshold) {
        if (diff > 0) {
            changeSlide(1);  // 向左滑动，下一页
        } else {
            changeSlide(-1); // 向右滑动，上一页
        }
    }
}
```

## 调试技巧

### 1. 浏览器控制台调试

```javascript
// 常用调试命令
console.log('当前页面:', currentSlide);
console.log('页面总数:', totalSlides);
console.log('slideOrder:', slideOrder);

// 检查元素
console.dir(document.getElementById('slide1'));

// 测试函数
window.testSlide = function() {
    showSlide(1);
};

// 性能测试
console.time('slideChange');
changeSlide(1);
console.timeEnd('slideChange');
```

### 2. CSS调试

```css
/* 临时添加调试边框 */
.slide {
    border: 1px solid red !important;
}

/* 网格调试 */
.three-columns {
    outline: 1px dashed blue;
}
```

### 3. 截图对比

```javascript
// 自动截图函数
function screenshot() {
    html2canvas(document.body).then(canvas => {
        const link = document.createElement('a');
        link.download = 'screenshot.png';
        link.href = canvas.toDataURL();
        link.click();
    });
}
```

## 快速修复脚本

```javascript
// 诊断脚本 - 添加到HTML底部
(function() {
    const checks = [];

    // 检查DOM元素
    function checkElement(id) {
        const el = document.getElementById(id);
        if (!el) {
            console.error(`元素 #${id} 不存在`);
            return false;
        }
        return true;
    }

    // 执行所有检查
    function runDiagnostics() {
        console.log('=== 开始诊断 ===');

        // 检查导航元素
        ['prevBtn', 'nextBtn', 'currentPage'].forEach(id => {
            if (!checkElement(id)) {
                checks.push(`❌ 导航元素 #${id} 缺失`);
            } else {
                checks.push(`✅ 导航元素 #${id} 正常`);
            }
        });

        // 检查slide元素
        const expectedSlides = ['slide-cover', 'slide-toc1', 'slide1'];
        expectedSlides.forEach(id => {
            if (!checkElement(id)) {
                checks.push(`❌ 幻灯片元素 #${id} 缺失`);
            } else {
                checks.push(`✅ 幻灯片元素 #${id} 正常`);
            }
        });

        // 检查JavaScript
        if (typeof changeSlide !== 'function') {
            checks.push('❌ changeSlide 函数未定义');
        } else {
            checks.push('✅ changeSlide 函数正常');
        }

        // 输出结果
        checks.forEach(check => console.log(check));
        console.log('=== 诊断完成 ===');
    }

    // 页面加载完成后运行
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', runDiagnostics);
    } else {
        runDiagnostics();
    }
})();
```

## 联系支持

如果以上方案都无法解决问题，请检查：

1. **浏览器版本**：确保使用现代浏览器（Chrome 80+, Safari 13+, Firefox 75+）
2. **控制台错误**：查看F12开发者工具中的Console面板
3. **网络问题**：检查CDN资源是否正常加载
4. **代码版本**：确保HTML文件完整，未被意外修改

更多信息可参考：
- [MDN Web Docs](https://developer.mozilla.org/)
- [ECharts官方文档](https://echarts.apache.org/)
- [Mermaid官方文档](https://mermaid.js.org/)