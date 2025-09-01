#!/usr/bin/env python3
"""
求职申请追踪系统
"""

import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path

class ApplicationTracker:
    def __init__(self, tracker_file="./applications/tracker.json"):
        self.tracker_file = Path(__file__).parent.parent / tracker_file.lstrip('./')
        self.data = self.load_data()
    
    def load_data(self):
        """加载追踪数据"""
        if self.tracker_file.exists():
            with open(self.tracker_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {"applications": [], "metadata": {"total_applications": 0}}
    
    def save_data(self):
        """保存数据到文件"""
        self.data["metadata"]["last_updated"] = datetime.now().isoformat()
        self.data["metadata"]["total_applications"] = len(self.data["applications"])
        self.data["metadata"]["active_applications"] = len([
            app for app in self.data["applications"] 
            if app["status"] not in ["rejected", "withdrawn", "accepted"]
        ])
        
        with open(self.tracker_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
    
    def add_application(self, company, position, **kwargs):
        """添加新的申请记录"""
        app_id = str(uuid.uuid4())[:8]
        
        application = {
            "id": app_id,
            "company": company,
            "position": position,
            "application_date": kwargs.get("application_date", datetime.now().strftime("%Y-%m-%d")),
            "status": kwargs.get("status", "draft"),
            "priority": kwargs.get("priority", "medium"),
            "source": kwargs.get("source", "company_website"),
            "resume_version": kwargs.get("resume_version", ""),
            "cover_letter": kwargs.get("cover_letter", ""),
            "job_description": kwargs.get("job_description", ""),
            "salary_range": kwargs.get("salary_range", ""),
            "timeline": {
                "application_deadline": kwargs.get("deadline", ""),
                "expected_response": kwargs.get("expected_response", 
                    (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")),
                "interview_dates": []
            },
            "contacts": kwargs.get("contacts", []),
            "notes": kwargs.get("notes", ""),
            "feedback": "",
            "next_actions": kwargs.get("next_actions", "Wait for response"),
            "tags": kwargs.get("tags", []),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        self.data["applications"].append(application)
        self.save_data()
        print(f"✅ Added application: {company} - {position} (ID: {app_id})")
        return app_id
    
    def update_status(self, app_id, new_status, notes=""):
        """更新申请状态"""
        for app in self.data["applications"]:
            if app["id"] == app_id:
                old_status = app["status"]
                app["status"] = new_status
                app["updated_at"] = datetime.now().isoformat()
                if notes:
                    app["notes"] += f"\\n[{datetime.now().strftime('%Y-%m-%d')}] Status: {old_status} → {new_status}. {notes}"
                
                self.save_data()
                print(f"✅ Updated {app['company']} status: {old_status} → {new_status}")
                return True
        
        print(f"❌ Application ID {app_id} not found")
        return False
    
    def add_interview(self, app_id, interview_date, interview_type="", notes=""):
        """添加面试记录"""
        for app in self.data["applications"]:
            if app["id"] == app_id:
                interview_record = {
                    "date": interview_date,
                    "type": interview_type,
                    "notes": notes,
                    "added_at": datetime.now().isoformat()
                }
                app["timeline"]["interview_dates"].append(interview_record)
                app["status"] = "interview_scheduled"
                app["updated_at"] = datetime.now().isoformat()
                
                self.save_data()
                print(f"✅ Added interview for {app['company']} on {interview_date}")
                return True
        
        return False
    
    def get_applications(self, status=None, company=None):
        """获取申请列表"""
        apps = self.data["applications"]
        
        if status:
            apps = [app for app in apps if app["status"] == status]
        
        if company:
            apps = [app for app in apps if company.lower() in app["company"].lower()]
        
        return apps
    
    def get_summary(self):
        """获取申请统计摘要"""
        apps = self.data["applications"]
        status_counts = {}
        
        for app in apps:
            status = app["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "total_applications": len(apps),
            "status_breakdown": status_counts,
            "response_rate": self._calculate_response_rate(),
            "interview_rate": self._calculate_interview_rate(),
            "active_applications": len([app for app in apps if app["status"] not in ["rejected", "withdrawn", "accepted"]])
        }
    
    def _calculate_response_rate(self):
        """计算回复率"""
        submitted_apps = [app for app in self.data["applications"] if app["status"] != "draft"]
        if not submitted_apps:
            return 0.0
        
        responded_apps = [app for app in submitted_apps if app["status"] not in ["submitted"]]
        return len(responded_apps) / len(submitted_apps) * 100
    
    def _calculate_interview_rate(self):
        """计算面试邀请率"""
        submitted_apps = [app for app in self.data["applications"] if app["status"] != "draft"]
        if not submitted_apps:
            return 0.0
        
        interview_apps = [app for app in submitted_apps 
                         if app["status"] in ["interview_scheduled", "interview_completed", "offer_received", "accepted"]]
        return len(interview_apps) / len(submitted_apps) * 100
    
    def list_applications(self):
        """列出所有申请"""
        apps = self.data["applications"]
        if not apps:
            print("No applications found.")
            return
        
        print(f"\\n📋 Total Applications: {len(apps)}\\n")
        
        for app in sorted(apps, key=lambda x: x["updated_at"], reverse=True):
            status_emoji = {
                "draft": "📝", "submitted": "📤", "screening": "🔍", 
                "interview_scheduled": "📅", "interview_completed": "✅",
                "offer_received": "🎉", "rejected": "❌", "accepted": "🏆"
            }.get(app["status"], "❓")
            
            print(f"{status_emoji} [{app['id']}] {app['company']} - {app['position']}")
            print(f"   Status: {app['status']} | Applied: {app['application_date']}")
            if app.get("salary_range"):
                print(f"   Salary: {app['salary_range']}")
            if app.get("notes"):
                print(f"   Notes: {app['notes'][:100]}...")
            print()

def main():
    """命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Track job applications")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # 添加申请
    add_parser = subparsers.add_parser("add", help="Add new application")
    add_parser.add_argument("--company", required=True)
    add_parser.add_argument("--position", required=True)
    add_parser.add_argument("--status", default="draft")
    add_parser.add_argument("--priority", default="medium")
    add_parser.add_argument("--salary", dest="salary_range")
    add_parser.add_argument("--notes")
    
    # 更新状态
    update_parser = subparsers.add_parser("update", help="Update application status")
    update_parser.add_argument("--id", required=True, dest="app_id")
    update_parser.add_argument("--status", required=True)
    update_parser.add_argument("--notes")
    
    # 添加面试
    interview_parser = subparsers.add_parser("interview", help="Add interview")
    interview_parser.add_argument("--id", required=True, dest="app_id")
    interview_parser.add_argument("--date", required=True)
    interview_parser.add_argument("--type", default="")
    interview_parser.add_argument("--notes", default="")
    
    # 列出申请
    list_parser = subparsers.add_parser("list", help="List applications")
    list_parser.add_argument("--status")
    list_parser.add_argument("--company")
    
    # 显示统计
    subparsers.add_parser("summary", help="Show summary statistics")
    
    args = parser.parse_args()
    tracker = ApplicationTracker()
    
    if args.command == "add":
        tracker.add_application(
            args.company, args.position,
            status=args.status, priority=args.priority,
            salary_range=args.salary_range or "", notes=args.notes or ""
        )
    
    elif args.command == "update":
        tracker.update_status(args.app_id, args.status, args.notes or "")
    
    elif args.command == "interview":
        tracker.add_interview(args.app_id, args.date, args.type, args.notes)
    
    elif args.command == "list":
        if args.status or args.company:
            apps = tracker.get_applications(args.status, args.company)
            print(f"Found {len(apps)} applications:")
            for app in apps:
                print(f"- {app['company']} - {app['position']} ({app['status']})")
        else:
            tracker.list_applications()
    
    elif args.command == "summary":
        summary = tracker.get_summary()
        print("📊 Application Summary:")
        print(f"Total Applications: {summary['total_applications']}")
        print(f"Active Applications: {summary['active_applications']}")
        print(f"Response Rate: {summary['response_rate']:.1f}%")
        print(f"Interview Rate: {summary['interview_rate']:.1f}%")
        print("\\nStatus Breakdown:")
        for status, count in summary['status_breakdown'].items():
            print(f"  {status}: {count}")

if __name__ == "__main__":
    main()