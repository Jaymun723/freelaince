import json
import datetime
from typing import List, Dict, Any, Optional
from smolagents import Tool
import os
import webbrowser
from pathlib import Path

class ScheduleWebViewTool(Tool):
    name = "view_schedule_web"
    description = "Display schedule in a beautiful web interface"
    
    inputs = {
        "start_date": {
            "type": "string",
            "description": "Start date in format 'YYYY-MM-DD' (default: today)",
            "default": "",
            "nullable": True
        },
        "days": {
            "type": "integer",
            "description": "Number of days to show (default: 7)",
            "default": 7,
            "nullable": True
        },
        "view_type": {
            "type": "string",
            "description": "View type: 'calendar', 'timeline', or 'list' (default: 'calendar')",
            "default": "calendar",
            "nullable": True
        },
        "open_browser": {
            "type": "boolean",
            "description": "Whether to automatically open in browser (default: true)",
            "default": True,
            "nullable": True
        }
    }
    
    output_type = "string"
    
    def __init__(self, schedule_manager):
        super().__init__()
        self.schedule_manager = schedule_manager
    
    def forward(self, start_date: str = "", days: int = 7, 
                view_type: str = "calendar", open_browser: bool = True) -> str:
        """Generate and display a beautiful web interface for the schedule"""
        try:
            # Parse dates
            if start_date:
                start = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
            else:
                start = datetime.date.today()
            
            end = start + datetime.timedelta(days=days-1)
            events = self.schedule_manager.get_schedule(start, end)
            
            # Generate HTML based on view type
            if view_type == "calendar":
                html_content = self._generate_calendar_view(events, start, end)
            elif view_type == "timeline":
                html_content = self._generate_timeline_view(events, start, end)
            else:  # list view
                html_content = self._generate_list_view(events, start, end)
            
            # Save to file
            file_path = Path("schedule_view.html")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Open in browser if requested
            if open_browser:
                webbrowser.open(f"file://{file_path.absolute()}")
            
            return json.dumps({
                "success": True,
                "message": f"Schedule web view generated successfully",
                "file_path": str(file_path.absolute()),
                "view_type": view_type,
                "period": f"{start} to {end}",
                "total_events": len(events),
                "browser_opened": open_browser
            }, indent=2)
            
        except Exception as e:
            return json.dumps({
                "success": False,
                "message": f"Error generating web view: {str(e)}"
            })
    
    def _get_base_html_template(self, title: str, additional_styles: str = "") -> str:
        """Base HTML template with modern styling"""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        :root {{
            --primary-color: #4f46e5;
            --secondary-color: #e0e7ff;
            --success-color: #10b981;
            --warning-color: #f59e0b;
            --danger-color: #ef4444;
            --dark-color: #1f2937;
            --light-color: #f9fafb;
            --border-color: #d1d5db;
            --text-primary: #111827;
            --text-secondary: #6b7280;
            --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: var(--text-primary);
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: var(--shadow-lg);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, var(--primary-color), #6366f1);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.1rem;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 30px;
        }}
        
        .event-card {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 16px;
            box-shadow: var(--shadow);
            border-left: 4px solid var(--primary-color);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        
        .event-card:hover {{
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
        }}
        
        .event-title {{
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 8px;
        }}
        
        .event-time {{
            color: var(--primary-color);
            font-weight: 500;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .event-details {{
            color: var(--text-secondary);
            font-size: 0.9rem;
            line-height: 1.5;
        }}
        
        .event-meta {{
            display: flex;
            gap: 12px;
            margin-top: 12px;
            flex-wrap: wrap;
        }}
        
        .meta-item {{
            display: flex;
            align-items: center;
            gap: 4px;
            font-size: 0.85rem;
            color: var(--text-secondary);
        }}
        
        .priority-badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 500;
            text-transform: uppercase;
        }}
        
        .priority-1 {{ background: #f3f4f6; color: #6b7280; }}
        .priority-2 {{ background: #dbeafe; color: #1d4ed8; }}
        .priority-3 {{ background: #fef3c7; color: #d97706; }}
        .priority-4 {{ background: #fed7aa; color: #ea580c; }}
        .priority-5 {{ background: #fecaca; color: #dc2626; }}
        
        .conflict-warning {{
            background: #fef2f2;
            border-left-color: var(--danger-color);
            border: 1px solid #fecaca;
        }}
        
        .conflict-badge {{
            background: var(--danger-color);
            color: white;
            padding: 2px 8px;
            border-radius: 8px;
            font-size: 0.7rem;
            font-weight: 600;
        }}
        
        .no-events {{
            text-align: center;
            padding: 60px 20px;
            color: var(--text-secondary);
        }}
        
        .no-events-icon {{
            font-size: 4rem;
            margin-bottom: 20px;
            opacity: 0.5;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: var(--light-color);
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            border: 1px solid var(--border-color);
        }}
        
        .stat-number {{
            font-size: 2rem;
            font-weight: 700;
            color: var(--primary-color);
            margin-bottom: 8px;
        }}
        
        .stat-label {{
            color: var(--text-secondary);
            font-size: 0.9rem;
        }}
        
        .icon {{
            width: 16px;
            height: 16px;
            fill: currentColor;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                margin: 10px;
                border-radius: 12px;
            }}
            
            .header {{
                padding: 20px;
            }}
            
            .header h1 {{
                font-size: 2rem;
            }}
            
            .content {{
                padding: 20px;
            }}
            
            .stats {{
                grid-template-columns: 1fr;
            }}
        }}
        
        {additional_styles}
    </style>
</head>
<body>
"""
    
    def _generate_list_view(self, events: List, start_date: datetime.date, end_date: datetime.date) -> str:
        """Generate a beautiful list view of events"""
        
        # Group events by date
        events_by_date = {}
        for event in events:
            event_date = event.start_time.date()
            if event_date not in events_by_date:
                events_by_date[event_date] = []
            events_by_date[event_date].append(event)
        
        # Check for conflicts
        all_conflicts = self.schedule_manager.get_all_conflicts()
        conflict_events = set()
        for event1, event2 in all_conflicts:
            conflict_events.add(event1.title)
            conflict_events.add(event2.title)
        
        # Calculate stats
        total_events = len(events)
        total_conflicts = len([e for e in events if e.title in conflict_events])
        avg_priority = sum(e.priority for e in events) / len(events) if events else 0
        
        html = self._get_base_html_template("My Schedule - List View")
        
        html += f"""
        <div class="container">
            <div class="header">
                <h1>📅 My Schedule</h1>
                <p>{start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}</p>
            </div>
            
            <div class="content">
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-number">{total_events}</div>
                        <div class="stat-label">Total Events</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{total_conflicts}</div>
                        <div class="stat-label">Conflicts</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{avg_priority:.1f}</div>
                        <div class="stat-label">Avg Priority</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{len(events_by_date)}</div>
                        <div class="stat-label">Active Days</div>
                    </div>
                </div>
        """
        
        if not events:
            html += """
                <div class="no-events">
                    <div class="no-events-icon">📅</div>
                    <h3>No events scheduled</h3>
                    <p>Your schedule is clear for this period.</p>
                </div>
            """
        else:
            # Sort dates
            sorted_dates = sorted(events_by_date.keys())
            
            for date in sorted_dates:
                day_events = sorted(events_by_date[date], key=lambda e: e.start_time)
                
                html += f"""
                <div style="margin-bottom: 30px;">
                    <h2 style="color: var(--primary-color); margin-bottom: 16px; padding-bottom: 8px; border-bottom: 2px solid var(--secondary-color);">
                        {date.strftime('%A, %B %d, %Y')}
                    </h2>
                """
                
                for event in day_events:
                    is_conflict = event.title in conflict_events
                    card_class = "event-card" + (" conflict-warning" if is_conflict else "")
                    
                    duration = event.end_time - event.start_time
                    duration_str = f"{duration.total_seconds() / 3600:.1f}h"
                    
                    html += f"""
                    <div class="{card_class}">
                        <div class="event-title">
                            {event.title}
                            {f'<span class="conflict-badge">CONFLICT</span>' if is_conflict else ''}
                        </div>
                        <div class="event-time">
                            🕐 {event.start_time.strftime('%I:%M %p')} - {event.end_time.strftime('%I:%M %p')}
                            <span style="color: var(--text-secondary);">({duration_str})</span>
                        </div>
                        
                        {f'<div class="event-details">{event.description}</div>' if event.description else ''}
                        
                        <div class="event-meta">
                            {f'<div class="meta-item">📍 {event.location}</div>' if event.location else ''}
                            <div class="meta-item">
                                <span class="priority-badge priority-{event.priority}">
                                    Priority {event.priority}
                                </span>
                            </div>
                        </div>
                    </div>
                    """
                
                html += "</div>"
        
        html += """
            </div>
        </div>
        </body>
        </html>
        """
        
        return html
    
    def _generate_calendar_view(self, events: List, start_date: datetime.date, end_date: datetime.date) -> str:
        """Generate a calendar grid view"""
        
        additional_styles = """
        .calendar-grid {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 1px;
            background: var(--border-color);
            border-radius: 8px;
            overflow: hidden;
            margin-bottom: 20px;
        }
        
        .calendar-header {
            background: var(--primary-color);
            color: white;
            padding: 12px;
            text-align: center;
            font-weight: 600;
            font-size: 0.9rem;
        }
        
        .calendar-day {
            background: white;
            min-height: 120px;
            padding: 8px;
            position: relative;
        }
        
        .calendar-day.other-month {
            background: #f8f9fa;
            color: var(--text-secondary);
        }
        
        .calendar-day.today {
            background: var(--secondary-color);
        }
        
        .day-number {
            font-weight: 600;
            margin-bottom: 4px;
        }
        
        .day-event {
            background: var(--primary-color);
            color: white;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.7rem;
            margin-bottom: 2px;
            cursor: pointer;
            transition: background 0.2s;
        }
        
        .day-event:hover {
            background: #3730a3;
        }
        
        .day-event.conflict {
            background: var(--danger-color);
        }
        
        .day-event.high-priority {
            background: var(--warning-color);
        }
        """
        
        html = self._get_base_html_template("My Schedule - Calendar View", additional_styles)
        
        # Get calendar boundaries
        calendar_start = start_date.replace(day=1)
        # Find the first Monday of the calendar view
        while calendar_start.weekday() != 0:
            calendar_start -= datetime.timedelta(days=1)
        
        # Find the last day of the calendar view
        calendar_end = end_date
        if calendar_end.day < 28:
            next_month = calendar_end.replace(day=28) + datetime.timedelta(days=4)
            calendar_end = next_month - datetime.timedelta(days=next_month.day)
        
        while calendar_end.weekday() != 6:
            calendar_end += datetime.timedelta(days=1)
        
        # Group events by date
        events_by_date = {}
        for event in events:
            event_date = event.start_time.date()
            if event_date not in events_by_date:
                events_by_date[event_date] = []
            events_by_date[event_date].append(event)
        
        # Check conflicts
        all_conflicts = self.schedule_manager.get_all_conflicts()
        conflict_events = set()
        for event1, event2 in all_conflicts:
            conflict_events.add(event1.title)
            conflict_events.add(event2.title)
        
        html += f"""
        <div class="container">
            <div class="header">
                <h1>📅 My Calendar</h1>
                <p>{start_date.strftime('%B %Y')}</p>
            </div>
            
            <div class="content">
                <div class="calendar-grid">
                    <div class="calendar-header">Monday</div>
                    <div class="calendar-header">Tuesday</div>
                    <div class="calendar-header">Wednesday</div>
                    <div class="calendar-header">Thursday</div>
                    <div class="calendar-header">Friday</div>
                    <div class="calendar-header">Saturday</div>
                    <div class="calendar-header">Sunday</div>
        """
        
        current_date = calendar_start
        today = datetime.date.today()
        
        while current_date <= calendar_end:
            is_other_month = current_date.month != start_date.month
            is_today = current_date == today
            
            day_class = "calendar-day"
            if is_other_month:
                day_class += " other-month"
            if is_today:
                day_class += " today"
            
            html += f'<div class="{day_class}">'
            html += f'<div class="day-number">{current_date.day}</div>'
            
            # Add events for this day
            if current_date in events_by_date:
                for event in events_by_date[current_date]:
                    event_class = "day-event"
                    if event.title in conflict_events:
                        event_class += " conflict"
                    elif event.priority >= 4:
                        event_class += " high-priority"
                    
                    time_str = event.start_time.strftime('%H:%M')
                    html += f'<div class="{event_class}" title="{event.title} at {time_str}">{time_str} {event.title[:15]}{"..." if len(event.title) > 15 else ""}</div>'
            
            html += '</div>'
            current_date += datetime.timedelta(days=1)
        
        html += """
                </div>
            </div>
        </div>
        </body>
        </html>
        """
        
        return html
    
    def _generate_timeline_view(self, events: List, start_date: datetime.date, end_date: datetime.date) -> str:
        """Generate a timeline view of events"""
        
        additional_styles = """
        .timeline {
            position: relative;
            padding-left: 30px;
        }
        
        .timeline::before {
            content: '';
            position: absolute;
            left: 15px;
            top: 0;
            bottom: 0;
            width: 2px;
            background: var(--primary-color);
        }
        
        .timeline-item {
            position: relative;
            margin-bottom: 30px;
        }
        
        .timeline-item::before {
            content: '';
            position: absolute;
            left: -22px;
            top: 20px;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: var(--primary-color);
            border: 3px solid white;
            box-shadow: 0 0 0 3px var(--primary-color);
        }
        
        .timeline-item.conflict::before {
            background: var(--danger-color);
            box-shadow: 0 0 0 3px var(--danger-color);
        }
        
        .timeline-date {
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--primary-color);
            margin-bottom: 10px;
        }
        
        .timeline-events {
            margin-left: 20px;
        }
        """
        
        html = self._get_base_html_template("My Schedule - Timeline View", additional_styles)
        
        # Group events by date
        events_by_date = {}
        for event in events:
            event_date = event.start_time.date()
            if event_date not in events_by_date:
                events_by_date[event_date] = []
            events_by_date[event_date].append(event)
        
        # Check conflicts
        all_conflicts = self.schedule_manager.get_all_conflicts()
        conflict_events = set()
        for event1, event2 in all_conflicts:
            conflict_events.add(event1.title)
            conflict_events.add(event2.title)
        
        html += f"""
        <div class="container">
            <div class="header">
                <h1>⏰ My Timeline</h1>
                <p>{start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}</p>
            </div>
            
            <div class="content">
                <div class="timeline">
        """
        
        if not events:
            html += """
                <div class="no-events">
                    <div class="no-events-icon">⏰</div>
                    <h3>No events scheduled</h3>
                    <p>Your timeline is clear for this period.</p>
                </div>
            """
        else:
            sorted_dates = sorted(events_by_date.keys())
            
            for date in sorted_dates:
                day_events = sorted(events_by_date[date], key=lambda e: e.start_time)
                has_conflicts = any(event.title in conflict_events for event in day_events)
                
                html += f"""
                <div class="timeline-item{'conflict' if has_conflicts else ''}">
                    <div class="timeline-date">
                        {date.strftime('%A, %B %d, %Y')}
                    </div>
                    <div class="timeline-events">
                """
                
                for event in day_events:
                    is_conflict = event.title in conflict_events
                    card_class = "event-card" + (" conflict-warning" if is_conflict else "")
                    
                    html += f"""
                    <div class="{card_class}" style="margin-bottom: 12px;">
                        <div class="event-title">
                            {event.title}
                            {f'<span class="conflict-badge">CONFLICT</span>' if is_conflict else ''}
                        </div>
                        <div class="event-time">
                            🕐 {event.start_time.strftime('%I:%M %p')} - {event.end_time.strftime('%I:%M %p')}
                        </div>
                        {f'<div class="event-details">{event.description}</div>' if event.description else ''}
                        <div class="event-meta">
                            {f'<div class="meta-item">📍 {event.location}</div>' if event.location else ''}
                            <div class="meta-item">
                                <span class="priority-badge priority-{event.priority}">
                                    Priority {event.priority}
                                </span>
                            </div>
                        </div>
                    </div>
                    """
                
                html += "</div></div>"
        
        html += """
                </div>
            </div>
        </div>
        </body>
        </html>
        """
        
        return html
