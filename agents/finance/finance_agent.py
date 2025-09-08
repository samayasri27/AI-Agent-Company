"""
Finance Agent - Budget analysis and financial reporting
"""
import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.agent_base import AgentBase


class FinanceAgent(AgentBase):
    """Finance Agent for budget analysis and financial reporting"""
    
    def __init__(self):
        super().__init__(
            name="Finance Agent",
            role="Financial Analysis & Budget Management",
            department="Finance"
        )
        self.capabilities = [
            "Budget planning and analysis",
            "Financial reporting and dashboards",
            "Cost analysis and optimization",
            "Revenue forecasting",
            "ROI and profitability analysis",
            "Financial risk assessment"
        ]
    
    async def execute_task(self, task: str) -> Dict[str, Any]:
        """Execute finance-related tasks"""
        try:
            if isinstance(task, str):
                task_dict = {'description': task, 'type': 'general'}
            else:
                task_dict = task
            
            task_description = task_dict.get('description', '').lower()
            
            if 'budget' in task_description:
                return self._create_budget_analysis(task_dict)
            elif 'financial report' in task_description or 'finance report' in task_description:
                return self._create_financial_report(task_dict)
            elif 'forecast' in task_description:
                return self._create_financial_forecast(task_dict)
            elif 'roi' in task_description or 'return on investment' in task_description:
                return self._analyze_roi(task_dict)
            else:
                return self._general_financial_analysis(task_dict)
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Finance task processing failed: {str(e)}",
                'agent': self.name,
                'timestamp': datetime.now().isoformat()
            }
    
    def _create_budget_analysis(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive budget analysis"""
        budget_period = task.get('period', 'annual')
        department = task.get('department', 'company_wide')
        budget_amount = task.get('budget_amount', 1000000)
        
        # Generate budget breakdown
        budget_analysis = {
            'total_budget': budget_amount,
            'period': budget_period,
            'department': department,
            'budget_breakdown': self._generate_budget_breakdown(budget_amount, department),
            'variance_analysis': self._analyze_budget_variance(),
            'cost_optimization': self._identify_cost_optimization(),
            'budget_recommendations': self._generate_budget_recommendations(),
            'risk_factors': self._identify_budget_risks(),
            'approval_workflow': self._define_approval_workflow()
        }
        
        result = {
            'success': True,
            'budget_analysis': budget_analysis,
            'period': budget_period,
            'department': department,
            'total_budget': budget_amount,
            'agent': self.name,
            'timestamp': datetime.now().isoformat()
        }
        
        # Generate budget spreadsheet
        try:
            # Prepare data for Excel
            budget_data = {
                'Budget Summary': {
                    'headers': ['Category', 'Allocated Budget', 'Percentage', 'Quarterly Split'],
                    'rows': []
                }
            }
            
            for category, amount in budget_analysis['budget_breakdown'].items():
                percentage = (amount / budget_amount) * 100
                quarterly = amount / 4
                budget_data['Budget Summary']['rows'].append([
                    category.replace('_', ' ').title(),
                    f"${amount:,}",
                    f"{percentage:.1f}%",
                    f"${quarterly:,}"
                ])
            
            filename = f"budget_analysis_{department}_{budget_period}_{datetime.now().strftime('%Y%m%d')}"
            xlsx_path = self.create_document(budget_data, 'xlsx', filename)
            
            if xlsx_path:
                result['generated_files'] = [xlsx_path]
                self.log(f"Generated budget analysis spreadsheet: {filename}.xlsx")
            
            # Also create a detailed report document
            doc_content = {
                'title': f'Budget Analysis Report - {department.replace("_", " ").title()}',
                'author': self.name,
                'subject': f'{budget_period.title()} Budget Analysis',
                'executive_summary': f'Comprehensive budget analysis for {department} covering {budget_period} period with total budget of ${budget_amount:,}.',
                'sections': [
                    {
                        'title': 'Budget Overview',
                        'content': f'Total Budget: ${budget_amount:,}\\nPeriod: {budget_period.title()}\\nDepartment: {department.replace("_", " ").title()}\\nAnalysis Date: {datetime.now().strftime("%B %d, %Y")}'
                    },
                    {
                        'title': 'Budget Breakdown',
                        'table': {
                            'headers': ['Category', 'Amount', 'Percentage'],
                            'rows': [[cat.replace('_', ' ').title(), f"${amt:,}", f"{(amt/budget_amount)*100:.1f}%"] 
                                   for cat, amt in budget_analysis['budget_breakdown'].items()]
                        }
                    },
                    {
                        'title': 'Cost Optimization Opportunities',
                        'bullet_points': budget_analysis['cost_optimization']
                    },
                    {
                        'title': 'Budget Recommendations',
                        'bullet_points': budget_analysis['budget_recommendations']
                    },
                    {
                        'title': 'Risk Factors',
                        'bullet_points': budget_analysis['risk_factors']
                    }
                ]
            }
            
            docx_path = self.create_document(doc_content, 'docx', filename + '_report')
            if docx_path:
                result['generated_files'] = result.get('generated_files', []) + [docx_path]
                self.log(f"Generated budget analysis report: {filename}_report.docx")
                
        except Exception as e:
            self.log(f"Error generating budget documents: {str(e)}")
            result['document_generation_error'] = str(e)
        
        return result
    
    def _create_financial_report(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive financial report"""
        report_type = task.get('report_type', 'quarterly')
        include_forecasts = task.get('include_forecasts', True)
        
        # Generate financial data
        financial_data = {
            'revenue': self._generate_revenue_data(report_type),
            'expenses': self._generate_expense_data(report_type),
            'profitability': self._calculate_profitability(),
            'cash_flow': self._generate_cash_flow_data(),
            'key_metrics': self._calculate_key_metrics(),
            'variance_analysis': self._perform_variance_analysis(),
            'forecasts': self._generate_forecasts() if include_forecasts else None
        }
        
        result = {
            'success': True,
            'financial_report': financial_data,
            'report_type': report_type,
            'reporting_period': self._get_reporting_period(report_type),
            'agent': self.name,
            'timestamp': datetime.now().isoformat()
        }
        
        # Generate financial report spreadsheet
        try:
            # Create comprehensive financial report
            report_data = {
                'Financial Summary': {
                    'headers': ['Metric', 'Current Period', 'Previous Period', 'Variance'],
                    'rows': [
                        ['Total Revenue', f"${financial_data['revenue']['total']:,}", 
                         f"${financial_data['revenue']['previous']:,}", 
                         f"{financial_data['revenue']['growth']:.1f}%"],
                        ['Total Expenses', f"${financial_data['expenses']['total']:,}", 
                         f"${financial_data['expenses']['previous']:,}", 
                         f"{financial_data['expenses']['change']:.1f}%"],
                        ['Net Profit', f"${financial_data['profitability']['net_profit']:,}", 
                         f"${financial_data['profitability']['previous_profit']:,}", 
                         f"{financial_data['profitability']['profit_growth']:.1f}%"],
                        ['Profit Margin', f"{financial_data['profitability']['margin']:.1f}%", 
                         f"{financial_data['profitability']['previous_margin']:.1f}%", 
                         f"{financial_data['profitability']['margin_change']:.1f}pp"]
                    ]
                },
                'Revenue Breakdown': {
                    'headers': ['Revenue Source', 'Amount', 'Percentage'],
                    'rows': [[source.replace('_', ' ').title(), f"${amount:,}", f"{(amount/financial_data['revenue']['total'])*100:.1f}%"] 
                           for source, amount in financial_data['revenue']['breakdown'].items()]
                },
                'Expense Breakdown': {
                    'headers': ['Expense Category', 'Amount', 'Percentage'],
                    'rows': [[category.replace('_', ' ').title(), f"${amount:,}", f"{(amount/financial_data['expenses']['total'])*100:.1f}%"] 
                           for category, amount in financial_data['expenses']['breakdown'].items()]
                }
            }
            
            filename = f"financial_report_{report_type}_{datetime.now().strftime('%Y%m%d')}"
            xlsx_path = self.create_document(report_data, 'xlsx', filename)
            
            if xlsx_path:
                result['generated_files'] = [xlsx_path]
                self.log(f"Generated financial report spreadsheet: {filename}.xlsx")
                
        except Exception as e:
            self.log(f"Error generating financial report: {str(e)}")
            result['document_generation_error'] = str(e)
        
        return result
    
    def _create_financial_forecast(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create financial forecast"""
        forecast_period = task.get('forecast_period', '12_months')
        scenarios = task.get('scenarios', ['conservative', 'realistic', 'optimistic'])
        
        forecast_data = {}
        for scenario in scenarios:
            forecast_data[scenario] = {
                'revenue_forecast': self._forecast_revenue(scenario, forecast_period),
                'expense_forecast': self._forecast_expenses(scenario, forecast_period),
                'profit_forecast': self._forecast_profit(scenario, forecast_period),
                'cash_flow_forecast': self._forecast_cash_flow(scenario, forecast_period)
            }
        
        result = {
            'success': True,
            'forecast': forecast_data,
            'forecast_period': forecast_period,
            'scenarios': scenarios,
            'assumptions': self._document_forecast_assumptions(),
            'agent': self.name,
            'timestamp': datetime.now().isoformat()
        }
        
        return result
    
    def _analyze_roi(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze return on investment"""
        investment_amount = task.get('investment_amount', 100000)
        investment_type = task.get('investment_type', 'marketing_campaign')
        time_period = task.get('time_period', '12_months')
        
        roi_analysis = {
            'investment_amount': investment_amount,
            'investment_type': investment_type,
            'time_period': time_period,
            'expected_returns': self._calculate_expected_returns(investment_amount, investment_type),
            'roi_percentage': self._calculate_roi_percentage(investment_amount, investment_type),
            'payback_period': self._calculate_payback_period(investment_amount, investment_type),
            'npv_analysis': self._calculate_npv(investment_amount, investment_type),
            'risk_assessment': self._assess_investment_risk(investment_type),
            'recommendations': self._generate_investment_recommendations(investment_type)
        }
        
        return {
            'success': True,
            'roi_analysis': roi_analysis,
            'agent': self.name,
            'timestamp': datetime.now().isoformat()
        }
    
    def _general_financial_analysis(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """General financial analysis"""
        analysis_type = task.get('analysis_type', 'performance_review')
        
        analysis = {
            'financial_health': self._assess_financial_health(),
            'performance_metrics': self._calculate_performance_metrics(),
            'trend_analysis': self._perform_trend_analysis(),
            'benchmarking': self._perform_industry_benchmarking(),
            'recommendations': self._generate_financial_recommendations()
        }
        
        return {
            'success': True,
            'financial_analysis': analysis,
            'analysis_type': analysis_type,
            'agent': self.name,
            'timestamp': datetime.now().isoformat()
        }
    
    # Helper methods for financial calculations and data generation
    def _generate_budget_breakdown(self, total_budget: int, department: str) -> Dict[str, int]:
        """Generate realistic budget breakdown"""
        if department == 'marketing':
            return {
                'advertising': int(total_budget * 0.4),
                'content_creation': int(total_budget * 0.2),
                'events_and_conferences': int(total_budget * 0.15),
                'marketing_tools': int(total_budget * 0.1),
                'personnel': int(total_budget * 0.1),
                'miscellaneous': int(total_budget * 0.05)
            }
        elif department == 'engineering':
            return {
                'personnel': int(total_budget * 0.6),
                'infrastructure': int(total_budget * 0.15),
                'software_licenses': int(total_budget * 0.1),
                'equipment': int(total_budget * 0.08),
                'training': int(total_budget * 0.05),
                'miscellaneous': int(total_budget * 0.02)
            }
        else:  # company_wide
            return {
                'personnel': int(total_budget * 0.5),
                'marketing': int(total_budget * 0.2),
                'operations': int(total_budget * 0.15),
                'technology': int(total_budget * 0.08),
                'facilities': int(total_budget * 0.05),
                'contingency': int(total_budget * 0.02)
            }
    
    def _analyze_budget_variance(self) -> List[str]:
        return [
            'Personnel costs 5% under budget due to delayed hiring',
            'Marketing spend 12% over budget due to additional campaigns',
            'Technology costs on track with budget allocations',
            'Facilities costs 3% under budget due to remote work'
        ]
    
    def _identify_cost_optimization(self) -> List[str]:
        return [
            'Consolidate software subscriptions to reduce licensing costs',
            'Negotiate better rates with vendors for bulk purchases',
            'Implement energy-efficient practices to reduce utility costs',
            'Optimize marketing spend by focusing on high-ROI channels',
            'Consider remote work options to reduce facility costs'
        ]
    
    def _generate_budget_recommendations(self) -> List[str]:
        return [
            'Increase marketing budget allocation for Q4 campaigns',
            'Create contingency fund for unexpected technology needs',
            'Invest in employee training and development programs',
            'Review and optimize vendor contracts annually',
            'Implement monthly budget review meetings'
        ]
    
    def _identify_budget_risks(self) -> List[str]:
        return [
            'Economic downturn could impact revenue projections',
            'Inflation may increase operational costs',
            'Currency fluctuations for international operations',
            'Regulatory changes may require additional compliance costs',
            'Technology disruption may require additional investments'
        ]
    
    def _define_approval_workflow(self) -> Dict[str, str]:
        return {
            'department_head': 'Initial budget review and approval',
            'finance_team': 'Financial analysis and validation',
            'executive_team': 'Strategic alignment and final approval',
            'board_approval': 'Required for budgets over $1M'
        }
    
    def _generate_revenue_data(self, report_type: str) -> Dict[str, Any]:
        base_revenue = 500000 if report_type == 'quarterly' else 2000000
        return {
            'total': base_revenue,
            'previous': int(base_revenue * 0.9),
            'growth': 11.1,
            'breakdown': {
                'product_sales': int(base_revenue * 0.6),
                'service_revenue': int(base_revenue * 0.3),
                'licensing': int(base_revenue * 0.1)
            }
        }
    
    def _generate_expense_data(self, report_type: str) -> Dict[str, Any]:
        base_expenses = 400000 if report_type == 'quarterly' else 1600000
        return {
            'total': base_expenses,
            'previous': int(base_expenses * 0.95),
            'change': 5.3,
            'breakdown': {
                'personnel': int(base_expenses * 0.5),
                'marketing': int(base_expenses * 0.2),
                'operations': int(base_expenses * 0.15),
                'technology': int(base_expenses * 0.1),
                'other': int(base_expenses * 0.05)
            }
        }
    
    def _calculate_profitability(self) -> Dict[str, Any]:
        revenue = 500000
        expenses = 400000
        net_profit = revenue - expenses
        margin = (net_profit / revenue) * 100
        
        return {
            'net_profit': net_profit,
            'previous_profit': 80000,
            'profit_growth': 25.0,
            'margin': margin,
            'previous_margin': 17.8,
            'margin_change': 2.2
        }
    
    def _generate_cash_flow_data(self) -> Dict[str, Any]:
        return {
            'operating_cash_flow': 120000,
            'investing_cash_flow': -50000,
            'financing_cash_flow': -20000,
            'net_cash_flow': 50000,
            'cash_position': 300000
        }
    
    def _calculate_key_metrics(self) -> Dict[str, Any]:
        return {
            'gross_margin': 65.0,
            'operating_margin': 20.0,
            'net_margin': 20.0,
            'roa': 15.0,
            'roe': 18.0,
            'current_ratio': 2.5,
            'debt_to_equity': 0.3
        }
    
    def _perform_variance_analysis(self) -> Dict[str, str]:
        return {
            'revenue_variance': 'Revenue exceeded budget by 8% due to strong product sales',
            'expense_variance': 'Expenses were 3% over budget due to increased marketing spend',
            'profit_variance': 'Net profit exceeded projections by 15%'
        }
    
    def _generate_forecasts(self) -> Dict[str, Any]:
        return {
            'next_quarter_revenue': 550000,
            'next_quarter_expenses': 420000,
            'next_quarter_profit': 130000,
            'annual_revenue_forecast': 2200000,
            'annual_profit_forecast': 520000
        }
    
    def _get_reporting_period(self, report_type: str) -> str:
        if report_type == 'quarterly':
            return f"Q{((datetime.now().month - 1) // 3) + 1} {datetime.now().year}"
        elif report_type == 'monthly':
            return datetime.now().strftime("%B %Y")
        else:
            return str(datetime.now().year)
    
    def _forecast_revenue(self, scenario: str, period: str) -> Dict[str, int]:
        base_monthly = 200000
        multipliers = {'conservative': 0.9, 'realistic': 1.0, 'optimistic': 1.2}
        multiplier = multipliers.get(scenario, 1.0)
        
        months = 12 if '12' in period else 6
        return {f'month_{i+1}': int(base_monthly * multiplier * (1 + i * 0.02)) 
                for i in range(months)}
    
    def _forecast_expenses(self, scenario: str, period: str) -> Dict[str, int]:
        base_monthly = 160000
        multipliers = {'conservative': 0.95, 'realistic': 1.0, 'optimistic': 1.1}
        multiplier = multipliers.get(scenario, 1.0)
        
        months = 12 if '12' in period else 6
        return {f'month_{i+1}': int(base_monthly * multiplier * (1 + i * 0.01)) 
                for i in range(months)}
    
    def _forecast_profit(self, scenario: str, period: str) -> Dict[str, int]:
        revenue = self._forecast_revenue(scenario, period)
        expenses = self._forecast_expenses(scenario, period)
        
        return {month: revenue[month] - expenses[month] 
                for month in revenue.keys()}
    
    def _forecast_cash_flow(self, scenario: str, period: str) -> Dict[str, int]:
        profit = self._forecast_profit(scenario, period)
        # Simplified cash flow = profit + depreciation - capex
        return {month: int(profit[month] * 1.1) for month in profit.keys()}
    
    def _document_forecast_assumptions(self) -> List[str]:
        return [
            'Revenue growth rate of 2% per month',
            'Expense inflation of 1% per month',
            'No major market disruptions',
            'Stable customer acquisition rates',
            'Current pricing strategy maintained'
        ]
    
    def _calculate_expected_returns(self, investment: int, inv_type: str) -> int:
        multipliers = {
            'marketing_campaign': 3.0,
            'technology_upgrade': 2.5,
            'new_product': 4.0,
            'market_expansion': 3.5
        }
        return int(investment * multipliers.get(inv_type, 2.0))
    
    def _calculate_roi_percentage(self, investment: int, inv_type: str) -> float:
        returns = self._calculate_expected_returns(investment, inv_type)
        return ((returns - investment) / investment) * 100
    
    def _calculate_payback_period(self, investment: int, inv_type: str) -> str:
        periods = {
            'marketing_campaign': '8 months',
            'technology_upgrade': '12 months',
            'new_product': '18 months',
            'market_expansion': '15 months'
        }
        return periods.get(inv_type, '12 months')
    
    def _calculate_npv(self, investment: int, inv_type: str) -> int:
        returns = self._calculate_expected_returns(investment, inv_type)
        discount_rate = 0.1  # 10% discount rate
        periods = 2  # 2 years
        npv = (returns / ((1 + discount_rate) ** periods)) - investment
        return int(npv)
    
    def _assess_investment_risk(self, inv_type: str) -> str:
        risks = {
            'marketing_campaign': 'Medium - dependent on market response',
            'technology_upgrade': 'Low - proven technology benefits',
            'new_product': 'High - market acceptance uncertainty',
            'market_expansion': 'Medium-High - regulatory and competitive risks'
        }
        return risks.get(inv_type, 'Medium - standard business risk')
    
    def _generate_investment_recommendations(self, inv_type: str) -> List[str]:
        return [
            f'Proceed with {inv_type.replace("_", " ")} investment',
            'Monitor key performance indicators closely',
            'Establish clear success metrics and milestones',
            'Consider phased implementation to reduce risk',
            'Regular review and adjustment of strategy'
        ]
    
    def _assess_financial_health(self) -> Dict[str, str]:
        return {
            'liquidity': 'Strong - sufficient cash reserves',
            'profitability': 'Good - healthy profit margins',
            'efficiency': 'Improving - better asset utilization',
            'leverage': 'Conservative - low debt levels',
            'overall_rating': 'Healthy'
        }
    
    def _calculate_performance_metrics(self) -> Dict[str, float]:
        return {
            'revenue_growth': 15.2,
            'profit_growth': 22.8,
            'margin_improvement': 2.3,
            'asset_turnover': 1.8,
            'return_on_assets': 12.5,
            'return_on_equity': 18.7
        }
    
    def _perform_trend_analysis(self) -> Dict[str, str]:
        return {
            'revenue_trend': 'Positive - consistent growth over 12 months',
            'expense_trend': 'Controlled - expenses growing slower than revenue',
            'profitability_trend': 'Improving - margins expanding',
            'cash_flow_trend': 'Stable - positive operating cash flow'
        }
    
    def _perform_industry_benchmarking(self) -> Dict[str, str]:
        return {
            'revenue_growth': 'Above industry average (12%)',
            'profit_margins': 'In line with industry standards',
            'operational_efficiency': 'Better than industry median',
            'financial_leverage': 'Conservative compared to peers'
        }
    
    def _generate_financial_recommendations(self) -> List[str]:
        return [
            'Continue focus on revenue growth initiatives',
            'Optimize cost structure for improved margins',
            'Consider strategic investments for market expansion',
            'Maintain strong cash position for opportunities',
            'Regular financial performance monitoring and reporting'
        ]