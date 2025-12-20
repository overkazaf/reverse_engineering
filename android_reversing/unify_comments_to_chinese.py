#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一代码块注释为中文
处理 01-Recipes 目录下所有 md 文件中的代码注释
"""

import os
import re
import glob

class CommentUnifier:
    """统一代码注释为中文"""

    def __init__(self):
        # 英文到中文的翻译映射
        self.en_to_zh = {
            # 常见的代码注释用语
            'Hook': '拦截',
            'Bypass': '绕过',
            'Detection': '检测',
            'Check': '检查',
            'Start': '开始',
            'End': '结束',
            'Initialize': '初始化',
            'Setup': '设置',
            'Config': '配置',
            'Setting': '设置',
            'Function': '函数',
            'Method': '方法',
            'Class': '类',
            'Variable': '变量',
            'Parameter': '参数',
            'Return': '返回',
            'Call': '调用',
            'Modify': '修改',
            'Replace': '替换',
            'Add': '添加',
            'Remove': '删除',
            'Delete': '删除',
            'Update': '更新',
            'Create': '创建',
            'Load': '加载',
            'Save': '保存',
            'Read': '读取',
            'Write': '写入',
            'Get': '获取',
            'Set': '设置',
            'Parse': '解析',
            'Process': '处理',
            'Handle': '处理',
            'Generate': '生成',
            'Build': '构建',
            'Compile': '编译',
            'Execute': '执行',
            'Run': '运行',
            'Test': '测试',
            'Debug': '调试',
            'Log': '日志',
            'Print': '打印',
            'Output': '输出',
            'Input': '输入',
            'File': '文件',
            'Path': '路径',
            'Directory': '目录',
            'Folder': '文件夹',
            'Data': '数据',
            'String': '字符串',
            'Number': '数字',
            'Integer': '整数',
            'Array': '数组',
            'List': '列表',
            'Object': '对象',
            'Instance': '实例',
            'Error': '错误',
            'Exception': '异常',
            'Success': '成功',
            'Failed': '失败',
            'True': '真',
            'False': '假',
            'Null': '空',
            'Empty': '空',
            'Valid': '有效',
            'Invalid': '无效',
            'Enabled': '启用',
            'Disabled': '禁用',
            'Active': '激活',
            'Inactive': '未激活',
            'Open': '打开',
            'Close': '关闭',
            'Connect': '连接',
            'Disconnect': '断开连接',
            'Send': '发送',
            'Receive': '接收',
            'Request': '请求',
            'Response': '响应',
            'Server': '服务器',
            'Client': '客户端',
            'Network': '网络',
            'Port': '端口',
            'Address': '地址',
            'Host': '主机',
            'URL': '地址',
            'API': '接口',
            'Protocol': '协议',
            'Header': '头部',
            'Body': '主体',
            'Payload': '载荷',
            'Query': '查询',
            'Filter': '过滤',
            'Sort': '排序',
            'Search': '搜索',
            'Find': '查找',
            'Match': '匹配',
            'Found': '找到',
            'Not found': '未找到',
            'Usage': '用法',
            'Example': '示例',
            'Sample': '样例',
            'Demo': '演示',
            'Note': '注意',
            'Warning': '警告',
            'Important': '重要',
            'Recommended': '推荐',
            'Optional': '可选',
            'Required': '必需',
            'Default': '默认',
            'Custom': '自定义',
            'Auto': '自动',
            'Manual': '手动',
            'Step': '步骤',
            'First': '首先',
            'Then': '然后',
            'Next': '接下来',
            'Finally': '最后',
            'Before': '之前',
            'After': '之后',
            'Wait for': '等待',
            'Timeout': '超时',
            'Retry': '重试',
            'Complete': '完成',
            'Done': '完成',
            'Finished': '完成',
            'Pending': '待处理',
            'Running': '运行中',
            'Stopped': '已停止',
            'Paused': '已暂停',
            'Resumed': '已恢复',
            'Intercepted': '已拦截',
            'Caught': '捕获',
            'Detected': '检测到',
            'Hidden': '隐藏',
            'Shown': '显示',
            'Visible': '可见',
            'Invisible': '不可见',
            'Target': '目标',
            'Source': '源',
            'Destination': '目的地',
            'Original': '原始',
            'Modified': '已修改',
            'New': '新',
            'Old': '旧',
            'Current': '当前',
            'Previous': '之前',
            'Dump': '导出',
            'Export': '导出',
            'Import': '导入',
            'Backup': '备份',
            'Restore': '恢复',
            'Copy': '复制',
            'Move': '移动',
            'Rename': '重命名',
            'Convert': '转换',
            'Encode': '编码',
            'Decode': '解码',
            'Encrypt': '加密',
            'Decrypt': '解密',
            'Compress': '压缩',
            'Decompress': '解压',
            'Extract': '提取',
            'Parse': '解析',
            'Validate': '验证',
            'Verify': '验证',
            'Ensure': '确保',
            'Allow': '允许',
            'Deny': '拒绝',
            'Grant': '授予',
            'Revoke': '撤销',
            'Permission': '权限',
            'Access': '访问',
            'Denied': '被拒绝',
            'Granted': '已授予',
            'Attempt': '尝试',
            'Try': '尝试',
            'Catch': '捕获',
            'Throw': '抛出',
            'Raise': '抛出',
            'Ignore': '忽略',
            'Skip': '跳过',
            'Continue': '继续',
            'Break': '中断',
            'Exit': '退出',
            'Quit': '退出',
            'Abort': '中止',
            'Cancel': '取消',
            'Confirm': '确认',
            'Prompt': '提示',
            'Message': '消息',
            'Notification': '通知',
            'Alert': '警报',
            'Info': '信息',
            'Status': '状态',
            'Result': '结果',
            'Value': '值',
            'Size': '大小',
            'Length': '长度',
            'Count': '计数',
            'Total': '总计',
            'Sum': '总和',
            'Average': '平均',
            'Min': '最小',
            'Max': '最大',
            'Index': '索引',
            'Position': '位置',
            'Offset': '偏移',
            'Buffer': '缓冲区',
            'Cache': '缓存',
            'Memory': '内存',
            'Storage': '存储',
            'Database': '数据库',
            'Table': '表',
            'Record': '记录',
            'Field': '字段',
            'Column': '列',
            'Row': '行',
            'Key': '键',
            'Map': '映射',
            'Set': '集合',
            'Collection': '集合',
            'Container': '容器',
            'Wrapper': '包装器',
            'Handler': '处理器',
            'Manager': '管理器',
            'Controller': '控制器',
            'Service': '服务',
            'Provider': '提供者',
            'Consumer': '消费者',
            'Producer': '生产者',
            'Worker': '工作进程',
            'Thread': '线程',
            'Process': '进程',
            'Task': '任务',
            'Job': '作业',
            'Queue': '队列',
            'Stack': '堆栈',
            'Heap': '堆',
            'Pool': '池',
            'Factory': '工厂',
            'Builder': '构建器',
            'Adapter': '适配器',
            'Bridge': '桥接器',
            'Proxy': '代理',
            'Singleton': '单例',
            'Observer': '观察者',
            'Listener': '监听器',
            'Callback': '回调',
            'Event': '事件',
            'Trigger': '触发器',
            'Signal': '信号',
            'Flag': '标志',
            'Option': '选项',
            'Setting': '设置',
            'Preference': '偏好',
            'Property': '属性',
            'Attribute': '属性',
            'Feature': '特性',
            'Capability': '能力',
            'Support': '支持',
            'Compatible': '兼容',
            'Incompatible': '不兼容',
            'Available': '可用',
            'Unavailable': '不可用',
            'Ready': '就绪',
            'Busy': '忙碌',
            'Idle': '空闲',
            'Online': '在线',
            'Offline': '离线',
            'Connected': '已连接',
            'Disconnected': '已断开',
            'Initialized': '已初始化',
            'Uninitialized': '未初始化',
            'Loaded': '已加载',
            'Unloaded': '未加载',
            'Registered': '已注册',
            'Unregistered': '未注册',
            'Installed': '已安装',
            'Uninstalled': '未安装',
            'Activated': '已激活',
            'Deactivated': '已停用',
            'Started': '已启动',
            'Locked': '已锁定',
            'Unlocked': '已解锁',
            'Blocked': '已阻止',
            'Allowed': '已允许',
            'Authenticated': '已认证',
            'Unauthenticated': '未认证',
            'Authorized': '已授权',
            'Unauthorized': '未授权',
            'Secure': '安全',
            'Insecure': '不安全',
            'Public': '公开',
            'Private': '私有',
            'Protected': '受保护',
            'Internal': '内部',
            'External': '外部',
            'Local': '本地',
            'Remote': '远程',
            'Global': '全局',
            'Static': '静态',
            'Dynamic': '动态',
            'Constant': '常量',
            'Temporary': '临时',
            'Permanent': '永久',
            'Volatile': '易失',
            'Stable': '稳定',
            'Unstable': '不稳定',
            'Deprecated': '已弃用',
            'Obsolete': '已废弃',
            'Legacy': '遗留',
            'Experimental': '实验性',
            'Beta': '测试版',
            'Alpha': '内测版',
            'Release': '发布',
            'Version': '版本',
            'Revision': '修订',
            'Build': '构建',
            'Patch': '补丁',
            'Update': '更新',
            'Upgrade': '升级',
            'Downgrade': '降级',
            'Migration': '迁移',
            'Conversion': '转换',
            'Transformation': '转换',
            'Translation': '翻译',
            'Localization': '本地化',
            'Internationalization': '国际化',
            'Format': '格式',
            'Type': '类型',
            'Kind': '种类',
            'Category': '类别',
            'Group': '组',
            'Tag': '标签',
            'Label': '标签',
            'Name': '名称',
            'Title': '标题',
            'Description': '描述',
            'Comment': '注释',
            'Documentation': '文档',
            'Reference': '参考',
            'Link': '链接',
            'Pointer': '指针',
            'Symbol': '符号',
            'Token': '令牌',
            'Identifier': '标识符',
            'Keyword': '关键字',
            'Reserved': '保留',
            'Special': '特殊',
            'Generic': '通用',
            'Specific': '特定',
            'General': '一般',
            'Particular': '特别',
            'Unique': '唯一',
            'Duplicate': '重复',
            'Distinct': '不同',
            'Same': '相同',
            'Different': '不同',
            'Equal': '相等',
            'Unequal': '不相等',
            'Greater': '更大',
            'Less': '更小',
            'Above': '以上',
            'Below': '以下',
            'Higher': '更高',
            'Lower': '更低',
            'Top': '顶部',
            'Bottom': '底部',
            'Left': '左',
            'Right': '右',
            'Front': '前',
            'Back': '后',
            'Forward': '向前',
            'Backward': '向后',
            'Up': '向上',
            'Down': '向下',
            'In': '在内',
            'Out': '在外',
            'Inside': '内部',
            'Outside': '外部',
            'Inner': '内部',
            'Outer': '外部',
            'Near': '附近',
            'Far': '远处',
            'Close': '接近',
            'Distant': '遥远',
            'Adjacent': '相邻',
            'Neighbor': '邻居',
            'Parent': '父',
            'Child': '子',
            'Sibling': '兄弟',
            'Ancestor': '祖先',
            'Descendant': '后代',
            'Root': '根',
            'Leaf': '叶',
            'Node': '节点',
            'Edge': '边',
            'Graph': '图',
            'Tree': '树',
            'Branch': '分支',
            'Trunk': '主干',
            'Path': '路径',
            'Route': '路由',
            'Chain': '链',
            'Link': '链接',
            'Connection': '连接',
            'Relation': '关系',
            'Association': '关联',
            'Dependency': '依赖',
            'Reference': '引用',
            'Usage': '用法',
        }

    def is_chinese(self, text):
        """检测文本是否包含中文"""
        return bool(re.search(r'[\u4e00-\u9fff]', text))

    def is_english(self, text):
        """检测文本是否包含英文"""
        return bool(re.search(r'[a-zA-Z]', text))

    def is_mixed(self, text):
        """检测文本是否中英文混杂"""
        return self.is_chinese(text) and self.is_english(text)

    def translate_to_chinese(self, text):
        """将英文术语翻译成中文"""
        result = text
        # 按长度排序（最长的优先），避免部分替换
        for en, zh in sorted(self.en_to_zh.items(), key=lambda x: len(x[0]), reverse=True):
            # 使用单词边界匹配，避免替换单词的一部分
            result = re.sub(r'\b' + re.escape(en) + r'\b', zh, result, flags=re.IGNORECASE)
        return result

    def unify_comment(self, line):
        """统一注释为中文"""
        original = line.rstrip('\n')

        # 匹配 // 注释
        match = re.match(r'^(\s*//\s*)(.+)$', original)
        if match:
            prefix = match.group(1)
            comment = match.group(2).strip()
            if self.is_mixed(comment):
                # 如果是中英文混杂，翻译英文部分为中文
                unified = self.translate_to_chinese(comment)
                return prefix + unified + '\n'

        # 匹配 # 注释
        match = re.match(r'^(\s*#\s*)(.+)$', original)
        if match:
            prefix = match.group(1)
            comment = match.group(2).strip()
            if self.is_mixed(comment):
                # 如果是中英文混杂，翻译英文部分为中文
                unified = self.translate_to_chinese(comment)
                return prefix + unified + '\n'

        # 行内注释
        match = re.match(r'(.+?)(//|#)(\s*)(.+)$', original)
        if match:
            code = match.group(1)
            marker = match.group(2)
            space = match.group(3)
            comment = match.group(4).strip()
            if self.is_mixed(comment):
                unified = self.translate_to_chinese(comment)
                return code + marker + space + unified + '\n'

        return line

    def process_file(self, file_path):
        """处理单个 markdown 文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            modified = False
            new_lines = []
            in_code_block = False

            for line in lines:
                if line.strip().startswith('```'):
                    in_code_block = not in_code_block
                    new_lines.append(line)
                elif in_code_block:
                    unified = self.unify_comment(line)
                    if unified != line:
                        modified = True
                        new_lines.append(unified)
                    else:
                        new_lines.append(line)
                else:
                    new_lines.append(line)

            if modified:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
                return True
            return False

        except Exception as e:
            print(f"❌ 处理文件失败 {file_path}: {e}")
            return False

def main():
    """主函数"""
    unifier = CommentUnifier()

    # 获取 01-Recipes 目录下所有 md 文件
    recipe_files = glob.glob('docs/01-Recipes/**/*.md', recursive=True)

    print("🚀 开始统一 01-Recipes 目录下的代码注释为中文...\n")
    print("=" * 70)

    processed = 0
    modified = 0

    for file_path in sorted(recipe_files):
        print(f"\n📄 处理: {file_path}")
        if unifier.process_file(file_path):
            print(f"   ✅ 已统一")
            modified += 1
        else:
            print(f"   ⏭️  无需修改")
        processed += 1

    print("\n" + "=" * 70)
    print(f"🎉 处理完成!")
    print(f"   📊 处理文件: {processed}")
    print(f"   ✅ 修改文件: {modified}")
    print(f"   ⏭️  跳过文件: {processed - modified}")
    print("=" * 70)

if __name__ == "__main__":
    main()
