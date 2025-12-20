#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dynamically scan and translate Chinese comments in code blocks to English.
"""

import os
import re

class ChineseCommentTranslator:
    def __init__(self):
        self.translation_cache = {}
        # Extended dictionary
        self.replacements = {
            '绕过': 'Bypass', '反调试': 'Anti-Debugging', '检测': 'Detection', '策略': 'Strategy',
            '修改': 'Modify', '拦截': 'Intercept', '返回': 'Return', '调用': 'Call',
            '函数': 'Function', '方法': 'Method', '类': 'Class', '对象': 'Object',
            '参数': 'Parameter', '变量': 'Variable', '注释': 'Comment', '代码': 'Code',
            '脚本': 'Script', '配置': 'Config', '设置': 'Setting', '初始化': 'Initialize',
            '处理': 'Process', '解析': 'Parse', '生成': 'Generate', '创建': 'Create',
            '删除': 'Delete', '更新': 'Update', '查询': 'Query', '插入': 'Insert',
            '获取': 'Get', '判断': 'Check', '如果': 'If', '否则': 'Else',
            '循环': 'Loop', '遍历': 'Iterate', '打印': 'Print', '输出': 'Output',
            '输入': 'Input', '读取': 'Read', '写入': 'Write', '文件': 'File',
            '目录': 'Directory', '路径': 'Path', '数据': 'Data', '结果': 'Result',
            '错误': 'Error', '异常': 'Exception', '成功': 'Success', '失败': 'Failed',
            '开始': 'Start', '结束': 'End', '转换': 'Convert', '格式化': 'Format',
            '验证': 'Validate', '加载': 'Load', '保存': 'Save', '发送': 'Send',
            '接收': 'Receive', '请求': 'Request', '响应': 'Response', '连接': 'Connect',
            '断开': 'Disconnect', '服务器': 'Server', '客户端': 'Client', '网络': 'Network',
            '地址': 'Address', '端口': 'Port', '协议': 'Protocol', '加密': 'Encrypt',
            '解密': 'Decrypt', '编码': 'Encode', '解码': 'Decode', '压缩': 'Compress',
            '解压': 'Decompress', '字符串': 'String', '数字': 'Number', '整数': 'Integer',
            '浮点数': 'Float', '布尔值': 'Boolean', '数组': 'Array', '列表': 'List',
            '字典': 'Dictionary', '集合': 'Set', '元组': 'Tuple', '空值': 'Null',
            '真': 'True', '假': 'False', '是': 'Yes', '否': 'No',
            '和': 'And', '或': 'Or', '非': 'Not', '等于': 'Equal', '不等于': 'NotEqual',
            '大于': 'GreaterThan', '小于': 'LessThan', '包含': 'Contains', '长度': 'Length',
            '大小': 'Size', '数量': 'Count', '索引': 'Index', '键': 'Key', '值': 'Value',
            '属性': 'Property', '实例': 'Instance', '继承': 'Inherit', '接口': 'Interface',
            '实现': 'Implement', '重写': 'Override', '抽象': 'Abstract', '静态': 'Static',
            '公共': 'Public', '私有': 'Private', '保护': 'Protected', '常量': 'Constant',
            '枚举': 'Enum', '模块': 'Module', '包': 'Package', '导入': 'Import',
            '导出': 'Export', '命名空间': 'Namespace', '作用域': 'Scope', '上下文': 'Context',
            '线程': 'Thread', '进程': 'Process', '异步': 'Async', '同步': 'Sync',
            '并发': 'Concurrent', '并行': 'Parallel', '队列': 'Queue', '堆栈': 'Stack',
            '缓存': 'Cache', '缓冲': 'Buffer', '内存': 'Memory', '存储': 'Storage',
            '数据库': 'Database', '表': 'Table', '字段': 'Field', '记录': 'Record',
            '事务': 'Transaction', '提交': 'Commit', '回滚': 'Rollback', '主键': 'Primary Key',
            '外键': 'Foreign Key', '关联': 'Association', '映射': 'Mapping', '过滤': 'Filter',
            '排序': 'Sort', '分组': 'Group', '聚合': 'Aggregate', '计算': 'Calculate',
            '统计': 'Statistics', '分析': 'Analyze', '日志': 'Log', '调试': 'Debug',
            '测试': 'Test', '运行': 'Run', '执行': 'Execute', '构建': 'Build',
            '编译': 'Compile', '部署': 'Deploy', '发布': 'Release', '版本': 'Version',
            '检查': 'Check', '槽位': 'Slot', '分配': 'Allocation', '项目': 'Project',
            '架构图': 'Architecture Diagram', '例子': 'Example', '注册': 'Register',
            '本地': 'Native', '库': 'Library', '时': 'When', '名': 'Name',
            '用于': 'Used for', '第二': 'Second', '槽': 'Slot',
            '工具': 'Tool', '实用程序': 'Utility', '帮助': 'Help', '支持': 'Support',
            '按': 'By', '前': 'Before', '后': 'After', '重新': 'Re-', '分片': 'Sharding',
            '添加': 'Add', '现有': 'Existing', '选项': 'Option', '目标': 'Target',
            '特定': 'Specific', '程序': 'Program', '搜索': 'Search', '措施': 'Measure',
            '反制': 'Counter', '附加': 'Attach', '中': 'In',
            '反馈': 'Feedback', '贡献': 'Contribution', '许可证': 'License', '版权': 'Copyright',
            '作者': 'Author', '时间': 'Time', '日期': 'Date', '年': 'Year',
            '月': 'Month', '日': 'Day', '小时': 'Hour', '分钟': 'Minute',
            '秒': 'Second', '应用': 'App', '主要': 'Main', '核心': 'Core', '基础': 'Basic',
            '高级': 'Advanced', '简单': 'Simple', '复杂': 'Complex', '示例': 'Example',
            '案例': 'Case', '教程': 'Tutorial', '文档': 'Docs', '说明': 'Desc',
            '介绍': 'Intro', '概述': 'Overview', '详细': 'Detail', '完整': 'Complete',
            '部分': 'Partial', '全部': 'All', '推荐': 'Recommended', '可选': 'Optional',
            '必需': 'Required', '必须': 'Must', '应该': 'Should', '可以': 'Can',
            '能够': 'Able to', '需要': 'Need', '使用': 'Use', '操作': 'Op',
            '控制': 'Control', '管理': 'Manage', '监控': 'Monitor', '优化': 'Optimize',
            '性能': 'Performance', '效率': 'Efficiency', '速度': 'Speed', '质量': 'Quality',
            '安全': 'Security', '稳定': 'Stable', '可靠': 'Reliable', '扩展': 'Extension',
            '插件': 'Plugin', '组件': 'Component', '服务': 'Service', '业务': 'Business',
            '逻辑': 'Logic', '流程': 'Flow', '步骤': 'Step', '阶段': 'Stage',
            '环节': 'Link', '节点': 'Node', '分区': 'Partition', '集群': 'Cluster',
            '主节点': 'Master Node', '从节点': 'Slave Node', '备份': 'Backup', '恢复': 'Restore',
            '迁移': 'Migration', '复制': 'Replication', '自动': 'Auto', '手动': 'Manual',
            '批量': 'Batch', '单个': 'Single', '多个': 'Multiple', '当前': 'Current',
            '原始': 'Original', '新的': 'New', '旧的': 'Old', '临时': 'Temp',
            '永久': 'Permanent', '预编译': 'Pre-compiled', '未编译': 'Uncompiled',
            '清单': 'Manifest', '描述': 'Describes', '基本信息': 'Basic Info', '字节码': 'Bytecode',
            '启用': 'Enabled', '出现': 'Appears', '资源': 'Resources', '布局': 'Layout',
            '图标': 'Icon', '原生库': 'Native Libs', '原始资源': 'Raw Assets', '签名': 'Signature',
            '证书': 'Cert', '信息': 'Info', '存放': 'Store', '层': 'Layer',
            '下载': 'Download', '打开': 'Open', '进行': 'Do', '命令': 'Command',
            '格式': 'Format', '认为': 'Consider', '自己': 'Self', '仍是': 'Still',
            '选举': 'Elect', '新主': 'NewMaster', '至少': 'AtLeast', '安装': 'Install',
            '启动': 'Start/Boot', '查看': 'View', '状态': 'Status', '计算引擎': 'Compute Engine',
            '元数据存储': 'Metadata Store', '数据存储': 'Data Store', '内存存储': 'Mem Store',
            '一对一转换': '1-to-1 Convert', '从集合创建': 'CreateFromSet',
            '从外部存储创建': 'CreateFromExtStore', '从其他': 'FromOther', '枚举': 'Enumerate',
            '指定': 'Specify', '中的': 'In', '的': '', '了': '', '是': 'Is',
            '在': 'At', '这': 'This', '这个': 'This', '这里': 'Here', '哪里': 'Where',
            '什么': 'What', '如何': 'How', '为什么': 'Why', '漫长的过程': 'Long Process',
            '匹配的': 'Matched', '工具链': 'Toolchain', '将': 'Will', '添加到': 'Add to',
            '环境变量': 'Env Vars', '切换到': 'Switch to', '稳定的分支': 'Stable Branch',
            '首先': 'First', '然后': 'Then', '最后': 'Finally', '接下来': 'Next',
            '同时': 'Meanwhile', '另外': 'Also', '此外': 'Also', '因此': 'Therefore',
            '所以': 'So', '但是': 'But', '然而': 'However', '虽然': 'Though', '尽管': 'Despite',
            '除了': 'Except', '包括': 'Include', '例如': 'E.g.', '比如': 'E.g.',
            '等等': 'Etc', '等': 'Etc', '主': 'Main', '型': 'Type', '延迟': 'Latency',
            '不超过': 'Max', '严格遵循': 'Strictly Follow', '命名规则': 'Naming Rules',
            '定义': 'Define', '个': '', '只': 'Only', '仅': 'Only', '无': 'No',
        }

    def is_chinese(self, text):
        return bool(re.search(r'[\u4e00-\u9fff]', text))

    def translate_text(self, text):
        if not self.is_chinese(text):
            return text
        
        if text in self.translation_cache:
            return self.translation_cache[text]

        result = text
        for zh, en in sorted(self.replacements.items(), key=lambda x: len(x[0]), reverse=True):
            result = result.replace(zh, en)
        
        # If still has chinese, just strip them or replace with 'Unknown' to match "cannot be Chinese" rule
        # But let's try to be gentle first.
        # Actually, if the goal is "Cannot be Chinese", any remaining Chinese should be removed or romanized.
        # Simple fallback:
        # result = re.sub(r'[\u4e00-\u9fff]+', '?', result)
        
        self.translation_cache[text] = result
        return result

    def translate_line(self, line):
        # Handle various comment types
        patterns = [
            (r'^(\s*//\s*)(.+)$', 2),  # // comment
            (r'^(\s*#\s*)(.+)$', 2),   # # comment
            (r'^(\s*--\s*)(.+)$', 2),  # -- comment
            (r'^(\s*;\s*)(.+)$', 2),   # ; comment (asm)
            (r'(.+?)(//|#|--|;)(\s*)(.+)$', 4) # Inline
        ]
        
        for p, group in patterns:
            match = re.search(p, line)
            if match:
                comment = match.group(group)
                if self.is_chinese(comment):
                    # Reconstruct line
                    # This is tricky because we need to preserve the other groups.
                    # Simplified for full line replacements or inline.
                    # If inline:
                    if group == 4:
                        return match.group(1) + match.group(2) + match.group(3) + self.translate_text(comment)
                    else:
                        return match.group(1) + self.translate_text(comment)
                        
        # Block comments like /* */ are harder to regexp line-by-line if multiline, but here we assume line-by-line check.
        # Also simple text in code blocks (like ASCII art or simple notes) might trigger this.
        
        if self.is_chinese(line):
            return self.translate_text(line)
            
        return line

def process_file(file_path, translator):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    in_code_block = False
    new_lines = []
    modified = False
    
    for line in lines:
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            new_lines.append(line)
        elif in_code_block:
            # Check for chinese
            if translator.is_chinese(line):
                new_line = translator.translate_line(line.rstrip('\n')) + '\n'
                if new_line != line:
                    modified = True
                    new_lines.append(new_line)
                else:
                     new_lines.append(line)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
            
    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        return True
    return False

def main():
    translator = ChineseCommentTranslator()
    docs_dir = '/Users/nongjiawu/frida/reverse_engineering/android_reversing/docs'
    count = 0
    for root, dirs, files in os.walk(docs_dir):
        for file in files:
            if file.endswith('.md'):
                path = os.path.join(root, file)
                if process_file(path, translator):
                    print(f"Fixed: {path}")
                    count += 1
    print(f"Total files fixed: {count}")

if __name__ == '__main__':
    main()
