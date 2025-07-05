#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import html as html_module
from datetime import datetime

def generate_complete_bilingual_webpage():
    """生成包含人物关系图的完整双语网页"""
    
    # 读取清洁版本的英文和中文
    with open('./en_clean.txt', 'r', encoding='utf-8') as f:
        english_lines = [line.rstrip('\n') for line in f.readlines()]
    
    with open('./cn_clean.txt', 'r', encoding='utf-8') as f:
        chinese_lines = [line.rstrip('\n') for line in f.readlines()]
    
    print(f"清洁版英文行数: {len(english_lines)}")
    print(f"清洁版中文行数: {len(chinese_lines)}")
    
    # 检测章节和结构
    chapters = detect_chapters_clean(english_lines, chinese_lines)
    print(f"检测到 {len(chapters)} 个章节")
    
    # 生成HTML
    html_content = generate_html_with_relationships(english_lines, chinese_lines, chapters)
    
    # 写入文件
    output_file = './true_friend_bilingual_complete.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"完整版双语网页已生成: {output_file}")
    return output_file

def detect_chapters_clean(english_lines, chinese_lines):
    """检测清洁版本的章节结构"""
    chapters = []
    current_chapter = None
    
    for i, (en_line, cn_line) in enumerate(zip(english_lines, chinese_lines)):
        en_stripped = en_line.strip()
        cn_stripped = cn_line.strip()
        
        # 检测章节标题
        if re.match(r'^CHAPTER\s+[IVX]+\.?$', en_stripped, re.IGNORECASE):
            if current_chapter:
                chapters.append(current_chapter)
            
            current_chapter = {
                'number': len(chapters) + 1,
                'title_en': en_stripped,
                'title_cn': cn_stripped,
                'subtitle_en': '',
                'subtitle_cn': '',
                'start_line': i,
                'content': []
            }
        elif current_chapter and i == current_chapter['start_line'] + 1:
            # 章节副标题（紧跟在CHAPTER后面的行）
            current_chapter['subtitle_en'] = en_stripped
            current_chapter['subtitle_cn'] = cn_stripped
        elif current_chapter and en_stripped:
            # 章节内容（跳过空行）
            current_chapter['content'].append({
                'line_num': i + 1,
                'en': en_line,
                'cn': cn_line
            })
    
    # 添加最后一章
    if current_chapter:
        chapters.append(current_chapter)
    
    return chapters

def generate_html_with_relationships(english_lines, chinese_lines, chapters):
    """生成包含人物关系图的HTML内容"""
    
    # CSS样式定义
    css_styles = """
        body {
            font-family: "Times New Roman", "宋体", serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #f5f3f0 0%, #ede8e3 100%);
            background-attachment: fixed;
            position: relative;
        }
        
        /* 维多利亚风格背景花纹 */
        body::before {
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: 
                radial-gradient(circle at 25% 25%, rgba(139, 69, 19, 0.03) 0%, transparent 50%),
                radial-gradient(circle at 75% 75%, rgba(160, 82, 45, 0.03) 0%, transparent 50%),
                linear-gradient(45deg, transparent 40%, rgba(205, 133, 63, 0.02) 50%, transparent 60%),
                linear-gradient(-45deg, transparent 40%, rgba(222, 184, 135, 0.02) 50%, transparent 60%);
            background-size: 120px 120px, 80px 80px, 60px 60px, 40px 40px;
            background-position: 0 0, 40px 40px, 0 0, 20px 20px;
            pointer-events: none;
            z-index: -1;
        }
        
        /* 页面边框装饰 */
        body::after {
            content: '';
            position: fixed;
            top: 10px;
            left: 10px;
            right: 10px;
            bottom: 10px;
            border: 2px solid rgba(139, 69, 19, 0.1);
            border-image: linear-gradient(45deg, 
                rgba(160, 82, 45, 0.2), 
                rgba(205, 133, 63, 0.1), 
                rgba(222, 184, 135, 0.2), 
                rgba(160, 82, 45, 0.2)
            ) 1;
            pointer-events: none;
            z-index: -1;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            box-shadow: 
                0 0 30px rgba(139, 69, 19, 0.1),
                inset 0 1px 0 rgba(255, 255, 255, 0.8);
            padding: 40px;
            border-radius: 15px;
            border: 1px solid rgba(205, 133, 63, 0.2);
            position: relative;
        }
        
        /* 容器装饰花纹 */
        .container::before {
            content: '';
            position: absolute;
            top: 15px;
            left: 15px;
            right: 15px;
            bottom: 15px;
            border: 1px solid rgba(160, 82, 45, 0.1);
            border-radius: 10px;
            background: 
                radial-gradient(circle at 20% 20%, rgba(222, 184, 135, 0.05) 0%, transparent 30%),
                radial-gradient(circle at 80% 80%, rgba(205, 133, 63, 0.05) 0%, transparent 30%);
            pointer-events: none;
        }
        .title {
            text-align: center;
            margin-bottom: 40px;
            border-bottom: 3px double rgba(139, 69, 19, 0.3);
            padding-bottom: 25px;
            position: relative;
            background: linear-gradient(135deg, rgba(245, 245, 220, 0.3) 0%, rgba(255, 248, 220, 0.2) 100%);
            border-radius: 10px;
            margin: 0 -20px 40px -20px;
            padding: 25px 20px;
        }
        
        /* 标题装饰花纹 */
        .title::before {
            content: '❦';
            position: absolute;
            top: -15px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 30px;
            color: rgba(160, 82, 45, 0.4);
            background: rgba(255, 255, 255, 0.9);
            padding: 0 15px;
        }
        
        .title::after {
            content: '';
            position: absolute;
            bottom: -10px;
            left: 50%;
            transform: translateX(-50%);
            width: 100px;
            height: 20px;
            background: 
                radial-gradient(ellipse, rgba(205, 133, 63, 0.2) 0%, transparent 70%);
        }
        .title h1 {
            color: #5d4037;
            margin: 15px 0;
            text-shadow: 1px 1px 2px rgba(139, 69, 19, 0.1);
            font-weight: normal;
            letter-spacing: 1px;
        }
        .comparison-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
            background: rgba(255, 255, 255, 0.7);
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(139, 69, 19, 0.05);
        }
        .comparison-table td {
            vertical-align: top;
            padding: 20px;
            border-bottom: 1px solid rgba(205, 133, 63, 0.1);
            position: relative;
        }
        
        /* 表格行装饰 */
        .comparison-table tr:nth-child(even) {
            background: rgba(245, 245, 220, 0.1);
        }
        
        .comparison-table tr:hover {
            background: rgba(222, 184, 135, 0.05);
            transition: background 0.3s ease;
        }
        .english-column {
            width: 50%;
            border-right: 2px solid rgba(160, 82, 45, 0.2);
            font-family: 'Times New Roman', serif;
            font-size: 14px;
            color: #4a4a4a;
            line-height: 1.6;
            position: relative;
        }
        
        /* 英文列装饰 */
        .english-column::before {
            content: '';
            position: absolute;
            top: 0;
            right: -1px;
            width: 1px;
            height: 100%;
            background: linear-gradient(to bottom, 
                transparent 0%, 
                rgba(205, 133, 63, 0.3) 50%, 
                transparent 100%);
        }
        .chinese-column {
            width: 50%;
            font-family: '宋体', serif;
            font-size: 15px;
            color: #3e2723;
            line-height: 1.7;
            position: relative;
        }
        
        /* 中文列装饰 */
        .chinese-column::before {
            content: '';
            position: absolute;
            top: 10px;
            left: -10px;
            width: 3px;
            height: 30px;
            background: linear-gradient(to bottom, 
                rgba(222, 184, 135, 0.4), 
                rgba(205, 133, 63, 0.2));
            border-radius: 2px;
        }
        .chapter-header {
            background: linear-gradient(135deg, 
                rgba(245, 245, 220, 0.6) 0%, 
                rgba(255, 248, 220, 0.4) 50%, 
                rgba(245, 245, 220, 0.6) 100%);
            padding: 20px;
            margin: 40px 0 25px 0;
            border-left: 6px solid rgba(139, 69, 19, 0.4);
            border-right: 6px solid rgba(139, 69, 19, 0.4);
            text-align: center;
            border-radius: 8px;
            position: relative;
            box-shadow: 
                0 2px 10px rgba(139, 69, 19, 0.1),
                inset 0 1px 0 rgba(255, 255, 255, 0.5);
        }
        
        /* 章节标题装饰花纹 */
        .chapter-header::before {
            content: '◆ ◇ ◆';
            position: absolute;
            top: -10px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(255, 255, 255, 0.9);
            padding: 0 15px;
            color: rgba(160, 82, 45, 0.6);
            font-size: 12px;
            letter-spacing: 5px;
        }
        
        .chapter-header::after {
            content: '◆ ◇ ◆';
            position: absolute;
            bottom: -10px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(255, 255, 255, 0.9);
            padding: 0 15px;
            color: rgba(160, 82, 45, 0.6);
            font-size: 12px;
            letter-spacing: 5px;
        }
        .chapter-header h2 {
            margin: 0;
            color: #5d4037;
            text-shadow: 1px 1px 2px rgba(139, 69, 19, 0.1);
            font-weight: normal;
            letter-spacing: 2px;
        }
        .paragraph-marker {
            color: rgba(139, 69, 19, 0.6);
            font-size: 11px;
            margin-bottom: 8px;
            font-weight: bold;
            font-family: 'Times New Roman', serif;
            letter-spacing: 0.5px;
        }
        p {
            margin: 0 0 15px 0;
            text-align: justify;
        }
        .navigation {
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 15px;
            border: 2px solid rgba(160, 82, 45, 0.2);
            border-radius: 12px;
            box-shadow: 
                0 4px 20px rgba(139, 69, 19, 0.15),
                inset 0 1px 0 rgba(255, 255, 255, 0.8);
            max-height: 400px;
            overflow-y: auto;
            z-index: 9999;
            width: 220px;
        }
        
        /* 导航装饰花纹 */
        .navigation::before {
            content: '';
            position: absolute;
            top: 8px;
            left: 8px;
            right: 8px;
            bottom: 8px;
            border: 1px solid rgba(205, 133, 63, 0.1);
            border-radius: 8px;
            background: 
                radial-gradient(circle at 30% 30%, rgba(245, 245, 220, 0.3) 0%, transparent 50%),
                radial-gradient(circle at 70% 70%, rgba(222, 184, 135, 0.2) 0%, transparent 50%);
            pointer-events: none;
        }
        .navigation a {
            display: block;
            margin: 8px 0;
            color: #5d4037;
            text-decoration: none;
            font-size: 12px;
            padding: 6px 10px;
            border-radius: 6px;
            transition: all 0.3s ease;
            position: relative;
            z-index: 1;
        }
        .navigation a:hover {
            color: #3e2723;
            background: linear-gradient(135deg, 
                rgba(245, 245, 220, 0.6) 0%, 
                rgba(222, 184, 135, 0.3) 100%);
            transform: translateX(3px);
            box-shadow: 0 2px 8px rgba(139, 69, 19, 0.1);
        }
        .nav-section {
            margin-bottom: 18px;
            border-bottom: 1px solid rgba(205, 133, 63, 0.2);
            padding-bottom: 12px;
            position: relative;
        }
        
        /* 导航分节装饰 */
        .nav-section::after {
            content: '❦';
            position: absolute;
            bottom: -8px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 12px;
            color: rgba(160, 82, 45, 0.4);
            background: rgba(255, 255, 255, 0.9);
            padding: 0 8px;
        }
        .nav-title {
            font-weight: bold;
            color: #5d4037;
            margin-bottom: 8px;
            font-size: 13px;
            text-align: center;
            letter-spacing: 1px;
            text-shadow: 1px 1px 2px rgba(139, 69, 19, 0.1);
        }
        .progress-bar {
            position: fixed;
            top: 0;
            left: 0;
            width: 0%;
            height: 4px;
            background: linear-gradient(90deg, 
                rgba(139, 69, 19, 0.8) 0%, 
                rgba(205, 133, 63, 0.8) 50%, 
                rgba(222, 184, 135, 0.8) 100%);
            z-index: 9998;
            box-shadow: 0 2px 4px rgba(139, 69, 19, 0.3);
        }
        .nav-toggle-btn {
            display: block;
            width: 100%;
            background: linear-gradient(135deg, 
                rgba(245, 245, 220, 0.8) 0%, 
                rgba(222, 184, 135, 0.6) 100%);
            border: 1px solid rgba(160, 82, 45, 0.3);
            color: #5d4037;
            font-size: 12px;
            padding: 8px 0;
            margin-bottom: 12px;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 500;
            letter-spacing: 0.5px;
            position: relative;
            z-index: 1;
        }
        .nav-toggle-btn:hover {
            background: linear-gradient(135deg, 
                rgba(222, 184, 135, 0.8) 0%, 
                rgba(205, 133, 63, 0.6) 100%);
            transform: translateY(-1px);
            box-shadow: 0 3px 8px rgba(139, 69, 19, 0.2);
        }
        #navContent {
            transition: all 0.4s ease;
            overflow: hidden;
            position: relative;
        }
        #navContent.collapsed {
            max-height: 0;
            opacity: 0;
            margin: 0;
            padding: 0;
        }
        
        /* 添加一些维多利亚风格的装饰元素 */
        .ornament {
            text-align: center;
            margin: 30px 0;
            color: rgba(160, 82, 45, 0.4);
            font-size: 18px;
            letter-spacing: 10px;
        }
        
        /* 首字母装饰 */
        .first-letter {
            float: left;
            font-size: 4em;
            line-height: 0.8;
            margin: 0.1em 0.1em 0.1em 0;
            color: rgba(139, 69, 19, 0.7);
            font-family: 'Times New Roman', serif;
            text-shadow: 2px 2px 4px rgba(139, 69, 19, 0.1);
        }
        
        /* 响应式设计 */
        @media (max-width: 768px) {
            body {
                padding: 10px;
            }
            
            .container {
                padding: 20px;
                margin: 0 5px;
            }
            
            .navigation {
                position: fixed !important;
                top: 10px !important;
                right: 10px !important;
                width: 180px !important;
                max-height: 300px;
                font-size: 11px;
            }
            
            .navigation a {
                font-size: 11px;
                padding: 4px 8px;
                margin: 4px 0;
            }
            
            .nav-title {
                font-size: 12px;
            }
            
            .nav-toggle-btn {
                font-size: 11px;
                padding: 6px 0;
            }
            
            .comparison-table {
                display: block;
            }
            
            .comparison-table tr {
                display: block;
                margin-bottom: 20px;
                border: 1px solid rgba(205, 133, 63, 0.2);
                border-radius: 8px;
                overflow: hidden;
            }
            
            .comparison-table td {
                display: block;
                width: 100%;
                border-right: none;
                border-bottom: 1px solid rgba(205, 133, 63, 0.1);
            }
            
            .english-column::before,
            .chinese-column::before {
                display: none;
            }
            
            .first-letter {
                font-size: 3em;
            }
            
            .ornament {
                font-size: 14px;
                letter-spacing: 5px;
            }
        }
        
        @media (max-width: 480px) {
            .container {
                padding: 15px;
            }
            
            .navigation {
                position: fixed !important;
                top: 5px !important;
                right: 5px !important;
                width: 160px !important;
                max-height: 250px;
            }
            
            .navigation a {
                font-size: 10px;
                padding: 3px 6px;
            }
            
            .nav-title {
                font-size: 11px;
            }
            
            .nav-toggle-btn {
                font-size: 10px;
                padding: 5px 0;
            }
            
            .title {
                margin: 0 -10px 30px -10px;
                padding: 20px 10px;
            }
            
            .title h1 {
                font-size: 1.5em;
            }
            
            .chapter-header {
                padding: 15px;
                margin: 30px 0 20px 0;
            }
            
            .first-letter {
                font-size: 2.5em;
            }
        }
        .note {
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
            font-size: 13px;
        }
        .relationship-diagram {
            text-align: center;
            margin: 30px 0;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 10px;
        }
        .family-group {
            display: inline-block;
            margin: 15px;
            padding: 15px;
            border: 2px solid #007bff;
            border-radius: 8px;
            background-color: white;
            vertical-align: top;
        }
        .family-title {
            font-weight: bold;
            color: #007bff;
            margin-bottom: 10px;
            text-align: center;
        }
        .character-box {
            margin: 5px 0;
            padding: 5px;
            background-color: #e9ecef;
            border-radius: 4px;
            font-size: 12px;
        }
        .main-character {
            background-color: #ffd700;
            font-weight: bold;
        }
        .connection-line {
            display: inline-block;
            width: 50px;
            height: 2px;
            background-color: #666;
            margin: 0 10px;
            vertical-align: middle;
        }
        .character-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        .character-table th, .character-table td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        .character-table th {
            background-color: #f2f2f2;
            font-weight: bold;
        }
        .character-table .english-name {
            font-family: 'Times New Roman', serif;
            font-style: italic;
        }
        .character-table .chinese-name {
            font-family: '宋体', serif;
            font-weight: bold;
        }
        .stats {
            background-color: #e8f5e8;
            border: 1px solid #4caf50;
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
        }
        .stats h3 {
            margin-top: 0;
            color: #2e7d32;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 10px;
        }
        .stat-item {
            text-align: center;
            padding: 10px;
            background: white;
            border-radius: 5px;
        }
        .stat-number {
            font-size: 24px;
            font-weight: bold;
            color: #2e7d32;
        }
        .stat-label {
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        }
    """
    
    # HTML内容构建
    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>《真正的朋友》中英文完整对照版</title>
    <style>
{css_styles}
    </style>
</head>
<body>
    <div class="progress-bar" id="progressBar"></div>
    <div class="navigation" id="navMenu">
        <button class="nav-toggle-btn" id="navToggleBtn">收起导航 ▲</button>
        <div id="navContent">
            <div class="nav-section">
                <div class="nav-title">导航 / Navigation</div>
                <a href="#title">标题 / Title</a>
                <a href="#stats">版本信息 / Version Info</a>
                <a href="#characters">人物表 / Characters</a>
                <a href="#relationships">人物关系 / Characters</a>
            </div>
            <div class="nav-section">
                <div class="nav-title">章节 / Chapters</div>'''
    
    # 动态添加章节导航
    for chapter in chapters:
        chapter_id = f"chapter{chapter['number']}"
        html_content += f'''
            <a href="#{chapter_id}">{chapter['title_cn']} / {chapter['title_en']}<br><small>{chapter['subtitle_cn']} / {chapter['subtitle_en']}</small></a>'''
    
    # Close the navigation structure properly after the loop
    html_content += '''
            </div>
        </div>
    </div>

    <div class="container">
        <div class="title" id="title">
            <h1>《真正的朋友》清洁版</h1>
            <h1>A TRUE FRIEND - Clean Edition</h1>
            <p>中英文完整对照版 - Complete Chinese-English Parallel Text</p>
            <p><em>作者：阿德琳·萨金特 (Adeline Sergeant)</em></p>
        </div>

        <!-- 版本信息 -->
        <div class="ornament">❦ ◆ ❦ ◆ ❦</div>
        <div id="stats" class="stats">
            <h3>📊 清洁版本信息 / Clean Version Statistics</h3>
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-number">375</div>
                    <div class="stat-label">总行数 / Total Lines</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">6</div>
                    <div class="stat-label">章节数 / Chapters</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">100%</div>
                    <div class="stat-label">行对应率 / Line Correspondence</div>
                </div>
            </div>
        </div>

        <!-- 人物对照表 -->
        <div class="ornament">◇ ❦ ◇ ❦ ◇</div>
        <div id="characters" class="chapter-header">
            <h2>主要人物对照表 / CHARACTER LIST</h2>
        </div>

        <table class="comparison-table">
            <tr>
                <td class="english-column">
                    <h3>Main Characters</h3>
                    <table class="character-table">
                        <tr>
                            <th>English Name</th>
                            <th>Role/Description</th>
                        </tr>
                        <tr>
                            <td class="english-name">Janetta Colwyn</td>
                            <td>Music governess, pupil-teacher</td>
                        </tr>
                        <tr>
                            <td class="english-name">Margaret Adair</td>
                            <td>Beauty and heiress, Janetta's friend</td>
                        </tr>
                        <tr>
                            <td class="english-name">Lady Caroline Adair</td>
                            <td>Margaret's mother</td>
                        </tr>
                        <tr>
                            <td class="english-name">Mr. Reginald Adair</td>
                            <td>Margaret's father</td>
                        </tr>
                        <tr>
                            <td class="english-name">Sir Philip Ashley</td>
                            <td>Young baronet, neighbor</td>
                        </tr>
                        <tr>
                            <td class="english-name">Miss Polehampton</td>
                            <td>School principal</td>
                        </tr>
                        <tr>
                            <td class="english-name">Mr. Colwyn</td>
                            <td>Janetta's father, surgeon</td>
                        </tr>
                        <tr>
                            <td class="english-name">Mrs. Colwyn</td>
                            <td>Janetta's stepmother</td>
                        </tr>
                        <tr>
                            <td class="english-name">Nora Colwyn</td>
                            <td>Janetta's stepsister</td>
                        </tr>
                        <tr>
                            <td class="english-name">Wyvis Brand</td>
                            <td>Young man from Brand Hall</td>
                        </tr>
                        <tr>
                            <td class="english-name">Mrs. Brand</td>
                            <td>Wyvis's mother</td>
                        </tr>
                    </table>
                </td>
                <td class="chinese-column">
                    <h3>主要人物</h3>
                    <table class="character-table">
                        <tr>
                            <th>中文姓名</th>
                            <th>角色/描述</th>
                        </tr>
                        <tr>
                            <td class="chinese-name">珍妮塔·科尔温</td>
                            <td>音乐女教师，学生教师</td>
                        </tr>
                        <tr>
                            <td class="chinese-name">玛格丽特·阿代尔</td>
                            <td>美人和女继承人，珍妮塔的朋友</td>
                        </tr>
                        <tr>
                            <td class="chinese-name">卡罗琳·阿代尔夫人</td>
                            <td>玛格丽特的母亲</td>
                        </tr>
                        <tr>
                            <td class="chinese-name">雷金纳德·阿代尔先生</td>
                            <td>玛格丽特的父亲</td>
                        </tr>
                        <tr>
                            <td class="chinese-name">菲利普·阿什利爵士</td>
                            <td>年轻男爵，邻居</td>
                        </tr>
                        <tr>
                            <td class="chinese-name">波尔汉普顿小姐</td>
                            <td>学校校长</td>
                        </tr>
                        <tr>
                            <td class="chinese-name">科尔温先生</td>
                            <td>珍妮塔的父亲，外科医生</td>
                        </tr>
                        <tr>
                            <td class="chinese-name">科尔温夫人</td>
                            <td>珍妮塔的继母</td>
                        </tr>
                        <tr>
                            <td class="chinese-name">诺拉·科尔温</td>
                            <td>珍妮塔的继妹</td>
                        </tr>
                        <tr>
                            <td class="chinese-name">威维斯·布兰德</td>
                            <td>布兰德庄园的年轻人</td>
                        </tr>
                        <tr>
                            <td class="chinese-name">布兰德夫人</td>
                            <td>威维斯的母亲</td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>

        <!-- 人物关系图 -->
        <div id="relationships" class="chapter-header">
            <h2>人物关系图 / CHARACTER RELATIONSHIPS</h2>
        </div>

        <table class="comparison-table">
            <tr>
                <td class="english-column">
                    <div class="relationship-diagram">
                        <h3>Character Relationships</h3>
                        
                        <div class="family-group">
                            <div class="family-title">Adair Family</div>
                            <div class="character-box">Lady Caroline Adair<br><small>(Mother)</small></div>
                            <div class="character-box">Mr. Reginald Adair<br><small>(Father)</small></div>
                            <div class="character-box main-character">Margaret Adair<br><small>(Daughter, Heiress)</small></div>
                        </div>

                        <div class="connection-line"></div>

                        <div class="family-group">
                            <div class="family-title">School</div>
                            <div class="character-box">Miss Polehampton<br><small>(Principal)</small></div>
                            <div class="character-box main-character">Janetta Colwyn<br><small>(Music Governess)</small></div>
                        </div>

                        <div class="connection-line"></div>

                        <div class="family-group">
                            <div class="family-title">Colwyn Family</div>
                            <div class="character-box">Mr. Colwyn<br><small>(Father, Surgeon)</small></div>
                            <div class="character-box">Mrs. Colwyn<br><small>(Stepmother)</small></div>
                            <div class="character-box">Nora Colwyn<br><small>(Stepsister)</small></div>
                            <div class="character-box">Joey, Georgie, Tiny, etc.<br><small>(Step-siblings)</small></div>
                        </div>

                        <br><br>

                        <div class="family-group">
                            <div class="family-title">Neighbors</div>
                            <div class="character-box">Sir Philip Ashley<br><small>(Young Baronet)</small></div>
                        </div>

                        <div class="connection-line"></div>

                        <div class="family-group">
                            <div class="family-title">Brand Family</div>
                            <div class="character-box">Mrs. Brand<br><small>(Mother)</small></div>
                            <div class="character-box">Wyvis Brand<br><small>(Son)</small></div>
                            <div class="character-box">Cuthbert Brand<br><small>(Younger Son)</small></div>
                        </div>

                        <div style="margin-top: 20px; font-size: 12px; color: #666;">
                            <strong>Key Relationships:</strong><br>
                            • Margaret ↔ Janetta: Close friends<br>
                            • Lady Caroline → Margaret: Protective mother<br>
                            • Sir Philip → Margaret: Romantic interest<br>
                            • Wyvis ↔ Janetta: Potential friendship<br>
                            • Brand family ↔ Colwyn family: Distant relatives
                        </div>
                    </div>
                </td>
                <td class="chinese-column">
                    <div class="relationship-diagram">
                        <h3>人物关系</h3>
                        
                        <div class="family-group">
                            <div class="family-title">阿代尔家族</div>
                            <div class="character-box">卡罗琳·阿代尔夫人<br><small>(母亲)</small></div>
                            <div class="character-box">雷金纳德·阿代尔先生<br><small>(父亲)</small></div>
                            <div class="character-box main-character">玛格丽特·阿代尔<br><small>(女儿，女继承人)</small></div>
                        </div>

                        <div class="connection-line"></div>

                        <div class="family-group">
                            <div class="family-title">学校</div>
                            <div class="character-box">波尔汉普顿小姐<br><small>(校长)</small></div>
                            <div class="character-box main-character">珍妮塔·科尔温<br><small>(音乐女教师)</small></div>
                        </div>

                        <div class="connection-line"></div>

                        <div class="family-group">
                            <div class="family-title">科尔温家族</div>
                            <div class="character-box">科尔温先生<br><small>(父亲，外科医生)</small></div>
                            <div class="character-box">科尔温夫人<br><small>(继母)</small></div>
                            <div class="character-box">诺拉·科尔温<br><small>(继妹)</small></div>
                            <div class="character-box">乔伊、乔治、小不点等<br><small>(继兄弟姐妹)</small></div>
                        </div>

                        <br><br>

                        <div class="family-group">
                            <div class="family-title">邻居</div>
                            <div class="character-box">菲利普·阿什利爵士<br><small>(年轻男爵)</small></div>
                        </div>

                        <div class="connection-line"></div>

                        <div class="family-group">
                            <div class="family-title">布兰德家族</div>
                            <div class="character-box">布兰德夫人<br><small>(母亲)</small></div>
                            <div class="character-box">威维斯·布兰德<br><small>(儿子)</small></div>
                            <div class="character-box">卡斯伯特·布兰德<br><small>(小儿子)</small></div>
                        </div>

                        <div style="margin-top: 20px; font-size: 12px; color: #666;">
                            <strong>主要关系：</strong><br>
                            • 玛格丽特 ↔ 珍妮塔：亲密朋友<br>
                            • 卡罗琳夫人 → 玛格丽特：保护性母亲<br>
                            • 菲利普爵士 → 玛格丽特：爱慕关系<br>
                            • 威维斯 ↔ 珍妮塔：潜在友谊<br>
                            • 布兰德家族 ↔ 科尔温家族：远亲关系
                        </div>
                    </div>
                </td>
            </tr>
        </table>'''
    
    # 添加章节内容
    for chapter in chapters:
        chapter_id = f"chapter{chapter['number']}"
        html_content += f'''
        
        <div class="ornament">◆ ❦ ◆ ❦ ◆</div>
        <div id="{chapter_id}" class="chapter-header">
            <h2>{chapter['title_cn']} / {chapter['title_en']}</h2>
            <p><em>{chapter['subtitle_cn']} / {chapter['subtitle_en']}</em></p>
        </div>
        
        <table class="comparison-table">'''
        
        # 添加章节段落
        # 在章节内容循环中，替换原有的段落标记行：
        for i, content in enumerate(chapter['content']):
            if content['en'].strip() and content['cn'].strip():
                html_content += f'''
            <tr>
                <td class="english-column">
                    <div class="paragraph-marker">§{chapter['number']}.{i+1} (Line {content['line_num']})</div>
                    <p>{html_module.escape(content['en'])}</p>
                </td>
                <td class="chinese-column">
                    <div class="paragraph-marker">§{chapter['number']}.{i+1} (第{content['line_num']}行)</div>
                    <p>{html_module.escape(content['cn'])}</p>
                </td>
            </tr>'''
        
        html_content += '''
        </table>'''
    
    # 添加JavaScript和HTML结束标签
    html_content += '''
    
    <div class="ornament">❦ ◆ ❦ ◆ ❦</div>
    <div style="text-align: center; margin: 40px 0; color: #666; font-size: 14px;">
        <p>--- 全文完 / THE END ---</p>
        <p><em>Generated on ''' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '''</em></p>
    </div>
    
    </div>

    <script>
        // 导航切换功能
        document.getElementById('navToggleBtn').addEventListener('click', function() {
            const navContent = document.getElementById('navContent');
            const btn = this;
            
            if (navContent.classList.contains('collapsed')) {
                navContent.classList.remove('collapsed');
                btn.textContent = '收起导航 ▲';
            } else {
                navContent.classList.add('collapsed');
                btn.textContent = '展开导航 ▼';
            }
        });
        
        // 滚动进度条
        window.addEventListener('scroll', function() {
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
            const scrollPercent = (scrollTop / scrollHeight) * 100;
            document.getElementById('progressBar').style.width = scrollPercent + '%';
        });
        
        // 平滑滚动到锚点
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
        
        // 响应式导航
        function adjustNavigation() {
            const nav = document.getElementById('navMenu');
            const navContent = document.getElementById('navContent');
            
            if (window.innerWidth <= 768) {
                // 移动端默认收起导航
                if (!navContent.classList.contains('collapsed')) {
                    navContent.classList.add('collapsed');
                    document.getElementById('navToggleBtn').textContent = '展开导航 ▼';
                }
            }
        }
        
        // 页面加载时调整
        window.addEventListener('load', adjustNavigation);
        window.addEventListener('resize', adjustNavigation);
    </script>
</body>
</html>'''
    
    return html_content

if __name__ == "__main__":
    generate_complete_bilingual_webpage()
