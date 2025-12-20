#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模拟面试题生成器 - 清理版
基于memo文档内容，使用Gemini API生成Android逆向工程相关的面试题目
"""

import os
import json
import random
import argparse
import datetime
from pathlib import Path
from google import genai
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class InterviewGenerator:
    def __init__(self):
        """初始化面试题生成器"""
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file or environment variables.")
        
        # 配置代理（如果需要）
        proxy_url = "http://127.0.0.1:1087"
        os.environ['HTTP_PROXY'] = proxy_url
        os.environ['HTTPS_PROXY'] = proxy_url
        
        # 初始化Gemini客户端
        self.client = genai.Client(api_key=self.api_key)
        
        # 获取项目根目录和memo文件目录
        self.project_root = Path(__file__).parent
        self.memo_files = list(self.project_root.glob("memo_*.md"))
        
        # 创建面试题输出目录
        self.interviews_dir = self.project_root / "interviews"
        self.interviews_dir.mkdir(exist_ok=True)
        
        if not self.memo_files:
            raise FileNotFoundError("No memo_*.md files found in the current directory")
        
        print(f"Found {len(self.memo_files)} memo files: {[f.name for f in self.memo_files]}")
        print(f"面试题将保存到: {self.interviews_dir}")

    def read_memo_content(self, memo_file: Path) -> str:
        """读取memo文件内容"""
        try:
            with open(memo_file, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except Exception as e:
            print(f"Error reading {memo_file}: {e}")
            return ""

    def extract_interview_topics(self, content: str) -> list:
        """从memo内容中提取面试问题和相关信息"""
        import re
        
        topics = []
        
        # 按二级标题分块处理内容
        sections = re.split(r'^## (.+)$', content, flags=re.MULTILINE)
        
        for i in range(1, len(sections), 2):  # 跳过第一个元素，然后按标题-内容对处理
            if i + 1 >= len(sections):
                break
                
            section_title = sections[i].strip()
            section_content = sections[i + 1].strip()
            
            # 清理标题中的emoji
            clean_title = re.sub(r'[🔧📱📦🗂️⚡🏗️📋🔄📊🎯💡🔍⭐🚀💻🛠️📚]', '', section_title).strip()
            
            if not clean_title or len(clean_title) < 3:
                continue
            
            # 从内容中提取具体的面试问题
            section_topics = self._extract_topics_from_section(clean_title, section_content)
            topics.extend(section_topics)
        
        return topics
    
    def _extract_topics_from_section(self, section_title: str, content: str) -> list:
        """从单个章节中提取具体的面试话题"""
        import re
        
        topics = []
        
        # 提取三级标题和相关内容
        subsections = re.split(r'^### (.+)$', content, flags=re.MULTILINE)
        
        if len(subsections) > 1:
            # 有三级标题的情况
            for i in range(1, len(subsections), 2):
                if i + 1 >= len(subsections):
                    break
                    
                subsection_title = subsections[i].strip()
                subsection_content = subsections[i + 1].strip()
                
                # 清理标题
                clean_subtitle = re.sub(r'[🔧📱📦🗂️⚡🏗️📋🔄📊🎯💡🔍⭐🚀💻🛠️📚]', '', subsection_title).strip()
                
                # 生成问题
                topics.append({
                    'main_topic': section_title,
                    'subtopic': clean_subtitle,
                    'content': subsection_content,
                    'question_type': self._determine_question_type(subsection_content),
                    'difficulty': self._determine_difficulty(section_title, subsection_content)
                })
        else:
            # 没有三级标题，直接使用二级标题内容
            topics.append({
                'main_topic': section_title,
                'subtopic': '',
                'content': content,
                'question_type': self._determine_question_type(content),
                'difficulty': self._determine_difficulty(section_title, content)
            })
        
        return topics
    
    def _determine_question_type(self, content: str) -> str:
        """根据内容确定问题类型"""
        if '```' in content or '|' in content:
            return '概念解释'
        elif '处理方法' in content or '使用' in content or '工具' in content:
            return '实践操作'
        elif '对比' in content or 'vs' in content.lower():
            return '概念对比'
        elif '影响' in content or '问题' in content:
            return '问题分析'
        else:
            return '综合理解'
    
    def _determine_difficulty(self, section: str, content: str) -> str:
        """根据章节和内容确定难度"""
        basic_keywords = ['基础', '介绍', '概述', '结构', '组成']
        advanced_keywords = ['原理', '实现', '优化', '影响', '深入', '高级']
        
        section_lower = section.lower()
        content_lower = content.lower()
        
        if any(keyword in section_lower or keyword in content_lower for keyword in advanced_keywords):
            return '高级'
        elif any(keyword in section_lower or keyword in content_lower for keyword in basic_keywords):
            return '基础'
        else:
            return '中级'

    def generate_questions_from_topics(self, topics: list, num_questions: int = 10) -> list:
        """基于提取的话题生成面试问题和答案"""
        
        # 随机选择话题
        selected_topics = random.sample(topics, min(len(topics), num_questions))
        
        questions = []
        
        for i, topic in enumerate(selected_topics, 1):
            # 基于话题内容生成问题
            question_text = self._generate_question_text(topic)
            
            # 使用Gemini生成详细答案
            answer_text = self._generate_answer_with_gemini(topic, question_text)
            
            # 提取关键点
            key_points = self._extract_key_points(topic)
            
            questions.append({
                "id": i,
                "question": question_text,
                "answer": answer_text,
                "difficulty": topic['difficulty'],
                "category": topic['question_type'],
                "key_points": key_points
            })
        
        return questions
    
    def _generate_question_text(self, topic: dict) -> str:
        """基于话题生成面试问题文本"""
        main_topic = topic['main_topic']
        subtopic = topic['subtopic']
        question_type = topic['question_type']
        
        if subtopic:
            if question_type == '概念解释':
                return f"请详细解释{main_topic}中的{subtopic}概念"
            elif question_type == '实践操作':
                return f"在{main_topic}中，如何进行{subtopic}操作？请给出具体步骤"
            elif question_type == '概念对比':
                return f"请对比分析{main_topic}中{subtopic}的不同特点和应用场景"
            elif question_type == '问题分析':
                return f"分析{main_topic}中{subtopic}对Android逆向工程的影响"
            else:
                return f"请全面阐述{main_topic}中{subtopic}的相关知识点"
        else:
            if question_type == '概念解释':
                return f"请详细解释{main_topic}的基本概念和结构"
            elif question_type == '实践操作':
                return f"在实际Android逆向工程中，如何处理{main_topic}相关的任务？"
            elif question_type == '概念对比':
                return f"请分析{main_topic}的不同实现方式和特点"
            elif question_type == '问题分析':
                return f"分析{main_topic}在Android逆向工程中的重要性和应用"
            else:
                return f"请全面介绍{main_topic}的相关知识"
    
    def _generate_answer_with_gemini(self, topic: dict, question: str) -> str:
        """使用Gemini为特定问题生成详细答案"""
        
        content = topic['content']
        main_topic = topic['main_topic']
        
        prompt = f"""
你是一位资深的Android逆向工程专家。请基于以下技术文档内容，为面试问题提供详细、准确的答案。

面试问题：{question}

相关技术文档内容：
{content}

主题领域：{main_topic}

请提供详细的答案，要求：
1. 答案要准确、详细，包含具体的技术细节
2. 结合实际逆向工程场景进行说明
3. 如果有代码示例或命令，请给出具体的例子
4. 适合面试场景，既有理论深度又有实践指导
5. 答案长度适中，不要过于冗长

直接输出答案内容，不需要额外的格式包装：
"""

        try:
            response = self.client.models.generate_content(
                model='gemini-1.5-flash',
                contents=prompt
            )
            
            answer = response.text.strip()
            return answer if answer else "暂无详细答案，请参考相关技术文档。"
            
        except Exception as e:
            print(f"Error generating answer for question '{question}': {e}")
            # 如果Gemini调用失败，返回基于原始内容的简化答案
            return self._generate_fallback_answer(topic)
    
    def _generate_fallback_answer(self, topic: dict) -> str:
        """生成备用答案（当Gemini调用失败时）"""
        content = topic['content']
        main_topic = topic['main_topic']
        subtopic = topic['subtopic']
        
        answer = f"关于{main_topic}"
        if subtopic:
            answer += f"中的{subtopic}"
        
        answer += f":\n\n{content}\n\n"
        
        # 添加一些通用的补充说明
        if '基础' in topic['difficulty']:
            answer += "这是Android逆向工程中的基础概念，需要熟练掌握。"
        elif '高级' in topic['difficulty']:
            answer += "这是高级主题，需要深入理解其原理和在实际项目中的应用。"
        else:
            answer += "这个知识点在实际逆向分析中经常遇到，建议结合实践加深理解。"
        
        return answer
    
    def _extract_key_points(self, topic: dict) -> list:
        """提取话题的关键点"""
        key_points = []
        
        # 添加主题作为关键点
        if topic['main_topic']:
            key_points.append(topic['main_topic'])
        
        # 添加子主题
        if topic['subtopic']:
            key_points.append(topic['subtopic'])
        
        # 根据内容提取额外关键词
        content = topic['content'].lower()
        
        # 常见的Android逆向关键词
        keywords = [
            'apk', 'dex', 'smali', 'dalvik', 'art', 'hook', 'frida', 
            'xposed', 'root', 'adb', 'jadx', 'apktool', 'oat', 'jit', 'aot',
            '脱壳', '反调试', '混淆', '加固', '逆向', '分析'
        ]
        
        for keyword in keywords:
            if keyword in content and keyword not in key_points:
                key_points.append(keyword)
                if len(key_points) >= 5:  # 限制关键点数量
                    break
        
        return key_points[:5]  # 最多返回5个关键点

    def save_questions_to_html(self, questions: list, output_file: str):
        """保存面试题为HTML格式"""
        # 统计题目难度分布
        basic_count = len([q for q in questions if q.get('difficulty') == '基础'])
        intermediate_count = len([q for q in questions if q.get('difficulty') == '中级']) 
        advanced_count = len([q for q in questions if q.get('difficulty') == '高级'])
        
        # 生成HTML内容
        html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Android 逆向工程模拟面试题</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #f5f5f5; }}
        .container {{ background: white; border-radius: 10px; padding: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 30px; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 8px; }}
        .stats {{ display: flex; justify-content: center; gap: 20px; margin-top: 15px; }}
        .stat-item {{ text-align: center; }}
        .stat-number {{ font-size: 1.5em; font-weight: bold; display: block; }}
        .question-card {{ border: 1px solid #e0e0e0; margin-bottom: 20px; border-radius: 8px; overflow: hidden; }}
        .question-header {{ padding: 15px; background: #f8f9fa; }}
        .question-meta {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }}
        .question-text {{ font-weight: bold; margin-bottom: 10px; }}
        .key-points {{ color: #666; font-size: 0.9em; }}
        .answer-section {{ padding: 15px; display: none; background: #f0f8ff; border-top: 1px solid #e0e0e0; }}
        .show-answer-btn {{ width: 100%; padding: 12px; background: #007bff; color: white; border: none; cursor: pointer; font-size: 1em; }}
        .show-answer-btn:hover {{ background: #0056b3; }}
        .show-answer-btn.active {{ background: #dc3545; }}
        .difficulty {{ padding: 4px 8px; border-radius: 12px; font-size: 0.8em; font-weight: bold; }}
        .difficulty-基础 {{ background: #d4edda; color: #155724; }}
        .difficulty-中级 {{ background: #fff3cd; color: #856404; }}
        .difficulty-高级 {{ background: #f8d7da; color: #721c24; }}
        .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 0.9em; }}
        @media (max-width: 768px) {{ body {{ padding: 10px; }} .stats {{ flex-direction: column; gap: 10px; }} }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Android 逆向工程模拟面试题</h1>
            <div class="stats">
                <div class="stat-item">
                    <span class="stat-number">{len(questions)}</span>
                    <span>总题数</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{basic_count}</span>
                    <span>基础题</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{intermediate_count}</span>
                    <span>中级题</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{advanced_count}</span>
                    <span>高级题</span>
                </div>
            </div>
        </div>
        
        <div class="questions">'''

        # 添加问题
        for i, q in enumerate(questions, 1):
            key_points = ", ".join(q.get('key_points', [])) if q.get('key_points') else "无"
            difficulty = q.get('difficulty', '基础')
            category = q.get('category', '综合')
            
            # 安全处理HTML内容
            question_text = q.get('question', '').replace('<', '&lt;').replace('>', '&gt;')
            answer_text = q.get('answer', '暂无答案').replace('<', '&lt;').replace('>', '&gt;')
            
            html_content += f'''
            <div class="question-card">
                <div class="question-header">
                    <div class="question-meta">
                        <div>
                            <span style="color: #007bff; font-weight: bold;">题目 {i}</span>
                            <span style="background: #e9ecef; color: #495057; padding: 2px 6px; border-radius: 10px; font-size: 0.8em; margin-left: 8px;">{category}</span>
                        </div>
                        <span class="difficulty difficulty-{difficulty}">{difficulty}</span>
                    </div>
                    <div class="question-text">{question_text}</div>
                    <div class="key-points"><strong>考查要点:</strong> {key_points}</div>
                </div>
                <div class="answer-section" id="answer-{i}">
                    <h4 style="color: #007bff; margin-bottom: 10px;">📝 参考答案</h4>
                    <div style="white-space: pre-line; line-height: 1.6;">{answer_text}</div>
                </div>
                <button class="show-answer-btn" id="btn-{i}" onclick="toggleAnswer({i})">👁️ 查看答案</button>
            </div>'''

        html_content += '''
        </div>
        
        <div class="footer">
            💡 提示：先独立思考答案，再点击查看参考答案进行对比学习<br>
            快捷键：按 H 隐藏所有答案，按 S 显示所有答案
        </div>
    </div>
    
    <script>
        function toggleAnswer(id) {
            const answer = document.getElementById('answer-' + id);
            const btn = document.getElementById('btn-' + id);
            if (answer.style.display === 'none' || !answer.style.display) {
                answer.style.display = 'block';
                btn.textContent = '🙈 隐藏答案';
                btn.classList.add('active');
            } else {
                answer.style.display = 'none';
                btn.textContent = '👁️ 查看答案';
                btn.classList.remove('active');
            }
        }
        
        document.addEventListener('keydown', function(e) {
            if (e.key === 'h') {
                document.querySelectorAll('.answer-section').forEach(section => {
                    section.style.display = 'none';
                });
                document.querySelectorAll('.show-answer-btn').forEach(btn => {
                    btn.textContent = '👁️ 查看答案';
                    btn.classList.remove('active');
                });
            } else if (e.key === 's') {
                document.querySelectorAll('.answer-section').forEach(section => {
                    section.style.display = 'block';
                });
                document.querySelectorAll('.show-answer-btn').forEach(btn => {
                    btn.textContent = '🙈 隐藏答案';
                    btn.classList.add('active');
                });
            }
        });
    </script>
</body>
</html>'''

        # 写入HTML文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

    def save_questions_to_file(self, questions: list, output_file: str, format_type: str = "json"):
        """保存面试题到文件"""
        if format_type.lower() == "html":
            self.save_questions_to_html(questions, output_file)
        else:
            output_data = {
                "generated_at": str(Path(__file__).parent),
                "total_questions": len(questions),
                "questions": questions
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"Interview questions saved to: {output_file}")

    def display_questions(self, questions: list):
        """在控制台显示面试题"""
        print("\n" + "="*60)
        print("🎯 Android 逆向工程模拟面试题")
        print("="*60)
        
        for i, q in enumerate(questions, 1):
            print(f"\n【题目 {i}】({q.get('difficulty', '未知')}) - {q.get('category', '综合')}")
            print("-" * 50)
            print(f"问题: {q['question']}")
            
            if 'key_points' in q and q['key_points']:
                print(f"考查要点: {', '.join(q['key_points'])}")
            
            print()

    def run(self, memo_file: str = None, num_questions: int = 10, output_file: str = None, format_type: str = "html"):
        """运行面试题生成器"""
        
        # 选择memo文件
        if memo_file:
            selected_file = Path(memo_file)
            if not selected_file.exists():
                print(f"Error: File {memo_file} not found")
                return
        else:
            # 随机选择一个memo文件
            selected_file = random.choice(self.memo_files)
        
        print(f"📚 选择文档: {selected_file.name}")
        
        # 读取内容
        content = self.read_memo_content(selected_file)
        if not content:
            print("Error: Could not read memo content")
            return
        
        # 提取面试话题
        topics = self.extract_interview_topics(content)
        print(f"🔍 提取到 {len(topics)} 个面试话题")
        
        if not topics:
            print("Warning: No interview topics extracted from content")
            return
        
        # 显示提取的话题
        print("📋 提取的话题包括:")
        for i, topic in enumerate(topics[:5], 1):  # 显示前5个话题
            subtopic_info = f" - {topic['subtopic']}" if topic['subtopic'] else ""
            print(f"  {i}. {topic['main_topic']}{subtopic_info} ({topic['difficulty']}, {topic['question_type']})")
        if len(topics) > 5:
            print(f"  ... 还有 {len(topics) - 5} 个话题")
        
        # 生成面试题和答案
        print(f"🚀 正在生成 {num_questions} 个面试题...")
        questions = self.generate_questions_from_topics(topics, num_questions)
        
        if not questions:
            print("Error: Failed to generate questions")
            return
        
        # 只有在非HTML格式时才在控制台显示题目
        if format_type.lower() != "html":
            self.display_questions(questions)
        
        # 保存到文件
        if output_file:
            # 如果是HTML格式且用户没有指定完整路径，则放到interviews目录
            if format_type.lower() == "html" and not Path(output_file).is_absolute():
                output_path = self.interviews_dir / output_file
            else:
                output_path = Path(output_file)
            self.save_questions_to_file(questions, str(output_path), format_type)
        else:
            # 自动生成文件名
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            extension = "html" if format_type.lower() == "html" else "json"
            
            if format_type.lower() == "html":
                # HTML文件保存到interviews目录
                default_output = self.interviews_dir / f"interview_questions_{selected_file.stem}_{timestamp}.{extension}"
            else:
                # JSON文件保存到项目根目录
                default_output = self.project_root / f"interview_questions_{selected_file.stem}_{timestamp}.{extension}"
            
            self.save_questions_to_file(questions, str(default_output), format_type)
        
        if format_type.lower() == "html":
            print(f"✅ HTML面试题已生成! 请在浏览器中打开查看")
            print(f"💡 快捷键: 按 H 隐藏所有答案, 按 S 显示所有答案")

def main():
    parser = argparse.ArgumentParser(description="Android逆向工程模拟面试题生成器")
    parser.add_argument("-f", "--file", help="指定memo文件路径（不指定则随机选择）")
    parser.add_argument("-n", "--num", type=int, default=10, help="生成题目数量（默认10）")
    parser.add_argument("-o", "--output", help="输出文件路径")
    parser.add_argument("-t", "--format", choices=["html", "json"], default="html", 
                       help="输出格式：html（默认）或 json")
    
    args = parser.parse_args()
    
    try:
        generator = InterviewGenerator()
        generator.run(
            memo_file=args.file,
            num_questions=args.num,
            output_file=args.output,
            format_type=args.format
        )
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())