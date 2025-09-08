"""
Marketing Agent - Campaign creation and marketing materials
"""
import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.agent_base import AgentBase


class MarketingAgent(AgentBase):
    """Marketing Agent for campaign creation and marketing materials"""
    
    def __init__(self):
        super().__init__(
            name="Marketing Agent",
            role="Campaign & Content Strategy",
            department="Marketing"
        )
        self.capabilities = [
            "Campaign strategy development",
            "Marketing material creation",
            "Brand messaging and positioning",
            "Content marketing planning",
            "Social media strategy",
            "Marketing analytics and reporting"
        ]
    
    async def execute_task(self, task: str) -> Dict[str, Any]:
        """Execute marketing-related tasks"""
        try:
            if isinstance(task, str):
                task_dict = {'description': task, 'type': 'general'}
            else:
                task_dict = task
            
            task_description = task_dict.get('description', '').lower()
            
            if 'campaign' in task_description:
                return self._create_marketing_campaign(task_dict)
            elif 'pitch' in task_description or 'presentation' in task_description:
                return self._create_pitch_deck(task_dict)
            elif 'content' in task_description:
                return self._create_content_strategy(task_dict)
            elif 'social media' in task_description:
                return self._create_social_media_strategy(task_dict)
            else:
                return self._general_marketing_analysis(task_dict)
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Marketing task processing failed: {str(e)}",
                'agent': self.name,
                'timestamp': datetime.now().isoformat()
            }
    
    def _create_marketing_campaign(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive marketing campaign"""
        campaign_type = task.get('campaign_type', 'product_launch')
        target_audience = task.get('target_audience', 'general_consumers')
        budget = task.get('budget', 50000)
        duration = task.get('duration', '3_months')
        
        # Generate campaign strategy
        campaign = {
            'campaign_name': f"{campaign_type.replace('_', ' ').title()} Campaign",
            'objective': self._generate_campaign_objective(campaign_type),
            'target_audience': self._analyze_target_audience(target_audience),
            'messaging': self._create_messaging_strategy(campaign_type, target_audience),
            'channels': self._select_marketing_channels(target_audience, budget),
            'timeline': self._create_campaign_timeline(duration),
            'budget_allocation': self._allocate_budget(budget),
            'kpis': self._define_campaign_kpis(campaign_type),
            'creative_concepts': self._generate_creative_concepts(campaign_type)
        }
        
        result = {
            'success': True,
            'campaign': campaign,
            'campaign_type': campaign_type,
            'estimated_reach': self._estimate_campaign_reach(campaign),
            'expected_roi': self._calculate_expected_roi(campaign, budget),
            'agent': self.name,
            'timestamp': datetime.now().isoformat()
        }
        
        # Generate campaign document
        try:
            doc_content = {
                'title': f'Marketing Campaign Strategy: {campaign["campaign_name"]}',
                'author': self.name,
                'subject': 'Marketing Campaign Plan',
                'executive_summary': f'Comprehensive marketing campaign strategy for {campaign_type} targeting {target_audience} with ${budget:,} budget over {duration}.',
                'sections': [
                    {
                        'title': 'Campaign Overview',
                        'content': f'Campaign Name: {campaign["campaign_name"]}\\nObjective: {campaign["objective"]}\\nDuration: {duration}\\nBudget: ${budget:,}'
                    },
                    {
                        'title': 'Target Audience Analysis',
                        'bullet_points': [
                            f"Primary Audience: {campaign['target_audience']['primary']}",
                            f"Demographics: {campaign['target_audience']['demographics']}",
                            f"Psychographics: {campaign['target_audience']['psychographics']}",
                            f"Pain Points: {', '.join(campaign['target_audience']['pain_points'])}"
                        ]
                    },
                    {
                        'title': 'Messaging Strategy',
                        'content': f"Core Message: {campaign['messaging']['core_message']}\\n\\nKey Messages:\\n" + 
                                 '\\n'.join([f"• {msg}" for msg in campaign['messaging']['key_messages']])
                    },
                    {
                        'title': 'Marketing Channels',
                        'bullet_points': [f"{channel}: {details}" for channel, details in campaign['channels'].items()]
                    },
                    {
                        'title': 'Budget Allocation',
                        'table': {
                            'headers': ['Channel', 'Budget', 'Percentage'],
                            'rows': [[channel, f"${amount:,}", f"{(amount/budget)*100:.1f}%"] 
                                   for channel, amount in campaign['budget_allocation'].items()]
                        }
                    },
                    {
                        'title': 'Success Metrics (KPIs)',
                        'bullet_points': campaign['kpis']
                    }
                ]
            }
            
            filename = f"marketing_campaign_{campaign_type}_{datetime.now().strftime('%Y%m%d')}"
            docx_path = self.create_document(doc_content, 'docx', filename)
            
            if docx_path:
                result['generated_files'] = [docx_path]
                self.log(f"Generated marketing campaign document: {filename}.docx")
                
        except Exception as e:
            self.log(f"Error generating campaign document: {str(e)}")
            result['document_generation_error'] = str(e)
        
        return result
    
    def _create_pitch_deck(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create pitch deck presentation"""
        pitch_type = task.get('pitch_type', 'product_pitch')
        audience = task.get('audience', 'investors')
        product_name = task.get('product_name', 'Our Product')
        
        # Generate slide content
        slides = [
            {
                'layout': 'title_slide',
                'title': f'{product_name} - {pitch_type.replace("_", " ").title()}',
                'content': f'Presented by {self.name}\\n{datetime.now().strftime("%B %Y")}'
            },
            {
                'title': 'Problem Statement',
                'bullet_points': [
                    'Market gap identification',
                    'Customer pain points analysis',
                    'Current solution limitations',
                    'Opportunity size quantification'
                ]
            },
            {
                'title': 'Our Solution',
                'bullet_points': [
                    f'{product_name} addresses key market needs',
                    'Unique value proposition',
                    'Competitive advantages',
                    'Technology differentiation'
                ]
            },
            {
                'title': 'Market Opportunity',
                'bullet_points': [
                    'Total Addressable Market (TAM): $10B+',
                    'Serviceable Addressable Market (SAM): $2B+',
                    'Target market segments',
                    'Growth projections'
                ]
            },
            {
                'title': 'Business Model',
                'bullet_points': [
                    'Revenue streams',
                    'Pricing strategy',
                    'Customer acquisition cost',
                    'Lifetime value projections'
                ]
            },
            {
                'title': 'Go-to-Market Strategy',
                'bullet_points': [
                    'Target customer segments',
                    'Marketing channels',
                    'Sales strategy',
                    'Partnership opportunities'
                ]
            },
            {
                'title': 'Financial Projections',
                'bullet_points': [
                    'Revenue forecast (3-year)',
                    'Key metrics and KPIs',
                    'Funding requirements',
                    'Expected ROI'
                ]
            },
            {
                'title': 'Next Steps',
                'bullet_points': [
                    'Immediate priorities',
                    'Milestone timeline',
                    'Resource requirements',
                    'Call to action'
                ]
            }
        ]
        
        result = {
            'success': True,
            'pitch_deck': {
                'title': f'{product_name} - {pitch_type.replace("_", " ").title()}',
                'slides': slides,
                'total_slides': len(slides),
                'target_audience': audience
            },
            'agent': self.name,
            'timestamp': datetime.now().isoformat()
        }
        
        # Generate PowerPoint presentation
        try:
            filename = f"pitch_deck_{product_name.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d')}"
            pptx_path = self.create_document({'slides': slides}, 'pptx', filename)
            
            if pptx_path:
                result['generated_files'] = [pptx_path]
                self.log(f"Generated pitch deck presentation: {filename}.pptx")
                
        except Exception as e:
            self.log(f"Error generating pitch deck: {str(e)}")
            result['document_generation_error'] = str(e)
        
        return result
    
    def _create_content_strategy(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create content marketing strategy"""
        content_type = task.get('content_type', 'blog_content')
        industry = task.get('industry', 'technology')
        duration = task.get('duration', '6_months')
        
        strategy = {
            'content_pillars': self._define_content_pillars(industry),
            'content_calendar': self._create_content_calendar(duration),
            'distribution_channels': self._select_content_channels(),
            'content_formats': self._recommend_content_formats(content_type),
            'seo_strategy': self._create_seo_strategy(industry),
            'performance_metrics': self._define_content_metrics()
        }
        
        return {
            'success': True,
            'content_strategy': strategy,
            'content_type': content_type,
            'industry': industry,
            'duration': duration,
            'agent': self.name,
            'timestamp': datetime.now().isoformat()
        }
    
    def _create_social_media_strategy(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create social media marketing strategy"""
        platforms = task.get('platforms', ['linkedin', 'twitter', 'facebook'])
        brand_voice = task.get('brand_voice', 'professional')
        
        strategy = {
            'platform_strategy': {platform: self._create_platform_strategy(platform, brand_voice) 
                                for platform in platforms},
            'content_themes': self._generate_social_content_themes(),
            'posting_schedule': self._create_posting_schedule(platforms),
            'engagement_strategy': self._create_engagement_strategy(),
            'influencer_strategy': self._create_influencer_strategy(),
            'social_advertising': self._plan_social_advertising(platforms)
        }
        
        return {
            'success': True,
            'social_media_strategy': strategy,
            'platforms': platforms,
            'brand_voice': brand_voice,
            'agent': self.name,
            'timestamp': datetime.now().isoformat()
        }
    
    def _general_marketing_analysis(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """General marketing analysis"""
        analysis_type = task.get('analysis_type', 'market_analysis')
        
        analysis = {
            'market_trends': self._analyze_market_trends(),
            'competitor_analysis': self._analyze_competitors(),
            'customer_insights': self._analyze_customer_insights(),
            'brand_positioning': self._analyze_brand_positioning(),
            'marketing_mix': self._analyze_marketing_mix(),
            'recommendations': self._generate_marketing_recommendations()
        }
        
        return {
            'success': True,
            'analysis': analysis,
            'analysis_type': analysis_type,
            'agent': self.name,
            'timestamp': datetime.now().isoformat()
        }
    
    # Helper methods for generating marketing content
    def _generate_campaign_objective(self, campaign_type: str) -> str:
        objectives = {
            'product_launch': 'Introduce new product to market and drive initial adoption',
            'brand_awareness': 'Increase brand recognition and market presence',
            'lead_generation': 'Generate qualified leads for sales team',
            'customer_retention': 'Improve customer loyalty and reduce churn',
            'market_expansion': 'Enter new market segments or geographic regions'
        }
        return objectives.get(campaign_type, 'Drive business growth through strategic marketing')
    
    def _analyze_target_audience(self, audience: str) -> Dict[str, Any]:
        return {
            'primary': audience,
            'demographics': 'Age 25-45, College-educated, Middle to high income',
            'psychographics': 'Tech-savvy, Value-conscious, Quality-focused',
            'pain_points': ['Time constraints', 'Budget limitations', 'Quality concerns'],
            'preferred_channels': ['Digital', 'Social Media', 'Email', 'Content Marketing']
        }
    
    def _create_messaging_strategy(self, campaign_type: str, audience: str) -> Dict[str, Any]:
        return {
            'core_message': f'Transform your business with our innovative solution',
            'key_messages': [
                'Proven results and ROI',
                'Easy implementation and use',
                'Expert support and guidance',
                'Competitive pricing and value'
            ],
            'tone_of_voice': 'Professional, approachable, and results-focused'
        }
    
    def _select_marketing_channels(self, audience: str, budget: int) -> Dict[str, str]:
        return {
            'digital_advertising': 'Google Ads, Facebook Ads, LinkedIn Ads',
            'content_marketing': 'Blog posts, whitepapers, case studies',
            'social_media': 'LinkedIn, Twitter, Facebook engagement',
            'email_marketing': 'Nurture campaigns and newsletters',
            'events': 'Webinars, conferences, trade shows',
            'partnerships': 'Strategic alliances and co-marketing'
        }
    
    def _create_campaign_timeline(self, duration: str) -> Dict[str, str]:
        return {
            'phase_1': 'Planning and creative development (Weeks 1-2)',
            'phase_2': 'Campaign launch and initial push (Weeks 3-6)',
            'phase_3': 'Optimization and scaling (Weeks 7-10)',
            'phase_4': 'Analysis and reporting (Weeks 11-12)'
        }
    
    def _allocate_budget(self, total_budget: int) -> Dict[str, int]:
        return {
            'digital_advertising': int(total_budget * 0.4),
            'content_creation': int(total_budget * 0.2),
            'social_media': int(total_budget * 0.15),
            'email_marketing': int(total_budget * 0.1),
            'events': int(total_budget * 0.1),
            'contingency': int(total_budget * 0.05)
        }
    
    def _define_campaign_kpis(self, campaign_type: str) -> List[str]:
        return [
            'Brand awareness lift',
            'Lead generation volume',
            'Cost per acquisition (CPA)',
            'Return on ad spend (ROAS)',
            'Engagement rates',
            'Conversion rates',
            'Customer lifetime value'
        ]
    
    def _generate_creative_concepts(self, campaign_type: str) -> List[str]:
        return [
            'Hero video showcasing product benefits',
            'Customer success story testimonials',
            'Interactive product demonstrations',
            'Behind-the-scenes company culture content',
            'Industry thought leadership pieces'
        ]
    
    def _estimate_campaign_reach(self, campaign: Dict) -> Dict[str, int]:
        return {
            'total_impressions': 500000,
            'unique_reach': 150000,
            'engagement_estimate': 15000,
            'lead_estimate': 1500
        }
    
    def _calculate_expected_roi(self, campaign: Dict, budget: int) -> Dict[str, Any]:
        return {
            'expected_revenue': budget * 3,
            'roi_percentage': 200,
            'payback_period': '6 months',
            'confidence_level': 'Medium-High'
        }
    
    def _define_content_pillars(self, industry: str) -> List[str]:
        return [
            'Industry insights and trends',
            'Product education and tutorials',
            'Customer success stories',
            'Company culture and values',
            'Thought leadership content'
        ]
    
    def _create_content_calendar(self, duration: str) -> Dict[str, Any]:
        return {
            'posting_frequency': '3-4 posts per week',
            'content_mix': '40% educational, 30% promotional, 20% entertainment, 10% user-generated',
            'seasonal_campaigns': 'Holiday promotions, industry events, product launches',
            'content_themes': 'Weekly themes aligned with business objectives'
        }
    
    def _select_content_channels(self) -> List[str]:
        return [
            'Company blog',
            'Social media platforms',
            'Email newsletters',
            'Industry publications',
            'Partner channels',
            'Video platforms'
        ]
    
    def _recommend_content_formats(self, content_type: str) -> List[str]:
        return [
            'Blog articles and posts',
            'Video content and tutorials',
            'Infographics and visual content',
            'Podcasts and audio content',
            'Interactive content and tools',
            'Case studies and whitepapers'
        ]
    
    def _create_seo_strategy(self, industry: str) -> Dict[str, Any]:
        return {
            'keyword_strategy': 'Focus on long-tail industry keywords',
            'content_optimization': 'SEO-optimized blog posts and landing pages',
            'technical_seo': 'Site speed, mobile optimization, schema markup',
            'link_building': 'Guest posting, industry partnerships, PR outreach'
        }
    
    def _define_content_metrics(self) -> List[str]:
        return [
            'Organic traffic growth',
            'Content engagement rates',
            'Social shares and mentions',
            'Lead generation from content',
            'Search ranking improvements',
            'Time on page and bounce rate'
        ]
    
    def _create_platform_strategy(self, platform: str, brand_voice: str) -> Dict[str, Any]:
        strategies = {
            'linkedin': {
                'content_focus': 'Professional insights, industry news, thought leadership',
                'posting_frequency': 'Daily',
                'engagement_strategy': 'Comment on industry posts, share valuable content'
            },
            'twitter': {
                'content_focus': 'Real-time updates, industry conversations, quick tips',
                'posting_frequency': '3-5 times daily',
                'engagement_strategy': 'Join trending conversations, respond quickly'
            },
            'facebook': {
                'content_focus': 'Community building, behind-the-scenes, customer stories',
                'posting_frequency': '1-2 times daily',
                'engagement_strategy': 'Build community, respond to comments and messages'
            }
        }
        return strategies.get(platform, {'content_focus': 'General business content', 'posting_frequency': 'Daily'})
    
    def _generate_social_content_themes(self) -> List[str]:
        return [
            'Monday Motivation',
            'Tutorial Tuesday',
            'Wisdom Wednesday',
            'Throwback Thursday',
            'Feature Friday',
            'Weekend Inspiration'
        ]
    
    def _create_posting_schedule(self, platforms: List[str]) -> Dict[str, str]:
        return {
            'optimal_times': 'Weekdays 9-11 AM and 2-4 PM',
            'frequency': 'Daily posting with peak engagement times',
            'content_calendar': 'Monthly planning with weekly adjustments',
            'automation': 'Scheduled posts with real-time engagement'
        }
    
    def _create_engagement_strategy(self) -> Dict[str, str]:
        return {
            'response_time': 'Within 2 hours during business hours',
            'community_management': 'Proactive engagement with followers',
            'user_generated_content': 'Encourage and share customer content',
            'influencer_engagement': 'Build relationships with industry influencers'
        }
    
    def _create_influencer_strategy(self) -> Dict[str, Any]:
        return {
            'influencer_tiers': 'Micro-influencers (1K-100K), Industry experts',
            'collaboration_types': 'Sponsored posts, product reviews, partnerships',
            'selection_criteria': 'Audience alignment, engagement rates, authenticity',
            'campaign_goals': 'Brand awareness, credibility, reach expansion'
        }
    
    def _plan_social_advertising(self, platforms: List[str]) -> Dict[str, Any]:
        return {
            'ad_objectives': 'Brand awareness, lead generation, website traffic',
            'targeting_strategy': 'Lookalike audiences, interest-based, retargeting',
            'budget_allocation': 'Test small, scale successful campaigns',
            'creative_strategy': 'A/B test ad formats, messaging, visuals'
        }
    
    def _analyze_market_trends(self) -> List[str]:
        return [
            'Digital transformation acceleration',
            'Increased focus on customer experience',
            'Rise of personalization and AI',
            'Sustainability and social responsibility',
            'Remote work and digital collaboration'
        ]
    
    def _analyze_competitors(self) -> Dict[str, Any]:
        return {
            'direct_competitors': 'Companies offering similar solutions',
            'indirect_competitors': 'Alternative solutions to customer problems',
            'competitive_advantages': 'Unique value propositions and differentiators',
            'market_gaps': 'Opportunities not addressed by competitors'
        }
    
    def _analyze_customer_insights(self) -> Dict[str, Any]:
        return {
            'customer_journey': 'Awareness → Consideration → Decision → Retention',
            'pain_points': 'Cost, complexity, time constraints, quality concerns',
            'motivations': 'Efficiency, growth, competitive advantage, ROI',
            'preferred_channels': 'Digital, referrals, content, social proof'
        }
    
    def _analyze_brand_positioning(self) -> Dict[str, str]:
        return {
            'brand_promise': 'Deliver exceptional value through innovation',
            'unique_value_proposition': 'The only solution that combines X, Y, and Z',
            'brand_personality': 'Innovative, reliable, customer-focused',
            'competitive_positioning': 'Premium quality at competitive prices'
        }
    
    def _analyze_marketing_mix(self) -> Dict[str, str]:
        return {
            'product': 'Feature-rich solution addressing key market needs',
            'price': 'Competitive pricing with clear value demonstration',
            'place': 'Multi-channel distribution strategy',
            'promotion': 'Integrated marketing communications approach'
        }
    
    def _generate_marketing_recommendations(self) -> List[str]:
        return [
            'Invest in digital marketing capabilities',
            'Develop customer-centric content strategy',
            'Implement marketing automation tools',
            'Focus on data-driven decision making',
            'Build strong brand community',
            'Optimize customer acquisition funnel'
        ]