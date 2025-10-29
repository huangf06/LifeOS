#!/usr/bin/env python3
"""
LifeOS AI决策顾问
基于Logseq数据分析，提供个人生活管理建议
"""

import json
import os
from datetime import datetime, date, timedelta
from pathlib import Path
import statistics
from collections import defaultdict, Counter
import re

class AIAdvisor:
    def __init__(self, lifeos_path=None):
        # 自动获取项目根目录（相对于此脚本文件）
        if lifeos_path is None:
            script_dir = Path(__file__).parent
            self.lifeos_path = script_dir.parent
        else:
            self.lifeos_path = Path(lifeos_path).expanduser()

        self.data_path = self.lifeos_path / "data"
        self.insights_path = self.data_path / "ai_insights.json"
        
        # 确保目录存在
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        # 加载历史洞察
        self.load_insights()
        
    def load_insights(self):
        """加载历史AI洞察"""
        if self.insights_path.exists():
            with open(self.insights_path, 'r', encoding='utf-8') as f:
                self.insights = json.load(f)
        else:
            self.insights = {
                'patterns': {},
                'recommendations': {},
                'learning': {},
                'last_analysis': None
            }
    
    def save_insights(self):
        """保存AI洞察"""
        self.insights['last_analysis'] = datetime.now().isoformat()
        with open(self.insights_path, 'w', encoding='utf-8') as f:
            json.dump(self.insights, f, ensure_ascii=False, indent=2, default=str)
    
    def collect_weekly_data(self, weeks=4):
        """收集最近几周的数据"""
        from logseq_tracker import LogseqTracker
        tracker = LogseqTracker()
        
        all_data = []
        for week in range(weeks):
            for day in range(7):
                target_date = date.today() - timedelta(days=week*7 + day)
                day_data = tracker.extract_daily_data(target_date)
                if day_data:
                    all_data.append(day_data)
        
        return all_data
    
    def analyze_patterns(self, data):
        """分析生活模式"""
        if not data:
            return {}
        
        patterns = {
            'mood_patterns': self._analyze_mood_patterns(data),
            'energy_patterns': self._analyze_energy_patterns(data),
            'productivity_patterns': self._analyze_productivity_patterns(data),
            'weekly_rhythms': self._analyze_weekly_rhythms(data),
            'correlations': self._analyze_correlations(data)
        }
        
        return patterns
    
    def _analyze_mood_patterns(self, data):
        """分析情绪模式"""
        moods = [(d['date'], d['mood']) for d in data if d['mood']]
        if not moods:
            return {}
        
        # 按星期几分组
        weekday_moods = defaultdict(list)
        for date_obj, mood in moods:
            weekday = date_obj.weekday()
            weekday_moods[weekday].append(mood)
        
        weekday_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        weekday_averages = {}
        for weekday, mood_list in weekday_moods.items():
            weekday_averages[weekday_names[weekday]] = statistics.mean(mood_list)
        
        # 找出最好和最差的日子
        best_day = max(weekday_averages, key=weekday_averages.get)
        worst_day = min(weekday_averages, key=weekday_averages.get)
        
        # 趋势分析
        recent_moods = [mood for _, mood in moods[-7:]]  # 最近一周
        overall_avg = statistics.mean([mood for _, mood in moods])
        recent_avg = statistics.mean(recent_moods) if recent_moods else overall_avg
        
        trend = "上升" if recent_avg > overall_avg else "下降" if recent_avg < overall_avg else "稳定"
        
        return {
            'overall_average': round(overall_avg, 1),
            'recent_average': round(recent_avg, 1),
            'trend': trend,
            'best_day': best_day,
            'worst_day': worst_day,
            'weekday_averages': weekday_averages
        }
    
    def _analyze_energy_patterns(self, data):
        """分析能量模式"""
        energies = [(d['date'], d['energy']) for d in data if d['energy']]
        if not energies:
            return {}
        
        # 类似心情分析的逻辑
        weekday_energies = defaultdict(list)
        for date_obj, energy in energies:
            weekday = date_obj.weekday()
            weekday_energies[weekday].append(energy)
        
        weekday_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        weekday_averages = {}
        for weekday, energy_list in weekday_energies.items():
            weekday_averages[weekday_names[weekday]] = statistics.mean(energy_list)
        
        best_energy_day = max(weekday_averages, key=weekday_averages.get)
        worst_energy_day = min(weekday_averages, key=weekday_averages.get)
        
        overall_avg = statistics.mean([energy for _, energy in energies])
        
        return {
            'overall_average': round(overall_avg, 1),
            'best_energy_day': best_energy_day,
            'worst_energy_day': worst_energy_day,
            'weekday_averages': weekday_averages
        }
    
    def _analyze_productivity_patterns(self, data):
        """分析生产力模式（基于任务完成情况）"""
        # 这里需要解析Logseq中的任务完成数据
        # 简化版本：基于记录的活动数量
        daily_activities = {}
        for d in data:
            date_str = d['date'].strftime('%Y-%m-%d')
            # 统计当天的活动记录数量（简化指标）
            activity_count = len([t for task_list in d.get('tasks', {}).values() for t in task_list])
            daily_activities[date_str] = activity_count
        
        if not daily_activities:
            return {}
        
        avg_activities = statistics.mean(daily_activities.values())
        
        return {
            'average_daily_activities': round(avg_activities, 1),
            'most_productive_days': sorted(daily_activities.items(), key=lambda x: x[1], reverse=True)[:3]
        }
    
    def _analyze_weekly_rhythms(self, data):
        """分析周节奏"""
        weekday_data = defaultdict(lambda: {'moods': [], 'energies': [], 'activities': []})
        
        for d in data:
            weekday = d['date'].weekday()
            if d['mood']:
                weekday_data[weekday]['moods'].append(d['mood'])
            if d['energy']:
                weekday_data[weekday]['energies'].append(d['energy'])
        
        weekday_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        rhythm = {}
        
        for weekday, data_dict in weekday_data.items():
            day_name = weekday_names[weekday]
            mood_avg = statistics.mean(data_dict['moods']) if data_dict['moods'] else 0
            energy_avg = statistics.mean(data_dict['energies']) if data_dict['energies'] else 0
            
            rhythm[day_name] = {
                'mood': round(mood_avg, 1),
                'energy': round(energy_avg, 1),
                'overall_score': round((mood_avg + energy_avg) / 2, 1)
            }
        
        return rhythm
    
    def _analyze_correlations(self, data):
        """分析变量间相关性"""
        mood_energy_pairs = []
        sleep_mood_pairs = []
        
        for d in data:
            if d['mood'] and d['energy']:
                mood_energy_pairs.append((d['mood'], d['energy']))
            
            # 这里可以添加更多相关性分析
            # 比如睡眠质量与心情、天气与能量等
        
        correlations = {}
        
        if mood_energy_pairs:
            # 简单的相关性计算
            moods = [pair[0] for pair in mood_energy_pairs]
            energies = [pair[1] for pair in mood_energy_pairs]
            
            if len(set(moods)) > 1 and len(set(energies)) > 1:
                # 计算皮尔逊相关系数（简化版）
                mood_avg = statistics.mean(moods)
                energy_avg = statistics.mean(energies)
                
                numerator = sum((m - mood_avg) * (e - energy_avg) for m, e in zip(moods, energies))
                mood_var = sum((m - mood_avg) ** 2 for m in moods)
                energy_var = sum((e - energy_avg) ** 2 for e in energies)
                
                if mood_var > 0 and energy_var > 0:
                    correlation = numerator / (mood_var * energy_var) ** 0.5
                    correlations['mood_energy'] = round(correlation, 2)
        
        return correlations
    
    def generate_recommendations(self, patterns):
        """基于模式分析生成建议"""
        recommendations = []
        
        # 基于心情模式的建议
        if 'mood_patterns' in patterns and patterns['mood_patterns']:
            mood_data = patterns['mood_patterns']
            
            if mood_data['overall_average'] < 6:
                recommendations.append({
                    'type': 'mood_improvement',
                    'priority': 'high',
                    'title': '提升整体心情',
                    'suggestion': f'你的平均心情为 {mood_data["overall_average"]}/10，建议增加愉悦活动，如运动、音乐或社交',
                    'actionable_steps': [
                        '每天安排30分钟愉悦活动',
                        '记录让你开心的事情',
                        '在心情低落的 {worst_day} 安排轻松任务'
                    ]
                })
            
            if mood_data['trend'] == '下降':
                recommendations.append({
                    'type': 'mood_trend',
                    'priority': 'high', 
                    'title': '心情趋势下降',
                    'suggestion': '最近心情呈下降趋势，建议主动调整生活节奏',
                    'actionable_steps': [
                        '分析近期压力源',
                        '增加休息和放松时间',
                        '寻求支持和帮助'
                    ]
                })
        
        # 基于能量模式的建议
        if 'energy_patterns' in patterns and patterns['energy_patterns']:
            energy_data = patterns['energy_patterns']
            
            recommendations.append({
                'type': 'energy_optimization',
                'priority': 'medium',
                'title': '优化能量管理',
                'suggestion': f'在 {energy_data["best_energy_day"]} 安排重要任务，{energy_data["worst_energy_day"]} 进行轻松活动',
                'actionable_steps': [
                    f'将重要工作安排在 {energy_data["best_energy_day"]}',
                    f'{energy_data["worst_energy_day"]} 专注休息和恢复',
                    '记录影响能量的因素（睡眠、饮食、运动）'
                ]
            })
        
        # 基于相关性的建议
        if 'correlations' in patterns and patterns['correlations']:
            corr_data = patterns['correlations']
            
            if corr_data.get('mood_energy', 0) > 0.5:
                recommendations.append({
                    'type': 'correlation_insight',
                    'priority': 'low',
                    'title': '心情与能量正相关',
                    'suggestion': '你的心情和能量高度相关，提升其中一项会带动另一项',
                    'actionable_steps': [
                        '能量低时先调节心情',
                        '心情差时通过运动提升能量',
                        '建立积极的反馈循环'
                    ]
                })
        
        return recommendations
    
    def generate_daily_plan(self, target_date=None):
        """基于历史数据生成优化的日计划"""
        if target_date is None:
            target_date = date.today() + timedelta(days=1)  # 明日计划
        
        weekday = target_date.weekday()
        weekday_name = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][weekday]
        
        # 获取该星期几的历史数据
        data = self.collect_weekly_data(4)
        patterns = self.analyze_patterns(data)
        
        plan = {
            'date': target_date,
            'weekday': weekday_name,
            'recommendations': [],
            'optimal_schedule': {},
            'focus_areas': [],
            'energy_forecast': 'medium'
        }
        
        # 基于历史模式预测
        if 'energy_patterns' in patterns:
            energy_data = patterns['energy_patterns']
            weekday_avg = energy_data.get('weekday_averages', {}).get(weekday_name, 5)
            
            if weekday_avg >= 7:
                plan['energy_forecast'] = 'high'
                plan['focus_areas'].append('重要项目')
                plan['focus_areas'].append('学习新技能')
            elif weekday_avg <= 4:
                plan['energy_forecast'] = 'low'
                plan['focus_areas'].append('休息恢复')
                plan['focus_areas'].append('轻松任务')
            else:
                plan['energy_forecast'] = 'medium'
                plan['focus_areas'].append('日常任务')
                plan['focus_areas'].append('维护性工作')
        
        # 时间安排建议
        if plan['energy_forecast'] == 'high':
            plan['optimal_schedule'] = {
                '09:00-11:00': '核心工作/学习',
                '11:00-12:00': '沟通协调',
                '14:00-16:00': '项目推进',
                '16:00-17:00': '总结规划',
                '19:00-20:00': '个人发展'
            }
        elif plan['energy_forecast'] == 'low':
            plan['optimal_schedule'] = {
                '09:00-10:00': '轻松阅读',
                '10:00-11:00': '整理环境',
                '14:00-15:00': '简单任务',
                '15:00-16:00': '放松休息',
                '19:00-20:00': '娱乐恢复'
            }
        else:
            plan['optimal_schedule'] = {
                '09:00-11:00': '重要任务',
                '11:00-12:00': '邮件处理',
                '14:00-15:30': '会议/沟通',
                '15:30-17:00': '后续工作',
                '19:00-20:00': '学习/运动'
            }
        
        return plan
    
    def analyze_and_advise(self):
        """执行完整的分析和建议生成"""
        print("🧠 AI顾问正在分析你的生活数据...")
        
        # 收集数据
        data = self.collect_weekly_data(4)
        if not data:
            return "📊 暂无足够数据进行分析，请先记录几天的生活数据"
        
        print(f"📊 已收集 {len(data)} 天的数据")
        
        # 分析模式
        patterns = self.analyze_patterns(data)
        
        # 生成建议
        recommendations = self.generate_recommendations(patterns)
        
        # 生成明日计划
        tomorrow_plan = self.generate_daily_plan()
        
        # 保存洞察
        self.insights['patterns'] = patterns
        self.insights['recommendations'] = recommendations
        self.save_insights()
        
        # 生成报告
        report = self._format_analysis_report(patterns, recommendations, tomorrow_plan)
        
        return report
    
    def _format_analysis_report(self, patterns, recommendations, tomorrow_plan):
        """格式化分析报告"""
        report = "🧠 AI生活顾问分析报告\n"
        report += "=" * 40 + "\n\n"
        
        # 生活模式分析
        if 'mood_patterns' in patterns and patterns['mood_patterns']:
            mood_data = patterns['mood_patterns']
            report += "😊 心情分析:\n"
            report += f"  • 平均心情: {mood_data['overall_average']}/10\n"
            report += f"  • 近期趋势: {mood_data['trend']}\n"
            report += f"  • 最佳状态: {mood_data['best_day']}\n"
            report += f"  • 需要关注: {mood_data['worst_day']}\n\n"
        
        if 'energy_patterns' in patterns and patterns['energy_patterns']:
            energy_data = patterns['energy_patterns']
            report += "⚡ 能量分析:\n"
            report += f"  • 平均能量: {energy_data['overall_average']}/10\n"
            report += f"  • 能量最佳: {energy_data['best_energy_day']}\n"
            report += f"  • 能量最低: {energy_data['worst_energy_day']}\n\n"
        
        # 关键建议
        if recommendations:
            report += "💡 AI建议:\n"
            for i, rec in enumerate(recommendations[:3], 1):  # 显示前3个建议
                report += f"  {i}. {rec['title']}\n"
                report += f"     {rec['suggestion']}\n"
                if rec['actionable_steps']:
                    report += f"     行动步骤: {rec['actionable_steps'][0]}\n"
                report += "\n"
        
        # 明日计划
        report += f"📅 明日优化建议 ({tomorrow_plan['weekday']}):\n"
        report += f"  • 预期能量: {tomorrow_plan['energy_forecast']}\n"
        report += f"  • 关注领域: {', '.join(tomorrow_plan['focus_areas'])}\n"
        report += "  • 建议时间安排:\n"
        
        for time_slot, activity in tomorrow_plan['optimal_schedule'].items():
            report += f"    {time_slot}: {activity}\n"
        
        report += f"\n📊 分析基于最近 {len(self.collect_weekly_data(4))} 天的数据"
        
        return report


def main():
    """命令行入口"""
    import sys
    
    advisor = AIAdvisor()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'analyze':
            result = advisor.analyze_and_advise()
            print(result)
        
        elif command == 'plan':
            plan = advisor.generate_daily_plan()
            print("📅 AI优化计划:")
            print(f"日期: {plan['date']} ({plan['weekday']})")
            print(f"能量预测: {plan['energy_forecast']}")
            print(f"关注领域: {', '.join(plan['focus_areas'])}")
            print("\n建议时间安排:")
            for time_slot, activity in plan['optimal_schedule'].items():
                print(f"  {time_slot}: {activity}")
        
        else:
            print("用法: python ai_advisor.py [analyze|plan]")
    else:
        result = advisor.analyze_and_advise()
        print(result)


if __name__ == "__main__":
    main()