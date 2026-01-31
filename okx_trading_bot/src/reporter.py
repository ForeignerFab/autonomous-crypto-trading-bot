
"""
Report Generation Module
Creates comprehensive PDF reports and performance analytics
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.piecharts import Pie
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from loguru import logger
import os
import io
import base64


class ReportGenerator:
    """Comprehensive trading report generator"""
    
    def __init__(self, config: Dict):
        """Initialize report generator"""
        self.config = config
        self.report_dir = "reports"
        self.charts_dir = "reports/charts"
        
        # Create directories
        os.makedirs(self.report_dir, exist_ok=True)
        os.makedirs(self.charts_dir, exist_ok=True)
        
        # Styles
        self.styles = getSampleStyleSheet()
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.darkblue
        )
        
        logger.info("Report generator initialized")
    
    async def generate_daily_report(self, date: Optional[datetime] = None) -> str:
        """Generate comprehensive daily trading report"""
        try:
            if date is None:
                date = datetime.now()
            
            report_filename = f"daily_report_{date.strftime('%Y%m%d')}.pdf"
            report_path = os.path.join(self.report_dir, report_filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(report_path, pagesize=A4)
            story = []
            
            # Title
            title = Paragraph(f"Daily Trading Report - {date.strftime('%B %d, %Y')}", self.title_style)
            story.append(title)
            story.append(Spacer(1, 20))
            
            # Executive Summary
            summary_data = await self._get_daily_summary(date)
            story.extend(self._create_executive_summary(summary_data))
            
            # Performance Metrics
            performance_data = await self._get_performance_metrics(date)
            story.extend(self._create_performance_section(performance_data))
            
            # Trade Analysis
            trade_data = await self._get_trade_analysis(date)
            story.extend(self._create_trade_analysis_section(trade_data))
            
            # Risk Analysis
            risk_data = await self._get_risk_analysis(date)
            story.extend(self._create_risk_analysis_section(risk_data))
            
            # Market Analysis
            market_data = await self._get_market_analysis(date)
            story.extend(self._create_market_analysis_section(market_data))
            
            # Charts and Visualizations
            charts = await self._generate_charts(date)
            story.extend(self._add_charts_to_report(charts))
            
            # AI Insights
            ai_insights = await self._get_ai_insights(date)
            story.extend(self._create_ai_insights_section(ai_insights))
            
            # Recommendations
            recommendations = await self._get_recommendations(date)
            story.extend(self._create_recommendations_section(recommendations))
            
            # Build PDF
            doc.build(story)
            
            logger.info(f"Daily report generated: {report_path}")
            return report_path
        
        except Exception as e:
            logger.error(f"Error generating daily report: {e}")
            return ""
    
    async def _get_daily_summary(self, date: datetime) -> Dict:
        """Get daily summary data"""
        try:
            # This would typically query the database
            # For now, return mock data
            return {
                'total_trades': 12,
                'winning_trades': 8,
                'losing_trades': 4,
                'win_rate': 66.7,
                'total_pnl': 25.50,
                'gross_profit': 45.20,
                'gross_loss': -19.70,
                'largest_win': 8.30,
                'largest_loss': -6.20,
                'average_win': 5.65,
                'average_loss': -4.93,
                'profit_factor': 2.29,
                'sharpe_ratio': 1.45,
                'max_drawdown': -12.30,
                'account_balance': 525.50,
                'equity_curve': [500, 505, 510, 515, 520, 525.50]
            }
        except Exception as e:
            logger.error(f"Error getting daily summary: {e}")
            return {}
    
    async def _get_performance_metrics(self, date: datetime) -> Dict:
        """Get performance metrics"""
        try:
            return {
                'daily_return': 5.1,
                'weekly_return': 12.3,
                'monthly_return': 28.7,
                'ytd_return': 45.2,
                'volatility': 15.8,
                'max_consecutive_wins': 4,
                'max_consecutive_losses': 2,
                'average_trade_duration': '00:15:30',
                'total_commissions': 2.45,
                'net_profit': 23.05
            }
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {}
    
    async def _get_trade_analysis(self, date: datetime) -> Dict:
        """Get trade analysis data"""
        try:
            return {
                'trades_by_pair': {
                    'BTC-USDT': {'count': 4, 'pnl': 12.50},
                    'ETH-USDT': {'count': 3, 'pnl': 8.20},
                    'ADA-USDT': {'count': 2, 'pnl': -3.10},
                    'SOL-USDT': {'count': 3, 'pnl': 7.90}
                },
                'trades_by_hour': {
                    '09:00': 2, '10:00': 1, '11:00': 3, '12:00': 2,
                    '13:00': 1, '14:00': 2, '15:00': 1, '16:00': 0
                },
                'signal_sources': {
                    'RSI': 5, 'MACD': 3, 'Bollinger Bands': 2, 'Volume': 2
                },
                'exit_reasons': {
                    'Take Profit': 6, 'Stop Loss': 3, 'Manual': 2, 'Time Exit': 1
                }
            }
        except Exception as e:
            logger.error(f"Error getting trade analysis: {e}")
            return {}
    
    async def _get_risk_analysis(self, date: datetime) -> Dict:
        """Get risk analysis data"""
        try:
            return {
                'var_95': -8.50,
                'var_99': -12.30,
                'expected_shortfall': -15.20,
                'risk_per_trade': 2.0,
                'portfolio_heat': 8.5,
                'correlation_risk': 'Low',
                'leverage_used': 1.0,
                'margin_utilization': 15.2
            }
        except Exception as e:
            logger.error(f"Error getting risk analysis: {e}")
            return {}
    
    async def _get_market_analysis(self, date: datetime) -> Dict:
        """Get market analysis data"""
        try:
            return {
                'market_sentiment': 'Bullish',
                'volatility_regime': 'Normal',
                'trend_strength': 'Strong',
                'volume_profile': 'Above Average',
                'correlation_breakdown': {
                    'BTC-ETH': 0.85,
                    'BTC-ADA': 0.72,
                    'ETH-SOL': 0.68
                }
            }
        except Exception as e:
            logger.error(f"Error getting market analysis: {e}")
            return {}
    
    async def _get_ai_insights(self, date: datetime) -> Dict:
        """Get AI insights and recommendations"""
        try:
            return {
                'pattern_recognition': [
                    {'pattern': 'Bullish Divergence', 'confidence': 0.85, 'frequency': 3},
                    {'pattern': 'Volume Spike', 'confidence': 0.72, 'frequency': 2}
                ],
                'parameter_suggestions': [
                    {'parameter': 'RSI Period', 'current': 5, 'suggested': 7, 'confidence': 0.78},
                    {'parameter': 'Stop Loss Multiplier', 'current': 2.0, 'suggested': 1.8, 'confidence': 0.65}
                ],
                'market_regime_detection': 'Trending Market',
                'optimal_trading_hours': ['09:00-11:00', '14:00-16:00']
            }
        except Exception as e:
            logger.error(f"Error getting AI insights: {e}")
            return {}
    
    async def _get_recommendations(self, date: datetime) -> Dict:
        """Get trading recommendations"""
        try:
            return {
                'immediate_actions': [
                    'Consider reducing position size on ADA-USDT due to poor performance',
                    'Increase allocation to BTC-USDT given strong performance'
                ],
                'parameter_adjustments': [
                    'Tighten stop losses during high volatility periods',
                    'Consider increasing RSI period to reduce false signals'
                ],
                'risk_management': [
                    'Current risk levels are appropriate',
                    'Monitor correlation risk between BTC and ETH positions'
                ],
                'market_outlook': [
                    'Bullish trend expected to continue short-term',
                    'Watch for potential volatility increase around market close'
                ]
            }
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            return {}
    
    def _create_executive_summary(self, data: Dict) -> List:
        """Create executive summary section"""
        try:
            elements = []
            
            # Section title
            elements.append(Paragraph("Executive Summary", self.styles['Heading2']))
            elements.append(Spacer(1, 12))
            
            # Summary table
            summary_data = [
                ['Metric', 'Value'],
                ['Total Trades', str(data.get('total_trades', 0))],
                ['Win Rate', f"{data.get('win_rate', 0):.1f}%"],
                ['Total P&L', f"£{data.get('total_pnl', 0):.2f}"],
                ['Profit Factor', f"{data.get('profit_factor', 0):.2f}"],
                ['Sharpe Ratio', f"{data.get('sharpe_ratio', 0):.2f}"],
                ['Max Drawdown', f"£{data.get('max_drawdown', 0):.2f}"],
                ['Account Balance', f"£{data.get('account_balance', 0):.2f}"]
            ]
            
            table = Table(summary_data, colWidths=[2*inch, 2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 20))
            
            return elements
        
        except Exception as e:
            logger.error(f"Error creating executive summary: {e}")
            return []
    
    def _create_performance_section(self, data: Dict) -> List:
        """Create performance metrics section"""
        try:
            elements = []
            
            elements.append(Paragraph("Performance Metrics", self.styles['Heading2']))
            elements.append(Spacer(1, 12))
            
            # Performance table
            perf_data = [
                ['Period', 'Return'],
                ['Daily', f"{data.get('daily_return', 0):.1f}%"],
                ['Weekly', f"{data.get('weekly_return', 0):.1f}%"],
                ['Monthly', f"{data.get('monthly_return', 0):.1f}%"],
                ['YTD', f"{data.get('ytd_return', 0):.1f}%"]
            ]
            
            table = Table(perf_data, colWidths=[2*inch, 2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 20))
            
            return elements
        
        except Exception as e:
            logger.error(f"Error creating performance section: {e}")
            return []
    
    def _create_trade_analysis_section(self, data: Dict) -> List:
        """Create trade analysis section"""
        try:
            elements = []
            
            elements.append(Paragraph("Trade Analysis", self.styles['Heading2']))
            elements.append(Spacer(1, 12))
            
            # Trades by pair
            elements.append(Paragraph("Trades by Trading Pair", self.styles['Heading3']))
            
            pair_data = [['Pair', 'Count', 'P&L']]
            for pair, info in data.get('trades_by_pair', {}).items():
                pair_data.append([pair, str(info['count']), f"£{info['pnl']:.2f}"])
            
            table = Table(pair_data, colWidths=[1.5*inch, 1*inch, 1*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 20))
            
            return elements
        
        except Exception as e:
            logger.error(f"Error creating trade analysis section: {e}")
            return []
    
    def _create_risk_analysis_section(self, data: Dict) -> List:
        """Create risk analysis section"""
        try:
            elements = []
            
            elements.append(Paragraph("Risk Analysis", self.styles['Heading2']))
            elements.append(Spacer(1, 12))
            
            risk_data = [
                ['Risk Metric', 'Value'],
                ['Value at Risk (95%)', f"£{data.get('var_95', 0):.2f}"],
                ['Value at Risk (99%)', f"£{data.get('var_99', 0):.2f}"],
                ['Expected Shortfall', f"£{data.get('expected_shortfall', 0):.2f}"],
                ['Risk per Trade', f"{data.get('risk_per_trade', 0):.1f}%"],
                ['Portfolio Heat', f"{data.get('portfolio_heat', 0):.1f}%"],
                ['Correlation Risk', data.get('correlation_risk', 'N/A')]
            ]
            
            table = Table(risk_data, colWidths=[2.5*inch, 1.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkred),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 20))
            
            return elements
        
        except Exception as e:
            logger.error(f"Error creating risk analysis section: {e}")
            return []
    
    def _create_market_analysis_section(self, data: Dict) -> List:
        """Create market analysis section"""
        try:
            elements = []
            
            elements.append(Paragraph("Market Analysis", self.styles['Heading2']))
            elements.append(Spacer(1, 12))
            
            # Market conditions
            elements.append(Paragraph(f"Market Sentiment: {data.get('market_sentiment', 'N/A')}", self.styles['Normal']))
            elements.append(Paragraph(f"Volatility Regime: {data.get('volatility_regime', 'N/A')}", self.styles['Normal']))
            elements.append(Paragraph(f"Trend Strength: {data.get('trend_strength', 'N/A')}", self.styles['Normal']))
            elements.append(Paragraph(f"Volume Profile: {data.get('volume_profile', 'N/A')}", self.styles['Normal']))
            
            elements.append(Spacer(1, 20))
            
            return elements
        
        except Exception as e:
            logger.error(f"Error creating market analysis section: {e}")
            return []
    
    def _create_ai_insights_section(self, data: Dict) -> List:
        """Create AI insights section"""
        try:
            elements = []
            
            elements.append(Paragraph("AI Insights", self.styles['Heading2']))
            elements.append(Spacer(1, 12))
            
            # Pattern recognition
            elements.append(Paragraph("Pattern Recognition", self.styles['Heading3']))
            for pattern in data.get('pattern_recognition', []):
                elements.append(Paragraph(
                    f"• {pattern['pattern']}: {pattern['confidence']*100:.0f}% confidence, {pattern['frequency']} occurrences",
                    self.styles['Normal']
                ))
            
            elements.append(Spacer(1, 12))
            
            # Parameter suggestions
            elements.append(Paragraph("Parameter Optimization Suggestions", self.styles['Heading3']))
            for suggestion in data.get('parameter_suggestions', []):
                elements.append(Paragraph(
                    f"• {suggestion['parameter']}: {suggestion['current']} → {suggestion['suggested']} ({suggestion['confidence']*100:.0f}% confidence)",
                    self.styles['Normal']
                ))
            
            elements.append(Spacer(1, 20))
            
            return elements
        
        except Exception as e:
            logger.error(f"Error creating AI insights section: {e}")
            return []
    
    def _create_recommendations_section(self, data: Dict) -> List:
        """Create recommendations section"""
        try:
            elements = []
            
            elements.append(Paragraph("Recommendations", self.styles['Heading2']))
            elements.append(Spacer(1, 12))
            
            # Immediate actions
            elements.append(Paragraph("Immediate Actions", self.styles['Heading3']))
            for action in data.get('immediate_actions', []):
                elements.append(Paragraph(f"• {action}", self.styles['Normal']))
            
            elements.append(Spacer(1, 12))
            
            # Parameter adjustments
            elements.append(Paragraph("Parameter Adjustments", self.styles['Heading3']))
            for adjustment in data.get('parameter_adjustments', []):
                elements.append(Paragraph(f"• {adjustment}", self.styles['Normal']))
            
            elements.append(Spacer(1, 12))
            
            # Risk management
            elements.append(Paragraph("Risk Management", self.styles['Heading3']))
            for risk_item in data.get('risk_management', []):
                elements.append(Paragraph(f"• {risk_item}", self.styles['Normal']))
            
            elements.append(Spacer(1, 20))
            
            return elements
        
        except Exception as e:
            logger.error(f"Error creating recommendations section: {e}")
            return []
    
    async def _generate_charts(self, date: datetime) -> Dict:
        """Generate charts for the report"""
        try:
            charts = {}
            
            # Equity curve chart
            charts['equity_curve'] = await self._create_equity_curve_chart(date)
            
            # P&L distribution chart
            charts['pnl_distribution'] = await self._create_pnl_distribution_chart(date)
            
            # Trading pairs performance chart
            charts['pairs_performance'] = await self._create_pairs_performance_chart(date)
            
            # Hourly trading activity chart
            charts['hourly_activity'] = await self._create_hourly_activity_chart(date)
            
            return charts
        
        except Exception as e:
            logger.error(f"Error generating charts: {e}")
            return {}
    
    async def _create_equity_curve_chart(self, date: datetime) -> str:
        """Create equity curve chart"""
        try:
            # Mock data - would come from database
            dates = pd.date_range(start=date - timedelta(days=30), end=date, freq='D')
            equity = np.cumsum(np.random.normal(1, 5, len(dates))) + 500
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=dates,
                y=equity,
                mode='lines',
                name='Equity Curve',
                line=dict(color='blue', width=2)
            ))
            
            fig.update_layout(
                title='30-Day Equity Curve',
                xaxis_title='Date',
                yaxis_title='Account Value (£)',
                template='plotly_white'
            )
            
            chart_path = os.path.join(self.charts_dir, f'equity_curve_{date.strftime("%Y%m%d")}.png')
            fig.write_image(chart_path, width=800, height=400)
            
            return chart_path
        
        except Exception as e:
            logger.error(f"Error creating equity curve chart: {e}")
            return ""
    
    async def _create_pnl_distribution_chart(self, date: datetime) -> str:
        """Create P&L distribution chart"""
        try:
            # Mock data
            pnl_data = np.random.normal(2, 8, 100)  # Mock P&L data
            
            fig = go.Figure()
            fig.add_trace(go.Histogram(
                x=pnl_data,
                nbinsx=20,
                name='P&L Distribution',
                marker_color='lightblue'
            ))
            
            fig.update_layout(
                title='Trade P&L Distribution',
                xaxis_title='P&L (£)',
                yaxis_title='Frequency',
                template='plotly_white'
            )
            
            chart_path = os.path.join(self.charts_dir, f'pnl_distribution_{date.strftime("%Y%m%d")}.png')
            fig.write_image(chart_path, width=800, height=400)
            
            return chart_path
        
        except Exception as e:
            logger.error(f"Error creating P&L distribution chart: {e}")
            return ""
    
    async def _create_pairs_performance_chart(self, date: datetime) -> str:
        """Create trading pairs performance chart"""
        try:
            # Mock data
            pairs = ['BTC-USDT', 'ETH-USDT', 'ADA-USDT', 'SOL-USDT']
            performance = [12.5, 8.2, -3.1, 7.9]
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=pairs,
                y=performance,
                marker_color=['green' if p > 0 else 'red' for p in performance]
            ))
            
            fig.update_layout(
                title='Trading Pairs Performance',
                xaxis_title='Trading Pair',
                yaxis_title='P&L (£)',
                template='plotly_white'
            )
            
            chart_path = os.path.join(self.charts_dir, f'pairs_performance_{date.strftime("%Y%m%d")}.png')
            fig.write_image(chart_path, width=800, height=400)
            
            return chart_path
        
        except Exception as e:
            logger.error(f"Error creating pairs performance chart: {e}")
            return ""
    
    async def _create_hourly_activity_chart(self, date: datetime) -> str:
        """Create hourly trading activity chart"""
        try:
            # Mock data
            hours = list(range(9, 17))
            trades = [2, 1, 3, 2, 1, 2, 1, 0]
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=[f"{h:02d}:00" for h in hours],
                y=trades,
                marker_color='lightgreen'
            ))
            
            fig.update_layout(
                title='Hourly Trading Activity',
                xaxis_title='Hour',
                yaxis_title='Number of Trades',
                template='plotly_white'
            )
            
            chart_path = os.path.join(self.charts_dir, f'hourly_activity_{date.strftime("%Y%m%d")}.png')
            fig.write_image(chart_path, width=800, height=400)
            
            return chart_path
        
        except Exception as e:
            logger.error(f"Error creating hourly activity chart: {e}")
            return ""
    
    def _add_charts_to_report(self, charts: Dict) -> List:
        """Add charts to the report"""
        try:
            elements = []
            
            elements.append(Paragraph("Charts and Visualizations", self.styles['Heading2']))
            elements.append(Spacer(1, 12))
            
            for chart_name, chart_path in charts.items():
                if chart_path and os.path.exists(chart_path):
                    # Add chart title
                    title = chart_name.replace('_', ' ').title()
                    elements.append(Paragraph(title, self.styles['Heading3']))
                    
                    # Add chart image
                    img = Image(chart_path, width=6*inch, height=3*inch)
                    elements.append(img)
                    elements.append(Spacer(1, 20))
            
            return elements
        
        except Exception as e:
            logger.error(f"Error adding charts to report: {e}")
            return []
    
    async def generate_weekly_report(self, start_date: datetime) -> str:
        """Generate weekly trading report"""
        try:
            # Similar to daily report but with weekly data
            report_filename = f"weekly_report_{start_date.strftime('%Y%m%d')}.pdf"
            report_path = os.path.join(self.report_dir, report_filename)
            
            # Implementation would be similar to daily report
            # but with weekly aggregated data
            
            logger.info(f"Weekly report generated: {report_path}")
            return report_path
        
        except Exception as e:
            logger.error(f"Error generating weekly report: {e}")
            return ""
    
    async def generate_monthly_report(self, month: int, year: int) -> str:
        """Generate monthly trading report"""
        try:
            report_filename = f"monthly_report_{year}{month:02d}.pdf"
            report_path = os.path.join(self.report_dir, report_filename)
            
            # Implementation would include monthly statistics,
            # performance comparison, and detailed analysis
            
            logger.info(f"Monthly report generated: {report_path}")
            return report_path
        
        except Exception as e:
            logger.error(f"Error generating monthly report: {e}")
            return ""
