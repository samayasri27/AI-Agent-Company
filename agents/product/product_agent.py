"""
Product Agent - Roadmap and Feature Prioritization
"""
import os
import json
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.agent_base import AgentBase
from utils.memory_system_init import get_memory_manager_for_agent


class ProductAgent(AgentBase):
    """Product Agent for roadmap and feature prioritization"""
    
    def __init__(self):
        super().__init__(
            name="Product Agent",
            role="Product Strategy & Roadmap Lead",
            department="Product"
        )
        self.capabilities = [
            "Product roadmap development",
            "Feature prioritization and scoring",
            "User story creation and management",
            "Market requirements analysis",
            "Competitive feature analysis",
            "Product metrics and KPI tracking"
        ]
        self.memory_system = get_memory_manager_for_agent('product')
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.github_api_base = "https://api.github.com"
        
    async def execute_task(self, task: str) -> Dict[str, Any]:
        """Execute product-related tasks"""
        try:
            # Parse task if it's a string
            if isinstance(task, str):
                task_dict = {'description': task, 'type': 'general'}
            else:
                task_dict = task
            
            task_type = task_dict.get('type', '').lower()
            task_description = task_dict.get('description', task if isinstance(task, str) else '')
            
            if 'roadmap' in task_description:
                return self._develop_product_roadmap(task_dict)
            elif 'prioritization' in task_description or 'feature' in task_description:
                return self._prioritize_features(task_dict)
            elif 'user story' in task_description or 'requirements' in task_description:
                return self._create_user_stories(task_dict)
            elif 'competitive' in task_description or 'analysis' in task_description:
                return self._analyze_competitive_features(task_dict)
            elif 'metrics' in task_description or 'kpi' in task_description:
                return self._track_product_metrics(task_dict)
            else:
                return self._general_product_analysis(task_dict)
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Product task processing failed: {str(e)}",
                'agent': self.name,
                'timestamp': datetime.now().isoformat()
            }
    
    def _develop_product_roadmap(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Develop comprehensive product roadmap"""
        product_area = task.get('product_area', 'AI Automation Platform')
        time_horizon = task.get('time_horizon', '12_months')
        strategic_goals = task.get('strategic_goals', [])
        
        # Search for existing roadmaps in memory
        memory_query = f"product roadmap {product_area}"
        historical_roadmaps = self.memory_system.search_knowledge(memory_query, limit=3)
        
        # Gather input data for roadmap
        roadmap_inputs = {
            'market_analysis': self._analyze_market_requirements(product_area),
            'user_feedback': self._analyze_user_feedback(product_area),
            'technical_constraints': self._assess_technical_constraints(product_area),
            'competitive_landscape': self._analyze_competitive_landscape(product_area),
            'business_objectives': self._align_business_objectives(strategic_goals),
            'resource_capacity': self._assess_resource_capacity()
        }
        
        # Develop roadmap by quarters
        roadmap = self._create_quarterly_roadmap(roadmap_inputs, time_horizon)
        
        # Add roadmap metadata
        roadmap_metadata = {
            'themes': self._identify_roadmap_themes(roadmap),
            'dependencies': self._identify_feature_dependencies(roadmap),
            'risks': self._assess_roadmap_risks(roadmap),
            'success_metrics': self._define_roadmap_metrics(roadmap),
            'review_schedule': self._create_review_schedule(time_horizon)
        }
        
        result = {
            'success': True,
            'product_area': product_area,
            'time_horizon': time_horizon,
            'roadmap': roadmap,
            'metadata': roadmap_metadata,
            'inputs': roadmap_inputs,
            'confidence_level': self._calculate_roadmap_confidence(roadmap_inputs),
            'historical_context': len(historical_roadmaps),
            'agent': self.name,
            'timestamp': datetime.now().isoformat()
        }
        
        # Store roadmap in memory
        self.memory_system.store_knowledge(
            f"Product roadmap: {product_area}",
            json.dumps(result),
            metadata={'department': 'product', 'type': 'roadmap', 'product': product_area}
        )
        
        return result
    
    def _prioritize_features(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Prioritize features using multiple frameworks"""
        features = task.get('features', [])
        prioritization_framework = task.get('framework', 'RICE')
        business_context = task.get('business_context', {})
        
        # Search for similar prioritization exercises in memory
        memory_query = f"feature prioritization {prioritization_framework}"
        historical_prioritizations = self.memory_system.search_knowledge(memory_query, limit=3)
        
        # If no features provided, get from GitHub issues or generate examples
        if not features:
            features = self._get_features_from_github() or self._generate_example_features()
        
        # Apply prioritization framework
        prioritized_features = []
        for feature in features:
            score = self._calculate_feature_score(feature, prioritization_framework, business_context)
            prioritized_features.append({
                **feature,
                'priority_score': score,
                'framework_used': prioritization_framework,
                'business_impact': self._assess_business_impact(feature, business_context),
                'technical_complexity': self._assess_technical_complexity(feature),
                'user_value': self._assess_user_value(feature),
                'effort_estimate': self._estimate_development_effort(feature)
            })
        
        # Sort by priority score
        prioritized_features.sort(key=lambda x: x.get('priority_score', 0), reverse=True)
        
        # Create prioritization insights
        insights = {
            'top_priorities': prioritized_features[:5],
            'quick_wins': self._identify_quick_wins(prioritized_features),
            'strategic_bets': self._identify_strategic_bets(prioritized_features),
            'technical_debt': self._identify_technical_debt_items(prioritized_features),
            'resource_allocation': self._recommend_resource_allocation(prioritized_features)
        }
        
        result = {
            'success': True,
            'framework': prioritization_framework,
            'total_features': len(features),
            'prioritized_features': prioritized_features,
            'insights': insights,
            'recommendations': self._generate_prioritization_recommendations(prioritized_features),
            'next_steps': self._define_prioritization_next_steps(prioritized_features),
            'historical_context': len(historical_prioritizations),
            'agent': self.name,
            'timestamp': datetime.now().isoformat()
        }
        
        # Store prioritization in memory
        self.memory_system.store_knowledge(
            f"Feature prioritization using {prioritization_framework}",
            json.dumps(result),
            metadata={'department': 'product', 'type': 'prioritization', 'framework': prioritization_framework}
        )
        
        return result
    
    def _create_user_stories(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create user stories from requirements"""
        requirements = task.get('requirements', [])
        user_personas = task.get('personas', [])
        epic_name = task.get('epic', 'Feature Development')
        
        # Search for similar user story creation in memory
        memory_query = f"user stories {epic_name}"
        historical_stories = self.memory_system.search_knowledge(memory_query, limit=3)
        
        # If no personas provided, create default ones
        if not user_personas:
            user_personas = self._create_default_personas()
        
        # Generate user stories for each requirement and persona combination
        user_stories = []
        for requirement in requirements:
            for persona in user_personas:
                stories = self._generate_stories_for_requirement(requirement, persona)
                user_stories.extend(stories)
        
        # Organize stories by epic and themes
        organized_stories = {
            'epics': self._organize_stories_by_epic(user_stories),
            'themes': self._organize_stories_by_theme(user_stories),
            'personas': self._organize_stories_by_persona(user_stories, user_personas)
        }
        
        # Add story metadata
        story_metadata = {
            'acceptance_criteria': self._generate_acceptance_criteria(user_stories),
            'story_points': self._estimate_story_points(user_stories),
            'dependencies': self._identify_story_dependencies(user_stories),
            'test_scenarios': self._generate_test_scenarios(user_stories)
        }
        
        result = {
            'success': True,
            'epic_name': epic_name,
            'total_stories': len(user_stories),
            'user_stories': user_stories,
            'organized_stories': organized_stories,
            'metadata': story_metadata,
            'personas_used': user_personas,
            'backlog_ready': self._assess_backlog_readiness(user_stories),
            'historical_context': len(historical_stories),
            'agent': self.name,
            'timestamp': datetime.now().isoformat()
        }
        
        # Store user stories in memory
        self.memory_system.store_knowledge(
            f"User stories for {epic_name}",
            json.dumps(result),
            metadata={'department': 'product', 'type': 'user_stories', 'epic': epic_name}
        )
        
        return result
    
    def _analyze_competitive_features(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze competitive features and capabilities"""
        competitors = task.get('competitors', [])
        feature_categories = task.get('categories', ['Core Features', 'Advanced Features', 'Integrations'])
        
        # Search for competitive analysis in memory
        memory_query = f"competitive analysis features"
        historical_analysis = self.memory_system.search_knowledge(memory_query, limit=3)
        
        # If no competitors specified, use default set
        if not competitors:
            competitors = self._get_default_competitors()
        
        # Analyze features for each competitor
        competitive_analysis = {}
        for competitor in competitors:
            competitive_analysis[competitor] = {
                'feature_matrix': self._create_feature_matrix(competitor, feature_categories),
                'strengths': self._identify_competitor_strengths(competitor),
                'weaknesses': self._identify_competitor_weaknesses(competitor),
                'unique_features': self._identify_unique_features(competitor),
                'pricing_model': self._analyze_pricing_model(competitor),
                'market_position': self._assess_market_position(competitor)
            }
        
        # Generate comparative insights
        comparative_insights = {
            'feature_gaps': self._identify_feature_gaps(competitive_analysis),
            'differentiation_opportunities': self._identify_differentiation_opportunities(competitive_analysis),
            'table_stakes_features': self._identify_table_stakes_features(competitive_analysis),
            'innovation_opportunities': self._identify_innovation_opportunities(competitive_analysis),
            'competitive_threats': self._assess_competitive_threats(competitive_analysis)
        }
        
        # Create strategic recommendations
        strategic_recommendations = {
            'feature_development': self._recommend_feature_development(comparative_insights),
            'positioning_strategy': self._recommend_positioning_strategy(comparative_insights),
            'pricing_strategy': self._recommend_pricing_strategy(competitive_analysis),
            'go_to_market': self._recommend_gtm_strategy(comparative_insights)
        }
        
        result = {
            'success': True,
            'competitors_analyzed': len(competitors),
            'feature_categories': feature_categories,
            'competitive_analysis': competitive_analysis,
            'comparative_insights': comparative_insights,
            'strategic_recommendations': strategic_recommendations,
            'market_landscape': self._summarize_market_landscape(competitive_analysis),
            'historical_context': len(historical_analysis),
            'agent': self.name,
            'timestamp': datetime.now().isoformat()
        }
        
        # Store competitive analysis in memory
        self.memory_system.store_knowledge(
            f"Competitive feature analysis",
            json.dumps(result),
            metadata={'department': 'product', 'type': 'competitive_analysis'}
        )
        
        return result
    
    def _track_product_metrics(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Track and analyze product metrics and KPIs"""
        metric_categories = task.get('categories', ['Usage', 'Engagement', 'Business'])
        time_period = task.get('time_period', '30_days')
        
        # Search for historical metrics in memory
        memory_query = f"product metrics {time_period}"
        historical_metrics = self.memory_system.search_knowledge(memory_query, limit=5)
        
        # Collect metrics for each category
        metrics_data = {}
        for category in metric_categories:
            metrics_data[category] = self._collect_metrics_for_category(category, time_period)
        
        # Analyze metric trends
        trend_analysis = {
            'growth_metrics': self._analyze_growth_trends(metrics_data),
            'engagement_metrics': self._analyze_engagement_trends(metrics_data),
            'business_metrics': self._analyze_business_trends(metrics_data),
            'user_behavior': self._analyze_user_behavior_trends(metrics_data)
        }
        
        # Generate insights and recommendations
        insights = {
            'key_findings': self._extract_key_metric_findings(metrics_data, trend_analysis),
            'performance_highlights': self._identify_performance_highlights(metrics_data),
            'areas_of_concern': self._identify_areas_of_concern(metrics_data),
            'improvement_opportunities': self._identify_improvement_opportunities(metrics_data)
        }
        
        # Create action items
        action_items = {
            'immediate_actions': self._recommend_immediate_actions(insights),
            'optimization_opportunities': self._recommend_optimizations(insights),
            'experiment_ideas': self._suggest_experiments(insights),
            'metric_improvements': self._suggest_metric_improvements(metrics_data)
        }
        
        result = {
            'success': True,
            'time_period': time_period,
            'metric_categories': metric_categories,
            'metrics_data': metrics_data,
            'trend_analysis': trend_analysis,
            'insights': insights,
            'action_items': action_items,
            'dashboard_summary': self._create_dashboard_summary(metrics_data),
            'historical_context': len(historical_metrics),
            'agent': self.name,
            'timestamp': datetime.now().isoformat()
        }
        
        # Store metrics analysis in memory
        self.memory_system.store_knowledge(
            f"Product metrics analysis {time_period}",
            json.dumps(result),
            metadata={'department': 'product', 'type': 'metrics_analysis', 'period': time_period}
        )
        
        return result
    
    def _general_product_analysis(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """General product analysis and insights"""
        analysis_focus = task.get('focus', 'overall_health')
        
        # Get recent product insights from memory
        memory_query = f"product analysis {analysis_focus}"
        historical_data = self.memory_system.search_knowledge(memory_query, limit=5)
        
        # Perform comprehensive product analysis
        analysis = {
            'product_health': self._assess_product_health(),
            'user_satisfaction': self._analyze_user_satisfaction(),
            'market_fit': self._assess_product_market_fit(),
            'growth_potential': self._assess_growth_potential(),
            'technical_debt': self._assess_technical_debt(),
            'competitive_position': self._assess_competitive_position()
        }
        
        result = {
            'success': True,
            'analysis_focus': analysis_focus,
            'analysis': analysis,
            'overall_score': self._calculate_overall_product_score(analysis),
            'recommendations': self._generate_product_recommendations(analysis),
            'next_steps': self._define_product_next_steps(analysis),
            'historical_context': len(historical_data),
            'agent': self.name,
            'timestamp': datetime.now().isoformat()
        }
        
        return result
    
    # GitHub integration methods
    def _get_features_from_github(self) -> List[Dict]:
        """Get features from GitHub issues"""
        if not self.github_token:
            return None
        
        try:
            headers = {'Authorization': f'token {self.github_token}'}
            # This would need to be configured with actual repo
            # For now, return None to use mock data
            return None
        except Exception:
            return None
    
    # Helper methods for roadmap development
    def _analyze_market_requirements(self, product_area: str) -> Dict:
        """Analyze market requirements for product area"""
        return {
            'customer_requests': ['API improvements', 'Mobile app', 'Advanced analytics'],
            'market_trends': ['AI integration', 'Real-time processing', 'Cloud-native'],
            'regulatory_requirements': ['Data privacy', 'Security compliance', 'Accessibility'],
            'technology_shifts': ['Microservices', 'Serverless', 'Edge computing']
        }
    
    def _analyze_user_feedback(self, product_area: str) -> Dict:
        """Analyze user feedback for product area"""
        return {
            'feature_requests': [
                {'feature': 'Advanced reporting', 'votes': 45, 'priority': 'High'},
                {'feature': 'Mobile notifications', 'votes': 32, 'priority': 'Medium'},
                {'feature': 'API rate limiting', 'votes': 28, 'priority': 'Medium'}
            ],
            'pain_points': [
                {'issue': 'Slow dashboard loading', 'frequency': 'High', 'impact': 'High'},
                {'issue': 'Complex setup process', 'frequency': 'Medium', 'impact': 'Medium'}
            ],
            'satisfaction_score': 7.8,
            'nps_score': 42
        }
    
    def _assess_technical_constraints(self, product_area: str) -> Dict:
        """Assess technical constraints"""
        return {
            'architecture_limitations': ['Monolithic structure', 'Database scalability'],
            'technology_debt': ['Legacy code', 'Outdated dependencies'],
            'resource_constraints': ['Limited backend capacity', 'Frontend framework migration'],
            'security_requirements': ['OAuth 2.0 implementation', 'Data encryption']
        }
    
    def _create_quarterly_roadmap(self, inputs: Dict, time_horizon: str) -> Dict:
        """Create quarterly roadmap based on inputs"""
        quarters = ['Q1', 'Q2', 'Q3', 'Q4'] if '12_months' in time_horizon else ['Q1', 'Q2']
        
        roadmap = {}
        for i, quarter in enumerate(quarters):
            roadmap[quarter] = {
                'theme': f'Theme {i+1}',
                'major_features': [
                    {'name': f'Feature {i+1}A', 'effort': 'Large', 'impact': 'High'},
                    {'name': f'Feature {i+1}B', 'effort': 'Medium', 'impact': 'Medium'}
                ],
                'improvements': [
                    {'name': f'Improvement {i+1}A', 'effort': 'Small', 'impact': 'Medium'}
                ],
                'technical_work': [
                    {'name': f'Tech Work {i+1}A', 'effort': 'Medium', 'impact': 'Low'}
                ],
                'milestones': [f'Milestone {i+1}'],
                'success_metrics': [f'Metric {i+1}']
            }
        
        return roadmap
    
    # Feature prioritization methods
    def _calculate_feature_score(self, feature: Dict, framework: str, context: Dict) -> float:
        """Calculate feature priority score using specified framework"""
        if framework.upper() == 'RICE':
            return self._calculate_rice_score(feature, context)
        elif framework.upper() == 'KANO':
            return self._calculate_kano_score(feature, context)
        elif framework.upper() == 'VALUE_VS_EFFORT':
            return self._calculate_value_effort_score(feature, context)
        else:
            return self._calculate_weighted_score(feature, context)
    
    def _calculate_rice_score(self, feature: Dict, context: Dict) -> float:
        """Calculate RICE score (Reach × Impact × Confidence ÷ Effort)"""
        reach = feature.get('reach', 100)  # Number of users affected
        impact = feature.get('impact', 3)  # Impact score (1-5)
        confidence = feature.get('confidence', 0.8)  # Confidence level (0-1)
        effort = feature.get('effort', 5)  # Effort in person-months
        
        return (reach * impact * confidence) / effort if effort > 0 else 0
    
    def _generate_example_features(self) -> List[Dict]:
        """Generate example features for demonstration"""
        return [
            {
                'name': 'Advanced Analytics Dashboard',
                'description': 'Comprehensive analytics with custom reports',
                'reach': 500,
                'impact': 4,
                'confidence': 0.9,
                'effort': 8,
                'category': 'Analytics'
            },
            {
                'name': 'Mobile App',
                'description': 'Native mobile application for iOS and Android',
                'reach': 800,
                'impact': 5,
                'confidence': 0.7,
                'effort': 12,
                'category': 'Platform'
            },
            {
                'name': 'API Rate Limiting',
                'description': 'Implement rate limiting for API endpoints',
                'reach': 200,
                'impact': 3,
                'confidence': 0.95,
                'effort': 3,
                'category': 'Infrastructure'
            },
            {
                'name': 'Real-time Notifications',
                'description': 'Push notifications for important events',
                'reach': 600,
                'impact': 3,
                'confidence': 0.8,
                'effort': 5,
                'category': 'Engagement'
            },
            {
                'name': 'Single Sign-On (SSO)',
                'description': 'Enterprise SSO integration',
                'reach': 300,
                'impact': 4,
                'confidence': 0.85,
                'effort': 6,
                'category': 'Security'
            }
        ]
    
    def _identify_quick_wins(self, features: List[Dict]) -> List[Dict]:
        """Identify quick win features (high impact, low effort)"""
        quick_wins = []
        for feature in features:
            effort = feature.get('effort', 10)
            impact = feature.get('impact', 1)
            if effort <= 3 and impact >= 3:
                quick_wins.append(feature)
        return quick_wins[:3]
    
    def _identify_strategic_bets(self, features: List[Dict]) -> List[Dict]:
        """Identify strategic bet features (high impact, high effort)"""
        strategic_bets = []
        for feature in features:
            effort = feature.get('effort', 1)
            impact = feature.get('impact', 1)
            if effort >= 8 and impact >= 4:
                strategic_bets.append(feature)
        return strategic_bets[:3]
    
    # User story creation methods
    def _create_default_personas(self) -> List[Dict]:
        """Create default user personas"""
        return [
            {
                'name': 'Business User',
                'role': 'Manager',
                'goals': ['Increase efficiency', 'Reduce costs', 'Improve visibility'],
                'pain_points': ['Manual processes', 'Lack of insights', 'Time-consuming tasks']
            },
            {
                'name': 'Technical User',
                'role': 'Developer',
                'goals': ['Easy integration', 'Reliable APIs', 'Good documentation'],
                'pain_points': ['Complex setup', 'Poor documentation', 'Limited customization']
            },
            {
                'name': 'Admin User',
                'role': 'Administrator',
                'goals': ['System control', 'User management', 'Security compliance'],
                'pain_points': ['Security concerns', 'User onboarding', 'System maintenance']
            }
        ]
    
    def _generate_stories_for_requirement(self, requirement: str, persona: Dict) -> List[Dict]:
        """Generate user stories for a requirement and persona"""
        return [
            {
                'id': f"US-{hash(requirement + persona['name']) % 1000}",
                'title': f"{persona['name']} - {requirement}",
                'story': f"As a {persona['role']}, I want to {requirement.lower()} so that I can achieve my goals",
                'persona': persona['name'],
                'acceptance_criteria': [
                    f"Given I am a {persona['role']}",
                    f"When I {requirement.lower()}",
                    f"Then I should see the expected result"
                ],
                'story_points': 3,
                'priority': 'Medium',
                'epic': 'Feature Development'
            }
        ]
    
    # Mock data and helper methods
    def _get_default_competitors(self) -> List[str]:
        """Get default competitors for analysis"""
        return ['Competitor A', 'Competitor B', 'Competitor C', 'Competitor D']
    
    def _create_feature_matrix(self, competitor: str, categories: List[str]) -> Dict:
        """Create feature comparison matrix"""
        matrix = {}
        for category in categories:
            matrix[category] = {
                'has_feature': True,
                'quality_score': 7.5,
                'unique_aspects': [f'{competitor} unique aspect for {category}']
            }
        return matrix
    
    def _collect_metrics_for_category(self, category: str, period: str) -> Dict:
        """Collect metrics for specific category"""
        if category == 'Usage':
            return {
                'daily_active_users': 1250,
                'monthly_active_users': 4500,
                'session_duration': 12.5,
                'page_views': 25000
            }
        elif category == 'Engagement':
            return {
                'feature_adoption_rate': 0.65,
                'user_retention_rate': 0.78,
                'time_to_value': 3.2,
                'support_ticket_volume': 45
            }
        elif category == 'Business':
            return {
                'conversion_rate': 0.035,
                'customer_lifetime_value': 2400,
                'monthly_recurring_revenue': 125000,
                'churn_rate': 0.05
            }
        else:
            return {'placeholder_metric': 100}
    
    def _assess_product_health(self) -> Dict:
        """Assess overall product health"""
        return {
            'health_score': 8.2,
            'user_satisfaction': 7.8,
            'technical_health': 7.5,
            'business_performance': 8.5,
            'market_position': 7.9
        }
    
    def _calculate_overall_product_score(self, analysis: Dict) -> float:
        """Calculate overall product score"""
        scores = []
        for category, data in analysis.items():
            if isinstance(data, dict) and 'score' in str(data):
                # Extract numeric scores from analysis
                scores.append(7.5)  # Mock score
        return sum(scores) / len(scores) if scores else 7.5