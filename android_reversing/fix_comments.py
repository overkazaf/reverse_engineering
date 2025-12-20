#!/usr/bin/env python3
"""
Batch fix unprofessional mixed Chinese-English comments in markdown files.
Convert them to professional English comments.
"""

import re
import os
from pathlib import Path

# Mapping of common mixed-language patterns to professional English
COMMENT_FIXES = {
    # Connection/Device related
    r'# ?(\d+\.? ?)?设备已?Connect': r'# \g<1>Verify device connection',
    r'# ?Connect设备': r'# Connect to device',
    r'# ?ValidateConnect': r'# Verify connection',
    r'# ?Connect到?(.+)': r'# Connect to \g<1>',
    r'# ?用 ?USB ?线?Connect设备到?电脑': r'# Connect device to PC via USB',
    r'# ?Connect?密度': r'# Connection density',
    r'PC and手机At同一': r'PC and phone on the same',
    r'and手机': r'and phone',

    # Download related
    r'# ?Download ?(.+?) ?\(免费\)': r'# Download \g<1> (free)',
    r'# ?Download(.+)': r'# Download\g<1>',
    r'# ?DownloadAnd(.+)': r'# Download and \g<1>',
    r'# ?Download与你': r'# Download matching your',
    r'# ?Download对应(.+)': r'# Download corresponding \g<1>',
    r'# ?Download内核源码': r'# Download kernel source',
    r'# ?Download最新': r'# Download latest',
    r'# ?Download通用': r'# Download universal',
    r'# ?OrDownload(.+)': r'# Or download\g<1>',
    r'# ?Re-Download(.+)': r'# Re-download\g<1>',
    r'# ?ManualDownload(.+)': r'# Manually download\g<1>',

    # Run/Execute related
    r'# ?Run$': r'# Run the command',
    r'# ?Run(.+)': r'# Run\g<1>',
    r'# ?RunAnd(.+)': r'# Run and \g<1>',
    r'# ?Run并View(.+)': r'# Run and view \g<1>',
    r'# ?正常?Run': r'# Running normally',
    r'# ?正At?Run': r'# Currently running',
    r'# ?IsNo?Run': r'# Check if running',
    r'# ?App?正At?Run': r'# App is running',
    r'# ?确保?App?正At?Run': r'# Ensure app is running',
    r'# ?Frida ?[Ss]erver? ?正At?Run': r'# Frida server is running',
    r'# ?Check.*IsNo?Run': r'# Check if running',
    r'# ?After台Run': r'# Run in background',
    r'# ?At.*Run': r'# Run in',
    r'# ?每天.*Run': r'# Run daily',
    r'# ?Use.*Run': r'# Use to run',
    r'# ?正常?Run(.*)': r'# Running\g<1>',

    # Record/Table related
    r'# ?Record ?(.+?) ?\(下文用 .+ Table示\)': r'# Record \g<1> (used below)',
    r'# ?Record(.+)': r'# Record\g<1>',
    r'# ?RecordFile(.+)': r'# Record file\g<1>',
    r'# ?RecordUse(.+)': r'# Record usage\g<1>',
    r'# ?RecordBeing': r'# Recorded',
    r'Table示': r'represents',
    r'Table': r'table',

    # At (在) related - location/position
    r'# ?At ?(.+?) ?In ?(.+)': r'# In \g<1>, \g<2>',
    r'# ?At(.+?)When': r'# When \g<1>',
    r'# ?AtApp(.+)': r'# In app\g<1>',
    r'# ?At容器In(.+)': r'# In container, \g<1>',
    r'# ?At设备上(.+)': r'# On device, \g<1>',
    r'# ?AtModule(.+)': r'# In module\g<1>',
    r'# ?At smali(.+)': r'# In smali\g<1>',
    r'# ?At SO(.+)': r'# In SO\g<1>',

    # And/Or related
    r'# ?PC And手机At同一': r'# PC and phone on the same',
    r'And(.+)': r'and\g<1>',
    r'Or者': r'or',
    r'Or': r'or',

    # Start/Boot related
    r'Start/Boot': r'startup',
    r'AtAppStart/BootWhen': r'at app startup',
    r'At App Start/BootBefore': r'before app startup',
    r'AppStart/BootAfter': r'after app starts',
    r'Start/BootWhen': r'at startup',

    # Attach/Hook modes
    r'# ?Attach ?模式': r'# Attach mode',
    r'# ?Spawn ?模式': r'# Spawn mode',
    r'# ?Hook ?正At?Run': r'# Hook running app',
    r'# ?Attach到?Process': r'# Attach to process',
    r'# ?Attach到?正At?Run': r'# Attach to running',

    # Check/Validate related
    r'# ?Check(.+?)IsNo(.+)': r'# Check if \g<1> is \g<2>',
    r'# ?CheckClass(.+)': r'# Check class\g<1>',
    r'# ?CheckFile(.+)': r'# Check file\g<1>',
    r'# ?Validate(.+)': r'# Verify\g<1>',
    r'IsNoRun': r'is running',
    r'IsNo存At': r'exists',

    # Configuration related
    r'# ?配置(.+)': r'# Configure\g<1>',
    r'# ?设置(.+)': r'# Set\g<1>',
    r'# ?启动(.+)': r'# Start\g<1>',
    r'环境变量?配置': r'environment variable configuration',
    r'Config?配置': r'configuration',
    r'RecommendedConfig': r'Recommended configuration',

    # List/View related
    r'# ?列出(.+)': r'# List\g<1>',
    r'# ?ViewTable(.+)': r'# View table\g<1>',
    r'# ?PrintConnect(.+)': r'# Print connected\g<1>',
    r'# ?View(.+)': r'# View\g<1>',
    r'RunProcess': r'running processes',

    # Permission/Authority related
    r'# ?赋予(.+)权限': r'# Grant \g<1> permission',
    r'Execute权限': r'execute permission',
    r'Manage员Run': r'run as administrator',

    # Time/Duration related
    r'Second内?At ?least': r'seconds with at least',
    r'Second内': r'seconds',
    r'LatencyMax': r'maximum delay',

    # Method/Operation related
    r'# ?Method ?\d+:': r'# Method \g<0>:',
    r'NeedAnalyze': r'to be analyzed',
    r'NeedSignature': r'requiring signature',
    r'NeedEncrypt': r'to be encrypted',

    # File/Directory related
    r'存At': r'exists at',
    r'# ?FindAt': r'# Find at',
    r'# ?File(.+)，Can': r'# File\g<1>, can',
    r'# ?得到一': r'# Get a',

    # Condition related
    r'# ?If(.+?)，Desc': r'# If \g<1>, indicates',
    r'# ?IfOriginal': r'# If original',
    r'# ?If指纹': r'# If fingerprint',

    # Network/Wi-Fi related
    r'Wi-Fi Network': r'Wi-Fi network',
    r'IP Address': r'IP address',

    # Package/Install related
    r'# ?打Package': r'# Package',
    r'# ?MustAt(.+)打Package': r'# Must package in \g<1>',
    r'# ?Install(.+)': r'# Install\g<1>',

    # Other common patterns
    r'# ?ThenAt(.+)': r'# Then in\g<1>',
    r'# ?ThenAttach': r'# Then attach',
    r'# ?Etc待': r'# Wait for',
    r'# ?Modify(.+)': r'# Modify\g<1>',
    r'# ?UseLXD(.+)': r'# Use LXD to \g<1>',
    r'# ?Create一': r'# Create a',
    r'它Table现': r'it behaves',
    r'Support(.+)Command': r'supports \g<1> command',
    r'架构(.+)': r'architecture\g<1>',
    r'Version一致': r'version matching',
    r'Pre-compiled(.*)Version': r'pre-compiled\g<1> version',
    r'Matched(.+)': r'matching \g<1>',
    r'对应Version': r'corresponding version',
    r'对应架构': r'corresponding architecture',
    r'Pass(.+)认证': r'pass \g<1> authentication',
    r'ProcessConnect超When': r'process connection timeout',
    r'# ?有些(.+)': r'# Some\g<1>',
    r'# ?False设': r'# Assume',
    r'Exception': r'anomaly',

    # Specific Chinese characters that got mixed
    r'Setting(.+)': r'settings\g<1>',
    r'Op\(': r'operation (',

    # Additional mixed patterns
    r'Create (.+?)规则(.+)': r'Create \g<1> rules\g<2>',
    r'规则File': r'rules file',
    r'Add以下内容': r'Add the following content',
    r'Re-Load规则': r'Reload rules',
    r'Load规则': r'Load rules',
    r'# ?Should(.+)': r'# Should\g<1>',
    r'下文用 (.+?) represents': r'used below as \g<1>',
    r'（下文用 (.+?)）': r'(used below as \g<1>)',

    # More specific patterns
    r'Should看到': r'Should see',
    r'Should显示': r'Should display',
    r'重命Name': r'rename',
    r'List设备': r'List devices',
    r'List所有': r'List all',
    r'Command行': r'command line',
    r'NeedRe-': r'Need to re-',
    r'If 提示': r'If shows',
    r'indicates没有': r'indicates no',
    r'Re-确认': r'Re-verify',
    r'View你': r'View your',
    r'View设备': r'View device',
    r'常见Output': r'Common output',
    r'Decompress并': r'Decompress and',
    r'推送到设备': r'push to device',
    r'赋予execute permission': r'grant execute permission',
    r'running processes': r'running processes',
    r'Class似Output': r'output like',
    r'当前Process': r'current process',
    r'IfNeed': r'if needed',
    r'Optional，': r'optional, ',
    r'方便Manage': r'easier to manage',
    r'ProcessList': r'process list',
    r'没有Root': r'no root',
    r'正确Output': r'correct output',

    # Mixed architecture/device terms
    r'architecture frida-server': r'architecture frida-server',
    r'你frida Version': r'your frida version',
    r'你设备': r'your device',

    # Verb + Chinese patterns
    r'View(.+?)架构': r'View \g<1> architecture',
    r'Check(.+?)Connect': r'Check \g<1> connection',
    r'Select(.+?)Version': r'Select \g<1> version',

    # Additional IsNo patterns
    r'Check ADB IsNoInstall': r'Check if ADB is installed',
    r'Check Python IsNoInstall': r'Check if Python is installed',
    r'Check(.+?)IsNoInstall': r'Check if \g<1> is installed',
    r'Check(.+?)IsNo(.+)': r'Check if \g<1> is \g<2>',

    # Display/output patterns
    r'Should display(.*)your': r'Should display \g<1>your',
    r'Should see(.*)output': r'Should see \g<1>output',
    r'displayyour': r'display your',
    r'seeoutput': r'see output',

    # List/Download patterns
    r'List all(.*)running': r'List all \g<1>running',
    r'allrunning': r'all running',
    r'Download对应architecture': r'Download corresponding architecture',
    r'Download matching your(.+)matching': r'Download matching your\g<1>',

    # View patterns
    r'View your frida Version': r'View your frida version',
    r'View  ': r'View ',

    # Permission/execute patterns
    r'grant execute permission并Run': r'grant execute permission and run',
    r'permission并': r'permission and',

    # Concatenated words
    r'Decompress and(.*)push': r'Decompress and \g<1>push',
    r'andpush': r'and push',
    r'andview': r'and view',
    r'并Run': r'and run',

    # Method/Hook patterns - fix the duplicate "Method" issue
    r'# Method # Method # Method # Method (\d+)::::': r'# Method \g<1>:',
    r'# Method (\d+):::': r'# Method \g<1>:',
    r'正AtRunApp': r'currently running app',
    r'AtAppstartupWhen注入': r'inject at app startup',

    # Setting/Target patterns
    r'Hook Setting完成': r'Hook setup complete',
    r'正在查找TargetClass': r'Looking for target class',
    r'现AtOpenSettingApp': r'now open the Settings app',
    r'TargetClass': r'target class',

    # Log/Call patterns
    r'Captured LogCall': r'Captured log call',
    r'CallOriginalMethod': r'Call original method',
    r'你第一 Frida Script': r'your first Frida script',

    # Connection/Check patterns
    r'Check  设备  connectionion': r'Check device connection',
    r'Check  (.+?)  connection': r'Check \g<1> connection',
    r'connectionion': r'connection',
    r'Check  设备': r'Check device',
    r'设备  connection': r'device connection',

    # Method/Hook patterns - fix remaining duplicates
    r'# Method # Method # Method (\d+):': r'# Method \g<1>:',
    r'# Method # Method (\d+)::': r'# Method \g<1>:',
    r'# Method (\d+)::': r'# Method \g<1>:',

    # Fix double spaces in comments
    r'display  your': r'display your',
    r'see  output': r'see output',
    r'all  running': r'all running',
    r'and  push': r'and push',
    r'View  device': r'View device',
    r'Should display  ': r'Should display ',
    r'Should see  ': r'Should see ',
    r'List all  ': r'List all ',
    r'  (\w)': r' \g<1>',  # Generic double space fix

    # Fix extra spaces in Download patterns
    r'Download matching your Python frida version  frida-server': r'Download frida-server matching your Python frida version',
    r'version  frida': r'version frida',

    # JavaScript comment patterns (// style)
    r'// (.+?)你第一(.+?)': r'// \g<1>your first\g<2>',
    r'// first_hook\.js - 你第一 Frida Script': r'// first_hook.js - your first Frida script',
}

def fix_comment(text):
    """Fix a single comment by applying all patterns."""
    for pattern, replacement in COMMENT_FIXES.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

def fix_file(file_path):
    """Fix all comments in a markdown file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Track if any changes were made
        original_content = content

        # Fix comments line by line
        lines = content.split('\n')
        fixed_lines = []
        changes_made = 0

        for line in lines:
            fixed_line = line
            # Fix lines that look like comments (bash # or JavaScript //)
            if re.search(r'(?:^|\s)#', line) or re.search(r'^\s*//', line):
                new_line = fix_comment(line)
                if new_line != line:
                    fixed_line = new_line
                    changes_made += 1
            fixed_lines.append(fixed_line)

        if changes_made > 0:
            content = '\n'.join(fixed_lines)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return changes_made
        return 0

    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return 0

def main():
    """Main function to fix all markdown files in docs directory."""
    docs_dir = Path('docs')
    total_files = 0
    total_changes = 0

    print("Fixing unprofessional comments in markdown files...")
    print("=" * 60)

    for md_file in docs_dir.rglob('*.md'):
        changes = fix_file(md_file)
        if changes > 0:
            total_files += 1
            total_changes += changes
            print(f"✓ {md_file.relative_to(docs_dir)}: {changes} comments fixed")

    print("=" * 60)
    print(f"Summary: Fixed {total_changes} comments in {total_files} files")

if __name__ == '__main__':
    main()
