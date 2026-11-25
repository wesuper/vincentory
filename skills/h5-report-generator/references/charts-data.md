# 图表数据定制指南

本指南介绍如何在H5汇报材料中集成ECharts和Mermaid图表，创建数据可视化展示。

## ECharts集成

### 基础柱状图

```html
<div id="chart-bar" style="height: 400px;"></div>

<script>
// 柱状图示例：投入成本对比
var chartBar = echarts.init(document.getElementById('chart-bar'));
var optionBar = {
    title: {
        text: '投入成本对比',
        left: 'center',
        textStyle: {
            fontSize: 20,
            color: '#0066cc',
            fontWeight: 700
        }
    },
    tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' }
    },
    legend: {
        data: ['原始投入', '优化后投入'],
        top: 40
    },
    grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
    },
    xAxis: {
        type: 'category',
        data: ['开发成本', '运维成本', '人力成本', '总投入']
    },
    yAxis: {
        type: 'value',
        name: '金额 (万元)'
    },
    series: [
        {
            name: '原始投入',
            type: 'bar',
            data: [120, 80, 60, 260],
            itemStyle: {
                color: '#4da6ff'
            }
        },
        {
            name: '优化后投入',
            type: 'bar',
            data: [100, 50, 40, 190],
            itemStyle: {
                color: '#0066cc'
            }
        }
    ]
};
chartBar.setOption(optionBar);
</script>
```

### 折线图

```html
<div id="chart-line" style="height: 400px;"></div>

<script>
// 折线图示例：每月业务量趋势
var chartLine = echarts.init(document.getElementById('chart-line'));
var optionLine = {
    title: {
        text: '月度业务量趋势',
        left: 'center'
    },
    tooltip: {
        trigger: 'axis'
    },
    legend: {
        data: ['人工质检', '智能质检'],
        top: 40
    },
    grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
    },
    xAxis: {
        type: 'category',
        boundaryGap: false,
        data: ['1月', '2月', '3月', '4月', '5月', '6月', '7月']
    },
    yAxis: {
        type: 'value',
        name: '业务量 (万笔)'
    },
    series: [
        {
            name: '人工质检',
            type: 'line',
            data: [120, 132, 141, 154, 190, 230, 280],
            smooth: true,
            itemStyle: { color: '#e63946' },
            areaStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    { offset: 0, color: 'rgba(230, 57, 70, 0.3)' },
                    { offset: 1, color: 'rgba(230, 57, 70, 0)' }
                ])
            }
        },
        {
            name: '智能质检',
            type: 'line',
            data: [220, 282, 391, 534, 690, 750, 820],
            smooth: true,
            itemStyle: { color: '#0066cc' },
            areaStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    { offset: 0, color: 'rgba(0, 102, 204, 0.3)' },
                    { offset: 1, color: 'rgba(0, 102, 204, 0)' }
                ])
            }
        }
    ]
};
chartLine.setOption(optionLine);
</script>
```

### 饼图

```html
<div id="chart-pie" style="height: 400px;"></div>

<script>
// 饼图示例：人员投入分布
var chartPie = echarts.init(document.getElementById('chart-pie'));
var optionPie = {
    title: {
        text: '人员投入分布',
        left: 'center',
        top: 20
    },
    tooltip: {
        trigger: 'item',
        formatter: '{b}: {c}人 ({d}%)'
    },
    legend: {
        orient: 'vertical',
        left: 'left',
        top: 'middle'
    },
    series: [
        {
            type: 'pie',
            radius: ['40%', '70%'],
            center: ['60%', '50%'],
            avoidLabelOverlap: false,
            itemStyle: {
                borderRadius: 10,
                borderColor: '#fff',
                borderWidth: 2
            },
            label: {
                show: true,
                fontSize: 14,
                fontWeight: 600
            },
            emphasis: {
                label: {
                    show: true,
                    fontSize: 16,
                    fontWeight: 'bold'
                }
            },
            data: [
                { value: 15, name: 'ASR&TTS开发', itemStyle: { color: '#0066cc' } },
                { value: 8, name: '智能质检开发', itemStyle: { color: '#4da6ff' } },
                { value: 12, name: '测试验证', itemStyle: { color: '#f4a261' } },
                { value: 10, name: '运维支持', itemStyle: { color: '#e63946' } }
            ]
        }
    ]
};
chartPie.setOption(optionPie);
</script>
```

### 混合图

```html
<div id="chart-mix" style="height: 450px;"></div>

<script>
// 混合图示例：指标完成度
var chartMix = echarts.init(document.getElementById('chart-mix'));
var optionMix = {
    title: {
        text: '关键指标完成情况',
        left: 'center'
    },
    tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'cross' }
    },
    legend: {
        data: ['ASR准确率', 'TTS质量', '质检覆盖率'],
        top: 40
    },
    grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
    },
    xAxis: {
        type: 'category',
        data: ['Q1', 'Q2', 'Q3', 'Q4']
    },
    yAxis: {
        type: 'value',
        name: '完成率 (%)',
        max: 100
    },
    series: [
        {
            name: 'ASR准确率',
            type: 'bar',
            data: [85, 88, 92, 95],
            itemStyle: { color: '#0066cc' }
        },
        {
            name: 'TTS质量',
            type: 'bar',
            data: [80, 85, 90, 93],
            itemStyle: { color: '#4da6ff' }
        },
        {
            name: '质检覆盖率',
            type: 'line',
            data: [60, 70, 85, 95],
            smooth: true,
            yAxisIndex: 0,
            itemStyle: { color: '#e63946' }
        }
    ]
};
chartMix.setOption(optionMix);
</script>
```

## Mermaid流程图

### 基础流程图

```html
<div class="mermaid">
graph LR
    A[收到客户需求] --> B{需求分析}
    B -->|可行| C[制定方案]
    B -->|不可行| D[拒绝需求]
    C --> E[技术评估]
    E --> F[风险评估]
    F --> G[高层审批]
    G -->|通过| H[执行项目]
    G -->|拒绝| I[终止项目]
    H --> J[完成交付]
</div>
```

### ASR流程图

```html
<div class="mermaid">
graph TD
    A[语音输入] --> B[预处理]
    B --> C[声学模型]
    C --> D[语言模型]
    D --> E[解码输出]
    E --> F[后处理]
    F --> G[文本结果]

    style A fill:#e8f4fc
    style G fill:#d4edda
    style C fill:#fff3cd
    style D fill:#fff3cd
```

### 质检流程图

```html
<div class="mermaid">
flowchart TD
    A[通话录音] --> B[ASR转文本]
    B --> C[质检规则引擎]
    C --> D{规则匹配}
    D -->|违规| E[标记违规]
    D -->|合规| F[质检通过]
    E --> G[生成质检报告]
    F --> H[更新质检状态]
    G --> I[通知相关人员]
    H --> J[归档记录]
    I --> K[人工复核]
    K --> L{复核结果}
    L -->|确认| L1[处理违规]
    L -->|撤销| H

    style C fill:#e8f4fc
    style E fill:#f4a261
    style F fill:#d4edda
```

## 动态数据加载

### 从JSON文件加载数据

```javascript
// data.json
{
    "categories": ["原始", "优化"],
    "values": [260, 190]
}

// 在HTML中加载
fetch('data.json')
    .then(response => response.json())
    .then(data => {
        var chart = echarts.init(document.getElementById('chart'));
        var option = {
            xAxis: { type: 'category', data: data.categories },
            series: [{ type: 'bar', data: data.values }]
        };
        chart.setOption(option);
    });
```

### 数据更新示例

```javascript
// 动态更新图表数据
function updateChart(data) {
    chart.setOption({
        series: [{
            data: data
        }]
    });
}

// 定时更新（每5秒）
setInterval(() => {
    updateChart([Math.random() * 100]);
}, 5000);
```

## 响应式图表

```javascript
// 窗口大小改变时自动调整
window.addEventListener('resize', function() {
    chart.resize();
});

// 页面显示/隐藏时的处理
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        chart.resize();
    }
});
```

## 统一初始化脚本

在HTML底部添加统一的初始化脚本：

```html
<script>
document.addEventListener('DOMContentLoaded', function() {
    // 初始化所有图表
    const charts = {
        'chart-bar': 'bar',
        'chart-line': 'line',
        'chart-pie': 'pie',
        'chart-mix': 'mix'
    };

    // 响应式处理
    window.addEventListener('resize', function() {
        Object.keys(charts).forEach(id => {
            const chart = echarts.getInstanceByDom(document.getElementById(id));
            if (chart) chart.resize();
        });
    });
});
</script>
```

## 最佳实践

1. **性能优化**：
   - 图表容器指定明确高度
   - 数据量大时使用`animation: false`
   - 复用图表实例，如需更新数据

2. **用户体验**：
   - 添加loading状态
   - 提供tooltip提示
   - 数据为空时显示友好提示

3. **主题一致性**：
   - 使用统一的配色方案
   - 保持字体大小一致
   - 遵循企业VI规范

4. **调试建议**：
   - 打开浏览器开发者工具
   - 检查console是否有错误
   - 使用echarts官网的工具辅助调试