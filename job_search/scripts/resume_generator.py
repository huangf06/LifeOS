#!/usr/bin/env python3
"""
简历生成器 - 根据公司和职位生成定制化简历
"""

import json
import os
from datetime import datetime
from pathlib import Path

class ResumeGenerator:
    def __init__(self, config_path="./config/settings.json"):
        self.config_path = config_path
        self.config = self.load_config()
        self.base_dir = Path(__file__).parent.parent
        
    def load_config(self):
        """加载配置文件"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_template(self, template_name="base_template"):
        """加载简历模板"""
        template_path = self.base_dir / "resumes" / "templates" / f"{template_name}.md"
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def get_company_customization(self, company_name):
        """获取公司特定的定制化内容"""
        # 这里可以根据公司特点定制内容
        customizations = {
            "IMC Trading": {
                "title": "Quantitative Research Candidate",
                "education_details": "- Deep Learning, Machine Learning, Time-Series Analysis, Statistical Methods\\n- Research: Evolutionary algorithms for adaptive systems optimization",
                "experience_focus": "quantitative_trading",
                "skills_emphasis": ["Python", "Machine Learning", "Statistical Analysis", "Time-Series Analysis"]
            },
            "Optiver": {
                "title": "Quantitative Trading Candidate", 
                "education_details": "- Advanced quantitative methods and algorithmic trading strategies\\n- Thesis: Market regime detection using machine learning",
                "experience_focus": "trading_systems",
                "skills_emphasis": ["Python", "Low-latency systems", "Mathematical modeling"]
            },
            "default": {
                "title": "Quantitative Research Specialist",
                "education_details": "- Specialization in machine learning and quantitative analysis\\n- Research focus on adaptive algorithms and financial applications",
                "experience_focus": "general_quant",
                "skills_emphasis": ["Python", "Machine Learning", "Statistical Analysis"]
            }
        }
        return customizations.get(company_name, customizations["default"])
    
    def format_experience_section(self, focus_type="general_quant"):
        """根据关注点格式化工作经验部分"""
        if focus_type == "quantitative_trading":
            return """**Independent Quantitative Research** | 2019 – 2023  
**Systematic Trading & Strategy Development**
- Multi-year systematic analysis and trading in China A-share markets
- Licensed Securities Professional (证券从业资格) + Fund Management Professional (基金从业资格)
- Developed quantitative screening frameworks and risk management protocols

**GLP Technology Co., Ltd.** | Jul 2017 – Aug 2019  
**Senior Data Modeling Engineer, Team Lead** | Shanghai, China
- Built machine learning models for financial risk assessment, improving prediction accuracy by 15%
- Automated ML pipelines reducing processing time by 40%

**BQ Investment Co., Ltd.** | Jul 2015 – Jun 2017  
**Quantitative Research Associate** | Beijing, China
- Participated in multi-factor model development for systematic equity strategies
- Applied time-series analysis and statistical testing methodologies"""
        
        # 可以添加更多focus类型
        return self.format_experience_section("quantitative_trading")  # 默认使用quantitative_trading
    
    def format_skills_section(self, emphasized_skills=None):
        """格式化技能部分"""
        if emphasized_skills is None:
            emphasized_skills = ["Python", "Machine Learning", "Statistical Analysis"]
            
        return f"""**Programming**: {', '.join(self.config['skills']['programming'])}  
**Quantitative Methods**: Time-series analysis, statistical modeling, risk assessment, backtesting  
**ML Frameworks**: {', '.join(self.config['skills']['ml_frameworks'])}  
**Tools**: {', '.join(self.config['skills']['tools'])}  
**Languages**: {', '.join(self.config['skills']['languages'])}"""
    
    def generate_resume(self, company_name, position_title, template_name="base_template"):
        """生成定制化简历"""
        # 加载模板
        template = self.load_template(template_name)
        
        # 获取公司定制化内容
        customization = self.get_company_customization(company_name)
        
        # 填充模板变量
        content = template.format(
            name=self.config['personal_info']['name'],
            title=customization['title'],
            email=self.config['personal_info']['email'],
            phone=self.config['personal_info']['phone'],
            location=self.config['personal_info']['location'],
            availability=self.config['personal_info']['availability'],
            education_details=customization['education_details'],
            tsinghua_details="- Mathematical modeling, statistical analysis, operations research foundation",
            experience_section=self.format_experience_section(customization['experience_focus']),
            skills_section=self.format_skills_section(customization['skills_emphasis']),
            additional_qualifications="• Licensed Securities Professional (China)\\n• Licensed Fund Management Professional (China)\\n• Multi-year experience in China A-share systematic trading",
            footer_note=f"*Generated for {company_name} - {position_title} position*"
        )
        
        # 保存文件
        output_filename = f"{company_name.replace(' ', '_')}_{position_title.replace(' ', '_')}_v1.md"
        output_path = self.base_dir / "resumes" / "versions" / output_filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"✅ Resume generated: {output_filename}")
        return output_path
    
    def convert_to_pdf(self, markdown_path):
        """将Markdown简历转换为PDF"""
        import subprocess
        
        input_path = Path(markdown_path)
        output_path = self.base_dir / "resumes" / "output" / f"{input_path.stem}.pdf"
        
        try:
            subprocess.run([
                "pandoc", str(input_path), 
                "-o", str(output_path),
                "--pdf-engine=xelatex"
            ], check=True)
            print(f"✅ PDF generated: {output_path.name}")
            return output_path
        except subprocess.CalledProcessError as e:
            print(f"❌ PDF generation failed: {e}")
            return None
    
    def batch_generate(self, companies_positions):
        """批量生成简历"""
        results = []
        for company, position in companies_positions:
            try:
                md_path = self.generate_resume(company, position)
                pdf_path = self.convert_to_pdf(md_path)
                results.append({
                    "company": company,
                    "position": position,
                    "markdown": str(md_path),
                    "pdf": str(pdf_path) if pdf_path else None,
                    "generated_at": datetime.now().isoformat()
                })
            except Exception as e:
                print(f"❌ Failed to generate resume for {company}: {e}")
        
        return results

def main():
    """主函数 - 命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate customized resumes")
    parser.add_argument("--company", required=True, help="Target company name")
    parser.add_argument("--position", required=True, help="Position title")
    parser.add_argument("--template", default="base_template", help="Template to use")
    parser.add_argument("--pdf", action="store_true", help="Also generate PDF")
    
    args = parser.parse_args()
    
    generator = ResumeGenerator()
    md_path = generator.generate_resume(args.company, args.position, args.template)
    
    if args.pdf:
        generator.convert_to_pdf(md_path)

if __name__ == "__main__":
    main()