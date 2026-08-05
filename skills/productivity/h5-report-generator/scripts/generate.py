#!/usr/bin/env python3
"""
H5汇报材料生成器脚本
根据配置自动生成HTML幻灯片演示文稿
"""

import os
import sys
import json
import argparse
from pathlib import Path
from string import Template


class H5ReportGenerator:
    """H5汇报材料生成器"""

    def __init__(self, template_path, output_dir):
        self.template_path = Path(template_path)
        self.output_dir = Path(output_dir)

        # 确保输出目录存在
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 默认配置
        self.config = {
            'title': '汇报材料',
            'subtitle': '专业汇报展示',
            'department': '业务部门',
            'date': '2026年1月',
            'chapters': [
                {
                    'id': 'chapter1',
                    'name': '第一章',
                    'description': '核心业务能力建设'
                },
                {
                    'id': 'chapter2',
                    'name': '第二章',
                    'description': '技术创新与优化'
                }
            ],
            'slides': [
                'slide-cover',
                'slide-toc1',
                'slide1'
            ]
        }

    def load_config(self, config_file):
        """加载配置文件"""
        if config_file and Path(config_file).exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                self.config.update(user_config)
                print(f"✅ 配置文件已加载: {config_file}")

    def generate_skeleton(self, name='汇报材料'):
        """生成基本骨架模板"""
        output_path = self.output_dir / f"{name}-skeleton.html"

        with open(self.template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()

        # 使用字符串模板替换占位符
        template = Template(template_content)

        # 渲染模板
        html_content = template.substitute(
            PRESENTATION_TITLE=name,
            PRESENTATION_SUBTITLE=self.config.get('subtitle', ''),
            DEPARTMENT=self.config.get('department', ''),
            DATE=self.config.get('date', ''),
            CHAPTER1_NAME=self.config['chapters'][0]['name'],
            CHAPTER1_DESC=self.config['chapters'][0]['description'],
            CHAPTER2_NAME=self.config['chapters'][1]['name'],
            CHAPTER2_DESC=self.config['chapters'][1]['description'],
            CONTENT_PAGE_TITLE='核心业务能力展示',
            COLUMN1_TITLE='ASR能力',
            COLUMN1_SUBTITLE='语音识别',
            COLUMN1_TAG='准确率 > 95%',
            COLUMN1_FEATURES='<li>实时语音转文本</li><li>支持多种方言</li><li>智能断句处理</li>',
            COLUMN1_STATUS='已上线运行',
            COLUMN2_TITLE='TTS能力',
            COLUMN2_SUBTITLE='语音合成',
            COLUMN2_TAG='自然度 > 90%',
            COLUMN2_FEATURES='<li>多音色支持</li><li>情感语音合成</li><li>SSML标记支持</li>',
            COLUMN2_STATUS='开发中',
            COLUMN3_TITLE='智能质检',
            COLUMN3_SUBTITLE='自动质控',
            COLUMN3_TAG='覆盖率 > 98%',
            COLUMN3_FEATURES='<li>违规行为检测</li><li>质检规则引擎</li><li>智能评分模型</li>',
            COLUMN3_STATUS='已上线运行'
        )

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"✅ 骨架模板已生成: {output_path}")
        return output_path

    def generate_from_custom(self, config_file, output_name='汇报材料'):
        """根据自定义配置生成完整汇报材料"""
        self.load_config(config_file)

        output_path = self.output_dir / f"{output_name}.html"

        with open(self.template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()

        # 生成页面内容
        slides_html = self._generate_slides_html()

        # 完整的HTML文档
        html_content = self._build_full_html(slides_html)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"✅ 完整汇报材料已生成: {output_path}")
        return output_path

    def _generate_slides_html(self):
        """根据配置生成幻灯片HTML"""
        html_parts = []

        # 封面页
        if 'slide-cover' in self.config['slides']:
            html_parts.append(self._render_cover_slide())

        # 目录页
        if 'slide-toc1' in self.config['slides']:
            html_parts.append(self._render_toc_slide())

        # 其他页面...
        for slide_id in self.config['slides']:
            if slide_id.startswith('slide') and slide_id not in ['slide-cover', 'slide-toc1']:
                html_parts.append(self._render_content_slide(slide_id))

        return '\n'.join(html_parts)

    def _render_cover_slide(self):
        """渲染封面页"""
        return f'''
    <div id="slide-cover" class="slide cover-slide">
        <h1 class="cover-title">{self.config['title']}</h1>
        <p class="cover-subtitle">{self.config['subtitle']}</p>
        <div class="cover-info">
            <p>{self.config['department']}</p>
            <p>{self.config['date']}</p>
        </div>
    </div>'''

    def _render_toc_slide(self):
        """渲染目录页"""
        html = '''
    <div id="slide-toc1" class="slide">
        <h2 class="page-title">目录 CONTENTS</h2>
        <div style="display: flex; gap: 30px; margin-top: 30px;">
            <div style="flex: 1; background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); border-radius: 16px; padding: 40px; color: white;">
                <h3 style="font-size: 28px; margin-bottom: 30px;">目录</h3>
                <p style="font-size: 18px; opacity: 0.9;">CONTENTS</p>
            </div>
            <div style="flex: 2;">'''

        for chapter in self.config['chapters']:
            html += f'''
                <div style="background: rgba(0, 102, 204, 0.1); border-radius: 12px; padding: 20px; margin-bottom: 15px; border-left: 4px solid var(--primary-blue);">
                    <h4 style="font-size: 20px; color: var(--primary-blue); margin-bottom: 8px;">{chapter['name']}</h4>
                    <p style="font-size: 14px; color: #666;">{chapter['description']}</p>
                </div>'''

        html += '''
            </div>
        </div>
    </div>'''

        return html

    def _render_content_slide(self, slide_id):
        """渲染内容页（示例）"""
        return f'''
    <div id="{slide_id}" class="slide">
        <h2 class="page-title">内容展示</h2>
        <div class="three-columns">
            <div class="column-card">
                <div class="column-header">
                    <h3>能力一</h3>
                    <p>详细说明</p>
                </div>
                <div class="feature-tag">关键指标</div>
                <div class="column-features">
                    <ul>
                        <li>功能特性1</li>
                        <li>功能特性2</li>
                        <li>功能特性3</li>
                    </ul>
                </div>
                <div class="status-green">已完成</div>
            </div>
            <div class="column-card">
                <div class="column-header">
                    <h3>能力二</h3>
                    <p>详细说明</p>
                </div>
                <div class="feature-tag">关键指标</div>
                <div class="column-features">
                    <ul>
                        <li>功能特性1</li>
                        <li>功能特性2</li>
                        <li>功能特性3</li>
                    </ul>
                </div>
                <div class="status-orange">进行中</div>
            </div>
            <div class="column-card">
                <div class="column-header">
                    <h3>能力三</h3>
                    <p>详细说明</p>
                </div>
                <div class="feature-tag">关键指标</div>
                <div class="column-features">
                    <ul>
                        <li>功能特性1</li>
                        <li>功能特性2</li>
                        <li>功能特性3</li>
                    </ul>
                </div>
                <div class="status-green">已完成</div>
            </div>
        </div>
    </div>'''

    def _build_full_html(self, slides_html):
        """构建完整的HTML文档"""
        slides = ','.join([f"'{s}'" for s in self.config['slides']])

        return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.config['title']}</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <style>
        /* 样式已在模板中定义 */
    </style>
</head>
<body>

<div class="presentation">
    {slides_html}
</div>

<div class="nav-controls">
    <button class="nav-btn" id="prevBtn" onclick="changeSlide(-1)">←</button>
    <span class="page-indicator"><span id="currentPage">1</span> / <span id="totalPages">{len(self.config['slides'])}</span></span>
    <button class="nav-btn" id="nextBtn" onclick="changeSlide(1)">→</button>
</div>

<script>
    const slideOrder = [{slides}];
    let currentSlide = 1;
    const totalSlides = slideOrder.length;

    function showSlide(n) {{
        if (n > totalSlides) currentSlide = 1;
        if (n < 1) currentSlide = totalSlides;

        document.querySelectorAll('.slide').forEach(slide => slide.classList.remove('active'));
        const slideId = slideOrder[currentSlide - 1];
        document.getElementById(slideId).classList.add('active');
        document.getElementById('currentPage').textContent = currentSlide;
        document.getElementById('totalPages').textContent = totalSlides;
        document.getElementById('prevBtn').disabled = currentSlide === 1;
        document.getElementById('nextBtn').disabled = currentSlide === totalSlides;
        window.scrollTo(0, 0);
    }}

    function changeSlide(direction) {{
        currentSlide += direction;
        showSlide(currentSlide);
    }}

    document.addEventListener('keydown', function(e) {{
        if (e.key === 'ArrowLeft') changeSlide(-1);
        else if (e.key === 'ArrowRight') changeSlide(1);
    }});

    document.addEventListener('DOMContentLoaded', async function() {{
        mermaid.initialize({{
            startOnLoad: false,
            theme: 'default'
        }});
        showSlide(currentSlide);
    }});
</script>

</body>
</html>'''


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='H5汇报材料生成器')
    parser.add_argument('--template', '-t',
                       default='/tmp/h5-report-skill/templates/h5-report-template.html',
                       help='模板文件路径')
    parser.add_argument('--output', '-o',
                       default='./output',
                       help='输出目录')
    parser.add_argument('--name', '-n',
                       default='汇报材料',
                       help='项目名称')
    parser.add_argument('--config', '-c',
                       help='配置文件路径（JSON格式）')

    args = parser.parse_args()

    # 验证模板文件
    if not Path(args.template).exists():
        print(f"❌ 模板文件不存在: {args.template}")
        sys.exit(1)

    # 创建生成器实例
    generator = H5ReportGenerator(args.template, args.output)

    try:
        if args.config:
            # 根据配置生成完整汇报
            generator.generate_from_custom(args.config, args.name)
        else:
            # 生成基本骨架
            generator.generate_skeleton(args.name)

        print(f"\n✅ 生成完成！")
        print(f"📁 输出目录: {Path(args.output).absolute()}")

    except Exception as e:
        print(f"❌ 生成失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()