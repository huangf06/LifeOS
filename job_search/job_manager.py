#!/usr/bin/env python3
"""
求职管理系统 - 统一入口
"""

import argparse
import sys
from pathlib import Path
import subprocess
import webbrowser
import os

def main():
    parser = argparse.ArgumentParser(description="求职管理系统统一入口")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # 生成简历
    resume_parser = subparsers.add_parser("resume", help="简历管理")
    resume_parser.add_argument("--company", required=True, help="目标公司")
    resume_parser.add_argument("--position", required=True, help="职位名称")
    resume_parser.add_argument("--pdf", action="store_true", help="同时生成PDF")

    # 申请管理
    app_parser = subparsers.add_parser("apply", help="申请管理")
    app_subparsers = app_parser.add_subparsers(dest="app_action")
    
    # 添加申请
    add_app_parser = app_subparsers.add_parser("add", help="添加申请")
    add_app_parser.add_argument("--company", required=True)
    add_app_parser.add_argument("--position", required=True)
    add_app_parser.add_argument("--salary")
    add_app_parser.add_argument("--notes")

    # 更新申请状态
    update_app_parser = app_subparsers.add_parser("update", help="更新申请")
    update_app_parser.add_argument("--id", required=True)
    update_app_parser.add_argument("--status", required=True)
    update_app_parser.add_argument("--notes")

    # 查看申请
    app_subparsers.add_parser("list", help="查看申请列表")
    app_subparsers.add_parser("summary", help="查看申请统计")

    # 职位管理
    job_parser = subparsers.add_parser("jobs", help="职位管理")
    job_subparsers = job_parser.add_subparsers(dest="job_action")
    
    add_job_parser = job_subparsers.add_parser("add", help="添加职位")
    add_job_parser.add_argument("--company", required=True)
    add_job_parser.add_argument("--title", required=True)
    add_job_parser.add_argument("--salary")
    add_job_parser.add_argument("--url")

    search_job_parser = job_subparsers.add_parser("search", help="搜索职位")
    search_job_parser.add_argument("--keyword")
    search_job_parser.add_argument("--company")

    job_subparsers.add_parser("analyze", help="分析职位市场")

    # 仪表盘
    subparsers.add_parser("dashboard", help="打开仪表盘")

    # 初始化系统
    subparsers.add_parser("init", help="初始化求职管理系统")

    # 帮助
    subparsers.add_parser("help", help="显示详细帮助")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # 确保在正确的目录
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    if args.command == "resume":
        cmd = ["python", "scripts/resume_generator.py", 
               "--company", args.company, "--position", args.position]
        if args.pdf:
            cmd.append("--pdf")
        subprocess.run(cmd)

    elif args.command == "apply":
        if args.app_action == "add":
            cmd = ["python", "scripts/application_tracker.py", "add",
                   "--company", args.company, "--position", args.position]
            if args.salary:
                cmd.extend(["--salary", args.salary])
            if args.notes:
                cmd.extend(["--notes", args.notes])
            subprocess.run(cmd)
        
        elif args.app_action == "update":
            cmd = ["python", "scripts/application_tracker.py", "update",
                   "--id", args.id, "--status", args.status]
            if args.notes:
                cmd.extend(["--notes", args.notes])
            subprocess.run(cmd)
        
        elif args.app_action == "list":
            subprocess.run(["python", "scripts/application_tracker.py", "list"])
        
        elif args.app_action == "summary":
            subprocess.run(["python", "scripts/application_tracker.py", "summary"])

    elif args.command == "jobs":
        if args.job_action == "add":
            cmd = ["python", "scripts/job_scraper.py", "add",
                   "--company", args.company, "--title", args.title]
            if args.salary:
                cmd.extend(["--salary", args.salary])
            if args.url:
                cmd.extend(["--url", args.url])
            subprocess.run(cmd)
        
        elif args.job_action == "search":
            cmd = ["python", "scripts/job_scraper.py", "search"]
            if args.keyword:
                cmd.extend(["--keyword", args.keyword])
            if args.company:
                cmd.extend(["--company", args.company])
            subprocess.run(cmd)
        
        elif args.job_action == "analyze":
            subprocess.run(["python", "scripts/job_scraper.py", "analyze"])

    elif args.command == "dashboard":
        dashboard_path = script_dir / "dashboard" / "index.html"
        if dashboard_path.exists():
            webbrowser.open(f"file://{dashboard_path.absolute()}")
            print(f"✅ Dashboard opened in browser: {dashboard_path}")
        else:
            print("❌ Dashboard file not found")

    elif args.command == "init":
        print("🚀 初始化求职管理系统...")
        
        # 检查目录结构
        required_dirs = ["config", "resumes/templates", "resumes/versions", "resumes/output",
                        "applications", "job_data", "scripts", "dashboard"]
        
        for dir_path in required_dirs:
            full_path = script_dir / dir_path
            if not full_path.exists():
                full_path.mkdir(parents=True, exist_ok=True)
                print(f"  📁 Created directory: {dir_path}")
        
        # 检查配置文件
        config_file = script_dir / "config" / "settings.json"
        if not config_file.exists():
            print("  ⚠️  Configuration file missing. Please edit config/settings.json")
        
        print("✅ 系统初始化完成!")
        print("\\n📖 快速开始:")
        print("  1. 编辑 config/settings.json 设置个人信息")
        print("  2. 生成简历: python job_manager.py resume --company 'IMC Trading' --position 'Quantitative Researcher' --pdf")
        print("  3. 添加申请: python job_manager.py apply add --company 'IMC Trading' --position 'Quantitative Researcher'")
        print("  4. 查看仪表盘: python job_manager.py dashboard")

    elif args.command == "help":
        print("""
🎯 求职管理系统使用指南

📝 简历管理:
  python job_manager.py resume --company "IMC Trading" --position "Quantitative Researcher" --pdf
  
📋 申请管理:
  python job_manager.py apply add --company "IMC Trading" --position "量化研究员" --salary "€80-120k"
  python job_manager.py apply update --id abc123 --status "interview_scheduled"
  python job_manager.py apply list
  python job_manager.py apply summary

💼 职位管理:
  python job_manager.py jobs add --company "Optiver" --title "Quant Trader" --salary "€90-130k"
  python job_manager.py jobs search --keyword "quantitative"
  python job_manager.py jobs analyze

📊 仪表盘:
  python job_manager.py dashboard

🔧 系统管理:
  python job_manager.py init    # 初始化系统
  python job_manager.py help    # 显示帮助

📁 文件结构:
  config/settings.json          # 个人信息配置
  resumes/versions/             # 生成的简历版本
  applications/tracker.json     # 申请追踪数据
  job_data/scraped_jobs.json    # 收集的职位信息
        """)

if __name__ == "__main__":
    main()