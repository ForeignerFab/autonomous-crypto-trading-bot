
"""
Discord Integration Module
Handles notifications, alerts, and user interactions via Discord
"""

import asyncio
import discord
from discord.ext import commands, tasks
from discord import Webhook
import aiohttp
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from loguru import logger
import os
import uuid
from .reporter import ReportGenerator


class DiscordNotifier:
    """Discord bot for trading notifications and interactions"""
    
    def __init__(
        self,
        config: Dict,
        config_path: Optional[str] = None,
        config_update_callback: Optional[Any] = None,
        ai_optimization_callback: Optional[Any] = None,
        config_suggest_callback: Optional[Any] = None,
        status_callback: Optional[Any] = None,
        pause_callback: Optional[Any] = None,
        resume_callback: Optional[Any] = None,
        stop_callback: Optional[Any] = None,
        balance_callback: Optional[Any] = None,
        positions_callback: Optional[Any] = None
    ):
        """Initialize Discord notifier"""
        self.config = config
        self.discord_config = config['discord']
        self.config_path = config_path
        self.config_update_callback = config_update_callback
        self.ai_optimization_callback = ai_optimization_callback
        self.config_suggest_callback = config_suggest_callback
        self.status_callback = status_callback
        self.pause_callback = pause_callback
        self.resume_callback = resume_callback
        self.stop_callback = stop_callback
        self.balance_callback = balance_callback
        self.positions_callback = positions_callback
        
        # Bot setup
        intents = discord.Intents.default()
        intents.message_content = True
        
        self.bot = commands.Bot(command_prefix='!', intents=intents)
        self.webhook_url = self.discord_config.get('webhook_url')
        self.channel_id = int(self.discord_config.get('channel_id', 0))
        self.channel = None
        
        # Notification settings
        self.notify_trades = self.discord_config.get('notify_trades', True)
        self.notify_errors = self.discord_config.get('notify_errors', True)
        self.notify_daily_report = self.discord_config.get('notify_daily_report', True)
        
        # Report generator
        self.report_generator = ReportGenerator(config)
        self.pending_suggestions: Dict[str, Dict[str, Any]] = {}
        self.app_version = self._resolve_app_version()
        
        # Setup bot events and commands
        self._setup_bot_events()
        self._setup_commands()
        
        logger.info("Discord notifier initialized")
    
    async def initialize(self):
        """Initialize Discord bot"""
        try:
            token = self.discord_config.get('bot_token')
            if not token:
                logger.warning("No Discord bot token provided, notifications disabled")
                return
            
            # Start bot in background
            asyncio.create_task(self._start_bot(token))
            
            # Wait a moment for bot to connect
            await asyncio.sleep(2)
            
            # Get channel
            if self.channel_id:
                self.channel = self.bot.get_channel(self.channel_id)
                if not self.channel:
                    try:
                        self.channel = await self.bot.fetch_channel(self.channel_id)
                    except Exception as e:
                        logger.warning(f"Could not fetch Discord channel: {e}")
                if self.channel:
                    await self.send_notification("🤖 Trading Bot Connected", "Discord integration active")
                    logger.info(f"Discord bot connected to channel: {self.channel.name}")
                else:
                    logger.warning(f"Could not find Discord channel with ID: {self.channel_id}")
            
            # Start daily report task
            if self.notify_daily_report:
                self.daily_report_task.start()
        
        except Exception as e:
            logger.error(f"Failed to initialize Discord bot: {e}")

    def _resolve_app_version(self) -> str:
        """Resolve version from env or VERSION file"""
        env_version = os.getenv("APP_VERSION") or os.getenv("GIT_COMMIT")
        if env_version:
            return env_version
        try:
            base_dir = os.path.dirname(os.path.dirname(__file__))
            version_path = os.path.join(base_dir, "VERSION.txt")
            if os.path.exists(version_path):
                with open(version_path, "r", encoding="utf-8") as handle:
                    return handle.read().strip() or "1.0"
        except Exception as exc:
            logger.warning(f"Failed to read VERSION.txt: {exc}")
        return "1.0"
    
    async def _start_bot(self, token: str):
        """Start the Discord bot"""
        try:
            await self.bot.start(token)
        except Exception as e:
            logger.error(f"Discord bot error: {e}")
    
    def _setup_bot_events(self):
        """Setup Discord bot events"""
        
        @self.bot.event
        async def on_ready():
            logger.info(f'Discord bot logged in as {self.bot.user}')
        
        @self.bot.event
        async def on_message(message):
            if message.author == self.bot.user:
                return
            
            # Process commands
            await self.bot.process_commands(message)

        @self.bot.event
        async def on_command_error(ctx, error):
            """Handle command errors with user feedback"""
            if isinstance(error, commands.MissingPermissions):
                await ctx.send("❌ You need Administrator permission to use this command.")
                return
            if isinstance(error, commands.CommandNotFound):
                return
            if isinstance(error, commands.CheckFailure):
                await ctx.send("❌ You don't have permission to run this command.")
                return

            logger.error(f"Command error: {error}")
            await ctx.send("❌ Command failed. Check logs for details.")
    
    def _setup_commands(self):
        """Setup Discord bot commands"""
        
        @self.bot.command(name='status')
        async def status_command(ctx):
            """Get bot status"""
            try:
                if not self.status_callback:
                    await ctx.send("Status callback not configured.")
                    return

                status = await self.status_callback()
                embed = discord.Embed(
                    title="🤖 Trading Bot Status",
                    color=discord.Color.blue(),
                    timestamp=datetime.now()
                )
                embed.add_field(name="Status", value="Running ✅" if status.get("running") else "Stopped ❌", inline=True)
                embed.add_field(name="Paused", value="Yes" if status.get("paused") else "No", inline=True)
                embed.add_field(name="Open Positions", value=str(status.get("open_positions", 0)), inline=True)
                active_pairs = status.get("active_pairs", [])
                embed.add_field(name="Active Pairs", value=str(len(active_pairs)), inline=True)
                embed.add_field(name="Daily P&L", value=f"£{status.get('daily_pnl', 0):.2f}", inline=True)
                await ctx.send(embed=embed)
            except Exception as e:
                logger.error(f"Error in status command: {e}")
        
        @self.bot.command(name='balance')
        async def balance_command(ctx):
            """Get account balance"""
            try:
                if not self.balance_callback:
                    await ctx.send("Balance callback not configured.")
                    return

                balance = await self.balance_callback()
                embed = discord.Embed(
                    title="💰 Account Balance",
                    color=discord.Color.green(),
                    timestamp=datetime.now()
                )
                embed.add_field(name="Available (USDT)", value=f"{balance:.4f}", inline=True)
                await ctx.send(embed=embed)
            except Exception as e:
                logger.error(f"Error in balance command: {e}")
        
        @self.bot.command(name='positions')
        async def positions_command(ctx):
            """Get open positions"""
            try:
                if not self.positions_callback:
                    await ctx.send("Positions callback not configured.")
                    return

                positions = await self.positions_callback()
                embed = discord.Embed(
                    title="📊 Open Positions",
                    color=discord.Color.orange(),
                    timestamp=datetime.now()
                )
                if not positions:
                    embed.add_field(name="No Open Positions", value="All positions closed", inline=False)
                else:
                    for position in positions[:10]:
                        embed.add_field(
                            name=f"{position['symbol']} ({position['side'].upper()})",
                            value=f"Size: {position['size']:.6f}\nP&L: £{position['pnl']:.2f}",
                            inline=False
                        )
                await ctx.send(embed=embed)
            except Exception as e:
                logger.error(f"Error in positions command: {e}")
        
        @self.bot.command(name='stop')
        @commands.has_permissions(administrator=True)
        async def stop_command(ctx):
            """Emergency stop trading"""
            try:
                if not self.stop_callback:
                    await ctx.send("Stop callback not configured.")
                    return

                await self.stop_callback()
                embed = discord.Embed(
                    title="🛑 Emergency Stop",
                    description="Trading bot stop requested.",
                    color=discord.Color.red(),
                    timestamp=datetime.now()
                )
                await ctx.send(embed=embed)
            except Exception as e:
                logger.error(f"Error in stop command: {e}")
        
        @self.bot.command(name='report')
        async def report_command(ctx):
            """Generate and send trading report"""
            try:
                await ctx.send("📊 Generating trading report...")
                
                # Generate report
                report_path = await self.report_generator.generate_daily_report()
                
                if report_path and os.path.exists(report_path):
                    with open(report_path, 'rb') as f:
                        file = discord.File(f, filename="trading_report.pdf")
                        await ctx.send("📈 Daily Trading Report", file=file)
                else:
                    await ctx.send("❌ Failed to generate report")
            
            except Exception as e:
                logger.error(f"Error in report command: {e}")
                await ctx.send("❌ Error generating report")

        @self.bot.command(name='version')
        async def version_command(ctx):
            """Show bot version"""
            try:
                await ctx.send(f"🤖 Bot version: `{self.app_version}`")
            except Exception as e:
                logger.error(f"Error in version command: {e}")

        @self.bot.command(name='pause')
        @commands.has_permissions(administrator=True)
        async def pause_command(ctx):
            """Pause trading"""
            try:
                if not self.pause_callback:
                    await ctx.send("Pause callback not configured.")
                    return
                await self.pause_callback()
                await ctx.send("⏸️ Trading paused.")
            except Exception as e:
                logger.error(f"Error in pause command: {e}")

        @self.bot.command(name='resume')
        @commands.has_permissions(administrator=True)
        async def resume_command(ctx):
            """Resume trading"""
            try:
                if not self.resume_callback:
                    await ctx.send("Resume callback not configured.")
                    return
                await self.resume_callback()
                await ctx.send("▶️ Trading resumed.")
            except Exception as e:
                logger.error(f"Error in resume command: {e}")

        @self.bot.command(name='suggestions')
        @commands.has_permissions(administrator=True)
        async def suggestions_command(ctx):
            """List pending AI config suggestions"""
            self._prune_pending_suggestions()
            if not self.pending_suggestions:
                await ctx.send("No pending AI suggestions.")
                return

            lines = []
            for suggestion_id, entry in self.pending_suggestions.items():
                summary = ", ".join(
                    f"{param}: {details.get('current')} → {details.get('suggested')}"
                    for param, details in entry.get('suggestions', {}).items()
                )
                lines.append(f"`{suggestion_id}` — {summary}")

            await ctx.send("Pending suggestions:\n" + "\n".join(lines))

        @self.bot.command(name='approve')
        @commands.has_permissions(administrator=True)
        async def approve_command(ctx, suggestion_id: str):
            """Approve and apply a pending suggestion batch"""
            self._prune_pending_suggestions()
            entry = self.pending_suggestions.get(suggestion_id)
            if not entry:
                await ctx.send("Suggestion ID not found or expired.")
                return

            if not self.config_update_callback:
                await ctx.send("Config update callback is not configured.")
                return

            result = await self.config_update_callback(entry.get('suggestions', {}))
            applied = result.get('applied', {})
            skipped = result.get('skipped', {})
            errors = result.get('errors', [])

            response_parts = []
            if applied:
                applied_lines = [f"{k}: {v['from']} → {v['to']}" for k, v in applied.items()]
                response_parts.append("✅ Applied:\n" + "\n".join(applied_lines))
            if skipped:
                skipped_lines = [f"{k}: {v}" for k, v in skipped.items()]
                response_parts.append("⚠️ Skipped:\n" + "\n".join(skipped_lines))
            if errors:
                response_parts.append("❌ Errors:\n" + "\n".join(errors))

            await ctx.send("\n\n".join(response_parts) if response_parts else "No changes applied.")
            self.pending_suggestions.pop(suggestion_id, None)

        @self.bot.command(name='reject')
        @commands.has_permissions(administrator=True)
        async def reject_command(ctx, suggestion_id: str):
            """Reject a pending suggestion batch"""
            self._prune_pending_suggestions()
            if suggestion_id not in self.pending_suggestions:
                await ctx.send("Suggestion ID not found or expired.")
                return

            self.pending_suggestions.pop(suggestion_id, None)
            await ctx.send(f"Rejected suggestions `{suggestion_id}`.")

        @self.bot.command(name='optimize')
        @commands.has_permissions(administrator=True)
        async def optimize_command(ctx):
            """Trigger AI optimization now"""
            if not self.ai_optimization_callback:
                await ctx.send("AI optimization callback is not configured.")
                return

            await ctx.send("Running AI optimization...")
            suggestions = await self.ai_optimization_callback()
            if suggestions:
                await self.send_ai_suggestions(suggestions)
            else:
                await ctx.send("No AI suggestions available yet.")

        @self.bot.command(name='configsuggest')
        @commands.has_permissions(administrator=True)
        async def configsuggest_command(ctx):
            """Suggest config updates based on research"""
            if not self.config_suggest_callback:
                await ctx.send("Config suggest callback is not configured.")
                return

            await ctx.send("Generating research-based config suggestions...")
            result = await self.config_suggest_callback()
            suggestions = result.get("suggestions")
            chart_path = result.get("chart_path")
            message = result.get("message")

            if suggestions:
                await self.send_ai_suggestions(
                    suggestions,
                    chart_path=chart_path,
                    title="📌 Research-Based Config Suggestions",
                    note=message
                )
            else:
                await ctx.send(message or "No research-based suggestions available.")
                if chart_path:
                    await self.send_research_chart(chart_path, "Latest research snapshot")
    
    async def close(self):
        """Close Discord bot"""
        try:
            if hasattr(self, 'daily_report_task'):
                self.daily_report_task.cancel()
            
            if self.bot:
                await self.bot.close()
            
            logger.info("Discord bot closed")
        except Exception as e:
            logger.error(f"Error closing Discord bot: {e}")
    
    async def send_notification(self, title: str, message: str, color: discord.Color = discord.Color.blue()):
        """Send a general notification"""
        try:
            if not self.channel:
                return
            
            embed = discord.Embed(
                title=title,
                description=message,
                color=color,
                timestamp=datetime.now()
            )
            
            await self.channel.send(embed=embed)
        
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            # Fallback to webhook if available
            await self._send_webhook_message(title, message)
    
    async def send_trade_notification(self, signal, order: Dict):
        """Send trade execution notification"""
        try:
            if not self.notify_trades or not self.channel:
                return
            
            # Determine color based on trade direction
            color = discord.Color.green() if signal.action == 'buy' else discord.Color.red()
            
            embed = discord.Embed(
                title=f"{'📈' if signal.action == 'buy' else '📉'} Trade Executed",
                color=color,
                timestamp=datetime.now()
            )
            
            embed.add_field(name="Symbol", value=signal.symbol, inline=True)
            embed.add_field(name="Action", value=signal.action.upper(), inline=True)
            embed.add_field(name="Size", value=f"{signal.position_size:.6f}", inline=True)
            
            embed.add_field(name="Entry Price", value=f"£{signal.entry_price:.4f}", inline=True)
            embed.add_field(name="Stop Loss", value=f"£{signal.stop_loss:.4f}", inline=True)
            embed.add_field(name="Take Profit", value=f"£{signal.take_profit:.4f}", inline=True)
            
            embed.add_field(name="Risk Amount", value=f"£{signal.position_size * abs(signal.entry_price - signal.stop_loss):.2f}", inline=True)
            embed.add_field(name="Confidence", value=f"{signal.confidence*100:.1f}%", inline=True)
            embed.add_field(name="Order ID", value=order.get('id', 'N/A'), inline=True)
            
            if signal.reasoning:
                embed.add_field(name="Reasoning", value=signal.reasoning, inline=False)
            
            await self.channel.send(embed=embed)
        
        except Exception as e:
            logger.error(f"Error sending trade notification: {e}")
    
    async def send_position_close_notification(self, position, reason: str):
        """Send position close notification"""
        try:
            if not self.notify_trades or not self.channel:
                return
            
            # Determine color based on P&L
            color = discord.Color.green() if position.pnl > 0 else discord.Color.red()
            
            embed = discord.Embed(
                title=f"{'✅' if position.pnl > 0 else '❌'} Position Closed",
                color=color,
                timestamp=datetime.now()
            )
            
            embed.add_field(name="Symbol", value=position.symbol, inline=True)
            embed.add_field(name="Side", value=position.side.upper(), inline=True)
            embed.add_field(name="Size", value=f"{position.size:.6f}", inline=True)
            
            embed.add_field(name="Entry Price", value=f"£{position.entry_price:.4f}", inline=True)
            embed.add_field(name="Exit Price", value=f"£{position.current_price:.4f}", inline=True)
            embed.add_field(name="P&L", value=f"£{position.pnl:.2f}", inline=True)
            
            embed.add_field(name="Reason", value=reason, inline=False)
            
            await self.channel.send(embed=embed)
        
        except Exception as e:
            logger.error(f"Error sending position close notification: {e}")
    
    async def send_error(self, error_message: str):
        """Send error notification"""
        try:
            if not self.notify_errors:
                return
            
            await self.send_notification(
                "❌ Error Alert",
                f"```{error_message}```",
                discord.Color.red()
            )
        
        except Exception as e:
            logger.error(f"Error sending error notification: {e}")
    
    async def send_ai_suggestions(
        self,
        suggestions: Dict,
        chart_path: Optional[str] = None,
        title: str = "🧠 AI Parameter Suggestions",
        note: Optional[str] = None
    ):
        """Send AI parameter optimization suggestions"""
        try:
            if not self.channel:
                return

            normalized = self._normalize_suggestions(suggestions)
            if not normalized:
                return

            suggestion_id = uuid.uuid4().hex[:8]
            self.pending_suggestions[suggestion_id] = {
                "suggestions": normalized,
                "created_at": datetime.now()
            }

            description = (
                "The AI assistant suggests the following config updates.\n"
                f"Approve with `!approve {suggestion_id}` or reject with `!reject {suggestion_id}`."
            )
            if note:
                description = f"{note}\n\n{description}"

            embed = discord.Embed(
                title=title,
                description=description,
                color=discord.Color.purple(),
                timestamp=datetime.now()
            )

            for param, suggestion in normalized.items():
                embed.add_field(
                    name=param.replace('_', ' ').title(),
                    value=(
                        f"Current: {suggestion.get('current', 'N/A')}\n"
                        f"Suggested: {suggestion.get('suggested', 'N/A')}\n"
                        f"Confidence: {suggestion.get('confidence', 'N/A')}\n"
                        f"Reason: {suggestion.get('reason', 'N/A')}"
                    ),
                    inline=False
                )
            
            if chart_path and os.path.exists(chart_path):
                file = discord.File(chart_path, filename="research_summary.png")
                embed.set_image(url="attachment://research_summary.png")
                await self.channel.send(embed=embed, file=file)
            else:
                await self.channel.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error sending AI suggestions: {e}")

    async def send_research_chart(self, chart_path: str, message: Optional[str] = None):
        """Send a research chart image to Discord"""
        try:
            if not self.channel or not chart_path or not os.path.exists(chart_path):
                return

            embed = discord.Embed(
                title="📊 Research Snapshot",
                description=message or "",
                color=discord.Color.teal(),
                timestamp=datetime.now()
            )
            file = discord.File(chart_path, filename="research_summary.png")
            embed.set_image(url="attachment://research_summary.png")
            await self.channel.send(embed=embed, file=file)
        except Exception as e:
            logger.error(f"Error sending research chart: {e}")

    async def send_ai_gating_log(self, signal, evaluation: Dict):
        """Send AI gating decision to Discord"""
        try:
            if not self.channel:
                return

            approve = evaluation.get("approve", False)
            confidence = evaluation.get("confidence", 0.0)
            reason = evaluation.get("reason", "N/A")

            embed = discord.Embed(
                title=f"🤖 AI Gate {'Approved' if approve else 'Rejected'}",
                color=discord.Color.green() if approve else discord.Color.red(),
                timestamp=datetime.now()
            )
            embed.add_field(name="Symbol", value=signal.symbol, inline=True)
            embed.add_field(name="Action", value=signal.action.upper(), inline=True)
            embed.add_field(name="Confidence", value=f"{confidence:.2f}", inline=True)
            embed.add_field(name="Reason", value=reason, inline=False)

            await self.channel.send(embed=embed)
        except Exception as e:
            logger.error(f"Error sending AI gating log: {e}")

    async def send_config_change_log(self, entry: Dict):
        """Send config change summary to Discord"""
        try:
            if not self.channel:
                return

            applied = entry.get("applied", {})
            skipped = entry.get("skipped", {})
            errors = entry.get("errors", [])

            embed = discord.Embed(
                title="🛠️ Config Update Applied",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )

            if applied:
                applied_lines = [f"{k}: {v['from']} → {v['to']}" for k, v in applied.items()]
                embed.add_field(name="Applied", value="\n".join(applied_lines), inline=False)
            if skipped:
                skipped_lines = [f"{k}: {v}" for k, v in skipped.items()]
                embed.add_field(name="Skipped", value="\n".join(skipped_lines), inline=False)
            if errors:
                embed.add_field(name="Errors", value="\n".join(errors), inline=False)

            await self.channel.send(embed=embed)
        except Exception as e:
            logger.error(f"Error sending config change log: {e}")

    async def send_research_summary(self, results: List[Dict], request_count: int, max_requests: int):
        """Send a summary of pattern research results"""
        try:
            if not self.channel:
                return

            # Aggregate by pattern + timeframe
            summary = {}
            for record in results:
                key = f"{record.get('pattern_name')} ({record.get('timeframe')})"
                occ = record.get('occurrences', 0)
                success = record.get('success_rate', 0) * occ
                avg_ret = record.get('avg_return', 0) * occ
                if key not in summary:
                    summary[key] = {"occurrences": 0, "success": 0.0, "avg_ret": 0.0}
                summary[key]["occurrences"] += occ
                summary[key]["success"] += success
                summary[key]["avg_ret"] += avg_ret

            ranked = sorted(
                summary.items(),
                key=lambda item: (item[1]["success"] / item[1]["occurrences"]) if item[1]["occurrences"] else 0,
                reverse=True
            )

            lines = []
            for name, data in ranked[:5]:
                occ = data["occurrences"] or 1
                success_rate = data["success"] / occ
                avg_ret = data["avg_ret"] / occ
                lines.append(f"{name}: {success_rate*100:.1f}% success, avg return {avg_ret*100:.2f}% (n={occ})")

            embed = discord.Embed(
                title="📊 Pattern Research Summary",
                description="\n".join(lines) if lines else "No significant patterns found.",
                color=discord.Color.teal(),
                timestamp=datetime.now()
            )
            embed.add_field(
                name="Requests Used",
                value=f"{request_count}/{max_requests}",
                inline=True
            )

            await self.channel.send(embed=embed)
        except Exception as e:
            logger.error(f"Error sending research summary: {e}")

    def _normalize_suggestions(self, suggestions: Dict) -> Dict[str, Dict[str, Any]]:
        """Normalize suggestions to a serializable dict"""
        normalized = {}
        for param, suggestion in (suggestions or {}).items():
            if isinstance(suggestion, dict):
                normalized[param] = {
                    "current": suggestion.get("current_value", suggestion.get("current")),
                    "suggested": suggestion.get("suggested_value", suggestion.get("suggested")),
                    "confidence": suggestion.get("confidence"),
                    "reason": suggestion.get("reason")
                }
            else:
                normalized[param] = {
                    "current": getattr(suggestion, "current_value", None),
                    "suggested": getattr(suggestion, "suggested_value", None),
                    "confidence": getattr(suggestion, "confidence", None),
                    "reason": getattr(suggestion, "reason", None)
                }

        # Filter to items that have a suggested value
        return {k: v for k, v in normalized.items() if v.get("suggested") is not None}

    def _prune_pending_suggestions(self, max_age_hours: int = 24):
        """Remove expired suggestions without applying changes"""
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        expired = [key for key, value in self.pending_suggestions.items() if value.get("created_at") < cutoff]
        for key in expired:
            self.pending_suggestions.pop(key, None)
            logger.info(f"Expired AI suggestion {key} (no changes applied)")
            try:
                asyncio.create_task(
                    self.send_notification(
                        "⏳ AI Suggestion Expired",
                        f"Suggestion `{key}` expired after {max_age_hours} hours. No changes applied."
                    )
                )
            except Exception as exc:
                logger.error(f"Failed to send expiration notice: {exc}")
    
    async def _send_webhook_message(self, title: str, message: str):
        """Send message via webhook as fallback"""
        try:
            if not self.webhook_url:
                return
            
            async with aiohttp.ClientSession() as session:
                webhook = Webhook.from_url(self.webhook_url, session=session)
                
                embed = discord.Embed(
                    title=title,
                    description=message,
                    timestamp=datetime.now()
                )
                
                await webhook.send(embed=embed)
        
        except Exception as e:
            logger.error(f"Error sending webhook message: {e}")
    
    @tasks.loop(hours=24)
    async def daily_report_task(self):
        """Daily report generation task"""
        try:
            if not self.notify_daily_report or not self.channel:
                return
            
            logger.info("Generating daily report...")
            
            # Generate report
            report_path = await self.report_generator.generate_daily_report()
            
            if report_path and os.path.exists(report_path):
                embed = discord.Embed(
                    title="📊 Daily Trading Report",
                    description=f"Daily report for {datetime.now().strftime('%Y-%m-%d')}",
                    color=discord.Color.blue(),
                    timestamp=datetime.now()
                )
                
                with open(report_path, 'rb') as f:
                    file = discord.File(f, filename=f"trading_report_{datetime.now().strftime('%Y%m%d')}.pdf")
                    await self.channel.send(embed=embed, file=file)
            else:
                await self.send_error("Failed to generate daily report")
        
        except Exception as e:
            logger.error(f"Error in daily report task: {e}")
    
    @daily_report_task.before_loop
    async def before_daily_report(self):
        """Wait for bot to be ready before starting daily report task"""
        await self.bot.wait_until_ready()
        
        # Calculate time until next report
        now = datetime.now()
        report_time = self.discord_config.get('report_time', '09:00')
        hour, minute = map(int, report_time.split(':'))
        
        next_report = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if next_report <= now:
            next_report += timedelta(days=1)
        
        wait_seconds = (next_report - now).total_seconds()
        logger.info(f"Next daily report in {wait_seconds/3600:.1f} hours")
        
        await asyncio.sleep(wait_seconds)
