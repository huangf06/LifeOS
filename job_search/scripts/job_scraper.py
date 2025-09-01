#!/usr/bin/env python3
"""
职位信息爬虫 - 收集量化金融相关职位
"""

import json
import requests
from datetime import datetime
from pathlib import Path
import time
import re

class JobScraper:
    def __init__(self, output_file="./job_data/scraped_jobs.json"):
        self.output_file = Path(__file__).parent.parent / output_file.lstrip('./')
        self.data = self.load_existing_data()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def load_existing_data(self):
        """加载现有数据"""
        if self.output_file.exists():
            with open(self.output_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {"jobs": [], "metadata": {"last_scraped": "", "total_jobs": 0}}
    
    def save_data(self):
        """保存数据"""
        self.data["metadata"]["last_scraped"] = datetime.now().isoformat()
        self.data["metadata"]["total_jobs"] = len(self.data["jobs"])
        
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
    
    def scrape_company_careers(self, company_name, careers_url):
        """爬取公司官网职位信息"""
        print(f"🔍 Scraping {company_name} careers page...")
        
        try:
            response = self.session.get(careers_url, timeout=10)
            response.raise_for_status()
            
            # 这里应该根据具体网站结构来解析
            # 以下是一个通用的示例
            jobs_found = self.extract_jobs_from_html(company_name, response.text, careers_url)
            
            for job in jobs_found:
                if not self.job_exists(job):
                    self.data["jobs"].append(job)
                    print(f"  ✅ Found new job: {job['title']}")
            
            time.sleep(2)  # 礼貌性延迟
            
        except Exception as e:
            print(f"  ❌ Error scraping {company_name}: {e}")
    
    def extract_jobs_from_html(self, company, html_content, source_url):
        """从HTML中提取职位信息（需要根据具体网站定制）"""
        jobs = []
        
        # 简单的关键词匹配示例
        quant_keywords = [
            "quantitative researcher", "quantitative analyst", "quant developer",
            "quantitative trading", "algorithmic trading", "systematic trading",
            "risk analyst", "data scientist.*finance", "machine learning.*trading"
        ]
        
        for keyword in quant_keywords:
            if re.search(keyword, html_content, re.IGNORECASE):
                # 这里应该有更复杂的解析逻辑
                job = {
                    "id": f"{company.lower().replace(' ', '_')}_{keyword.replace(' ', '_')}_{int(time.time())}",
                    "company": company,
                    "title": keyword.title(),
                    "location": "Amsterdam, Netherlands",  # 默认位置
                    "salary_range": "",
                    "job_type": "Full-time",
                    "description": f"Position related to {keyword}",
                    "requirements": [],
                    "source_url": source_url,
                    "scraped_at": datetime.now().isoformat(),
                    "status": "active"
                }
                jobs.append(job)
                break  # 每个公司只添加一个匹配的职位示例
        
        return jobs
    
    def job_exists(self, new_job):
        """检查职位是否已存在"""
        for existing_job in self.data["jobs"]:
            if (existing_job["company"] == new_job["company"] and 
                existing_job["title"].lower() == new_job["title"].lower()):
                return True
        return False
    
    def scrape_target_companies(self):
        """爬取目标公司的职位"""
        target_companies = {
            "IMC Trading": "https://www.imc.com/us/careers",
            "Optiver": "https://optiver.com/working-at-optiver/career-opportunities",
            "Flow Traders": "https://www.flowtraders.com/careers",
            "Da Vinci": "https://www.davinci-group.com/careers/",
            # 添加更多公司...
        }
        
        for company, url in target_companies.items():
            try:
                self.scrape_company_careers(company, url)
            except Exception as e:
                print(f"Failed to scrape {company}: {e}")
        
        self.save_data()
        print(f"\\n✅ Scraping completed. Total jobs: {len(self.data['jobs'])}")
    
    def add_manual_job(self, company, title, **kwargs):
        """手动添加职位信息"""
        job = {
            "id": f"{company.lower().replace(' ', '_')}_{title.lower().replace(' ', '_')}_{int(time.time())}",
            "company": company,
            "title": title,
            "location": kwargs.get("location", "Amsterdam, Netherlands"),
            "salary_range": kwargs.get("salary_range", ""),
            "job_type": kwargs.get("job_type", "Full-time"),
            "description": kwargs.get("description", ""),
            "requirements": kwargs.get("requirements", []),
            "source_url": kwargs.get("source_url", ""),
            "scraped_at": datetime.now().isoformat(),
            "status": "active",
            "manually_added": True
        }
        
        if not self.job_exists(job):
            self.data["jobs"].append(job)
            self.save_data()
            print(f"✅ Manually added: {company} - {title}")
            return job["id"]
        else:
            print(f"❌ Job already exists: {company} - {title}")
            return None
    
    def get_jobs(self, company=None, keyword=None):
        """获取职位列表"""
        jobs = self.data["jobs"]
        
        if company:
            jobs = [job for job in jobs if company.lower() in job["company"].lower()]
        
        if keyword:
            jobs = [job for job in jobs if keyword.lower() in job["title"].lower() or 
                   keyword.lower() in job["description"].lower()]
        
        return jobs
    
    def analyze_job_market(self):
        """分析职位市场"""
        jobs = self.data["jobs"]
        
        if not jobs:
            return {"error": "No jobs data available"}
        
        # 公司分布
        company_counts = {}
        for job in jobs:
            company_counts[job["company"]] = company_counts.get(job["company"], 0) + 1
        
        # 职位类型分布
        title_keywords = {}
        for job in jobs:
            title_lower = job["title"].lower()
            for keyword in ["researcher", "analyst", "developer", "trader", "scientist"]:
                if keyword in title_lower:
                    title_keywords[keyword] = title_keywords.get(keyword, 0) + 1
        
        return {
            "total_jobs": len(jobs),
            "company_distribution": company_counts,
            "position_types": title_keywords,
            "last_updated": self.data["metadata"]["last_scraped"]
        }

def main():
    """命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Job market scraper")
    subparsers = parser.add_subparsers(dest="command")
    
    # 爬取职位
    subparsers.add_parser("scrape", help="Scrape job postings from target companies")
    
    # 手动添加职位
    add_parser = subparsers.add_parser("add", help="Manually add a job")
    add_parser.add_argument("--company", required=True)
    add_parser.add_argument("--title", required=True) 
    add_parser.add_argument("--location", default="Amsterdam, Netherlands")
    add_parser.add_argument("--salary")
    add_parser.add_argument("--url")
    
    # 搜索职位
    search_parser = subparsers.add_parser("search", help="Search jobs")
    search_parser.add_argument("--company")
    search_parser.add_argument("--keyword")
    
    # 市场分析
    subparsers.add_parser("analyze", help="Analyze job market")
    
    args = parser.parse_args()
    scraper = JobScraper()
    
    if args.command == "scrape":
        scraper.scrape_target_companies()
    
    elif args.command == "add":
        scraper.add_manual_job(
            args.company, args.title,
            location=args.location, salary_range=args.salary or "",
            source_url=args.url or ""
        )
    
    elif args.command == "search":
        jobs = scraper.get_jobs(args.company, args.keyword)
        print(f"Found {len(jobs)} jobs:")
        for job in jobs:
            print(f"- {job['company']} - {job['title']} ({job['location']})")
            if job.get('salary_range'):
                print(f"  Salary: {job['salary_range']}")
    
    elif args.command == "analyze":
        analysis = scraper.analyze_job_market()
        print("📈 Job Market Analysis:")
        print(f"Total Jobs: {analysis['total_jobs']}")
        print("\\nCompany Distribution:")
        for company, count in analysis['company_distribution'].items():
            print(f"  {company}: {count}")
        print("\\nPosition Types:")
        for pos_type, count in analysis['position_types'].items():
            print(f"  {pos_type}: {count}")

if __name__ == "__main__":
    main()