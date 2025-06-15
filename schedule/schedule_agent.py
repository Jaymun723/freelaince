import json
import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from smolagents import CodeAgent, Tool
import re

@dataclass
class Event:
    """Represents a calendar event"""
    title: str
    start_time: datetime.datetime
    end_time: datetime.datetime
    description: str = ""
    location: str = ""
    priority: int = 1  # 1-5, where 5 is highest priority
    
    def __post_init__(self):
        if self.start_time >= self.end_time:
            raise ValueError("Start time must be before end time")
    
    def overlaps_with(self, other: 'Event') -> bool:
        """Check if this event overlaps with another event"""
        return (self.start_time < other.end_time and 
                self.end_time > other.start_time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for JSON serialization"""
        return {
            'title': self.title,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'description': self.description,
            'location': self.location,
            'priority': self.priority
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """Create event from dictionary"""
        return cls(
            title=data['title'],
            start_time=datetime.datetime.fromisoformat(data['start_time']),
            end_time=datetime.datetime.fromisoformat(data['end_time']),
            description=data.get('description', ''),
            location=data.get('location', ''),
            priority=data.get('priority', 1)
        )

class ScheduleManager:
    """Manages calendar events and provides conflict resolution"""
    
    def __init__(self, storage_file: str = "schedule.json"):
        self.storage_file = storage_file
        self.events: List[Event] = []
        self.load_events()
    
    def load_events(self):
        """Load events from storage file"""
        try:
            with open(self.storage_file, 'r') as f:
                data = json.load(f)
                self.events = [Event.from_dict(event_data) for event_data in data]
        except (FileNotFoundError, json.JSONDecodeError):
            self.events = []
    
    def save_events(self):
        """Save events to storage file"""
        with open(self.storage_file, 'w') as f:
            json.dump([event.to_dict() for event in self.events], f, indent=2)
    
    def add_event(self, event: Event) -> Dict[str, Any]:
        """Add an event and check for conflicts"""
        conflicts = self.find_conflicts(event)
        
        self.events.append(event)
        self.events.sort(key=lambda e: e.start_time)
        self.save_events()
        
        result = {
            "success": True,
            "message": f"Event '{event.title}' added successfully",
            "event": event.to_dict(),
            "conflicts": [conflict.to_dict() for conflict in conflicts]
        }
        
        if conflicts:
            result["message"] += f" (Warning: {len(conflicts)} conflict(s) detected)"
        
        return result
    
    def remove_event(self, title: str) -> Dict[str, Any]:
        """Remove an event by title"""
        original_count = len(self.events)
        self.events = [e for e in self.events if e.title.lower() != title.lower()]
        
        if len(self.events) < original_count:
            self.save_events()
            return {
                "success": True,
                "message": f"Event '{title}' removed successfully"
            }
        else:
            return {
                "success": False,
                "message": f"Event '{title}' not found"
            }
    
    def find_conflicts(self, target_event: Event) -> List[Event]:
        """Find all events that conflict with the target event"""
        conflicts = []
        for event in self.events:
            if event.overlaps_with(target_event):
                conflicts.append(event)
        return conflicts
    
    def get_all_conflicts(self) -> List[Tuple[Event, Event]]:
        """Find all conflicting event pairs"""
        conflicts = []
        for i, event1 in enumerate(self.events):
            for event2 in self.events[i+1:]:
                if event1.overlaps_with(event2):
                    conflicts.append((event1, event2))
        return conflicts
    
    def suggest_conflict_resolution(self, event1: Event, event2: Event) -> List[str]:
        """Suggest ways to resolve conflicts between two events"""
        suggestions = []
        
        # Priority-based suggestions
        if event1.priority > event2.priority:
            suggestions.append(f"Keep '{event1.title}' (higher priority) and reschedule '{event2.title}'")
        elif event2.priority > event1.priority:
            suggestions.append(f"Keep '{event2.title}' (higher priority) and reschedule '{event1.title}'")
        
        # Time-based suggestions
        duration1 = event1.end_time - event1.start_time
        duration2 = event2.end_time - event2.start_time
        
        # Suggest moving shorter event
        if duration1 < duration2:
            suggestions.append(f"Move '{event1.title}' (shorter duration) to before or after '{event2.title}'")
        else:
            suggestions.append(f"Move '{event2.title}' (shorter duration) to before or after '{event1.title}'")
        
        # Suggest alternative times
        suggestions.append(f"Move '{event1.title}' to end at {event2.start_time.strftime('%Y-%m-%d %H:%M')}")
        suggestions.append(f"Move '{event2.title}' to start at {event1.end_time.strftime('%Y-%m-%d %H:%M')}")
        
        # Suggest shortening events
        overlap_start = max(event1.start_time, event2.start_time)
        overlap_end = min(event1.end_time, event2.end_time)
        overlap_duration = overlap_end - overlap_start
        
        if overlap_duration < duration1:
            suggestions.append(f"Shorten '{event1.title}' to avoid overlap")
        if overlap_duration < duration2:
            suggestions.append(f"Shorten '{event2.title}' to avoid overlap")
        
        return suggestions
    
    def get_schedule(self, start_date: Optional[datetime.date] = None, 
                    end_date: Optional[datetime.date] = None) -> List[Event]:
        """Get events within a date range"""
        if start_date is None:
            start_date = datetime.date.today()
        if end_date is None:
            end_date = start_date + datetime.timedelta(days=7)
        
        filtered_events = []
        for event in self.events:
            event_date = event.start_time.date()
            if start_date <= event_date <= end_date:
                filtered_events.append(event)
        
        return filtered_events

# Tool Classes with proper nullable handling
class AddEventTool(Tool):
    name = "add_event"
    description = "Add a new event to the schedule"
    
    inputs = {
        "title": {
            "type": "string", 
            "description": "Event title"
        },
        "start_time": {
            "type": "string", 
            "description": "Start time in format 'YYYY-MM-DD HH:MM'"
        },
        "end_time": {
            "type": "string", 
            "description": "End time in format 'YYYY-MM-DD HH:MM'"
        },
        "description": {
            "type": "string", 
            "description": "Optional event description",
            "nullable": True
        },
        "location": {
            "type": "string", 
            "description": "Optional event location",
            "nullable": True
        },
        "priority": {
            "type": "integer", 
            "description": "Priority level (1-5, where 5 is highest)",
            "nullable": True
        }
    }
    
    output_type = "string"
    
    def __init__(self, schedule_manager: ScheduleManager):
        super().__init__()
        self.schedule_manager = schedule_manager
    
    def forward(self, title: str, start_time: str, end_time: str, 
                description: Optional[str] = None, location: Optional[str] = None, 
                priority: Optional[int] = None) -> str:
        """Add a new event to the schedule"""
        try:
            start_dt = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M')
            end_dt = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M')
            
            event = Event(
                title=title,
                start_time=start_dt,
                end_time=end_dt,
                description=description or "",
                location=location or "",
                priority=priority or 1
            )
            
            result = self.schedule_manager.add_event(event)
            return json.dumps(result, indent=2)
            
        except ValueError as e:
            return json.dumps({
                "success": False,
                "message": f"Error creating event: {str(e)}"
            })

class RemoveEventTool(Tool):
    name = "remove_event"
    description = "Remove an event from the schedule by title"
    
    inputs = {
        "title": {
            "type": "string",
            "description": "Title of the event to remove"
        }
    }
    
    output_type = "string"
    
    def __init__(self, schedule_manager: ScheduleManager):
        super().__init__()
        self.schedule_manager = schedule_manager
    
    def forward(self, title: str) -> str:
        """Remove an event from the schedule by title"""
        result = self.schedule_manager.remove_event(title)
        return json.dumps(result, indent=2)

class ViewScheduleTool(Tool):
    name = "view_schedule"
    description = "View schedule for a date range"
    
    inputs = {
        "start_date": {
            "type": "string",
            "description": "Start date in format 'YYYY-MM-DD' (default: today)",
            "nullable": True
        },
        "days": {
            "type": "integer",
            "description": "Number of days to show (default: 7)",
            "nullable": True
        }
    }
    
    output_type = "string"
    
    def __init__(self, schedule_manager: ScheduleManager):
        super().__init__()
        self.schedule_manager = schedule_manager
    
    def forward(self, start_date: Optional[str] = None, days: Optional[int] = None) -> str:
        """View schedule for a date range"""
        try:
            if start_date:
                start = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
            else:
                start = datetime.date.today()
            
            days = days or 7
            end = start + datetime.timedelta(days=days-1)
            events = self.schedule_manager.get_schedule(start, end)
            
            return json.dumps({
                "success": True,
                "period": f"{start} to {end}",
                "events": [event.to_dict() for event in events],
                "total_events": len(events)
            }, indent=2)
            
        except ValueError as e:
            return json.dumps({
                "success": False,
                "message": f"Error viewing schedule: {str(e)}"
            })

class CheckConflictsTool(Tool):
    name = "check_conflicts"
    description = "Check for scheduling conflicts and get resolution suggestions"
    
    inputs = {}
    output_type = "string"
    
    def __init__(self, schedule_manager: ScheduleManager):
        super().__init__()
        self.schedule_manager = schedule_manager
    
    def forward(self) -> str:
        """Check for scheduling conflicts and get resolution suggestions"""
        conflicts = self.schedule_manager.get_all_conflicts()
        
        result = {
            "success": True,
            "total_conflicts": len(conflicts),
            "conflicts": []
        }
        
        for event1, event2 in conflicts:
            suggestions = self.schedule_manager.suggest_conflict_resolution(event1, event2)
            result["conflicts"].append({
                "event1": event1.to_dict(),
                "event2": event2.to_dict(),
                "suggestions": suggestions
            })
        
        return json.dumps(result, indent=2)

class UpdateEventTool(Tool):
    name = "update_event"
    description = "Update an existing event"
    
    inputs = {
        "old_title": {
            "type": "string",
            "description": "Current title of the event to update"
        },
        "new_title": {
            "type": "string",
            "description": "New title (optional)",
            "nullable": True
        },
        "new_start_time": {
            "type": "string",
            "description": "New start time in format 'YYYY-MM-DD HH:MM' (optional)",
            "nullable": True
        },
        "new_end_time": {
            "type": "string",
            "description": "New end time in format 'YYYY-MM-DD HH:MM' (optional)",
            "nullable": True
        },
        "new_description": {
            "type": "string",
            "description": "New description (optional)",
            "nullable": True
        },
        "new_location": {
            "type": "string",
            "description": "New location (optional)",
            "nullable": True
        },
        "new_priority": {
            "type": "integer",
            "description": "New priority 1-5 (optional, 0 means no change)",
            "nullable": True
        }
    }
    
    output_type = "string"
    
    def __init__(self, schedule_manager: ScheduleManager):
        super().__init__()
        self.schedule_manager = schedule_manager
    
    def forward(self, old_title: str, new_title: Optional[str] = None, 
                new_start_time: Optional[str] = None, new_end_time: Optional[str] = None, 
                new_description: Optional[str] = None, new_location: Optional[str] = None, 
                new_priority: Optional[int] = None) -> str:
        """Update an existing event"""
        try:
            # Find the event
            event_to_update = None
            for event in self.schedule_manager.events:
                if event.title.lower() == old_title.lower():
                    event_to_update = event
                    break
            
            if not event_to_update:
                return json.dumps({
                    "success": False,
                    "message": f"Event '{old_title}' not found"
                })
            
            # Update fields only if new values are provided
            if new_title is not None:
                event_to_update.title = new_title
            if new_start_time is not None:
                event_to_update.start_time = datetime.datetime.strptime(new_start_time, '%Y-%m-%d %H:%M')
            if new_end_time is not None:
                event_to_update.end_time = datetime.datetime.strptime(new_end_time, '%Y-%m-%d %H:%M')
            if new_description is not None:
                event_to_update.description = new_description
            if new_location is not None:
                event_to_update.location = new_location
            if new_priority is not None and new_priority > 0:
                event_to_update.priority = new_priority
            
            # Validate updated event
            if event_to_update.start_time >= event_to_update.end_time:
                return json.dumps({
                    "success": False,
                    "message": "Start time must be before end time"
                })
            
            # Check for new conflicts
            conflicts = []
            for other_event in self.schedule_manager.events:
                if other_event != event_to_update and event_to_update.overlaps_with(other_event):
                    conflicts.append(other_event)
            
            self.schedule_manager.save_events()
            
            result = {
                "success": True,
                "message": f"Event updated successfully",
                "updated_event": event_to_update.to_dict(),
                "conflicts": [conflict.to_dict() for conflict in conflicts]
            }
            
            if conflicts:
                result["message"] += f" (Warning: {len(conflicts)} conflict(s) detected)"
            
            return json.dumps(result, indent=2)
            
        except ValueError as e:
            return json.dumps({
                "success": False,
                "message": f"Error updating event: {str(e)}"
            })


class BeautifulScheduleTool(Tool):
    name = "show_beautiful_schedule"
    description = "Display the schedule in a beautiful, formatted view with colors and visual elements. This view has to be showed to the user exactlyy this way"
    
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
            "description": "Display format: 'timeline', 'agenda', 'calendar', or 'compact' (default: 'timeline')",
            "default": "timeline",
            "nullable": True
        },
        "show_conflicts": {
            "type": "boolean",
            "description": "Highlight conflicting events (default: true)",
            "default": True,
            "nullable": True
        }
    }
    
    output_type = "string"
    
    def __init__(self, schedule_manager):
        super().__init__()
        self.schedule_manager = schedule_manager
        
        # Color and styling constants
        self.colors = {
            'header': '\033[95m',      # Magenta
            'date': '\033[94m',        # Blue
            'time': '\033[92m',        # Green
            'title': '\033[93m',       # Yellow
            'description': '\033[96m', # Cyan
            'location': '\033[97m',    # White
            'priority_high': '\033[91m',  # Red
            'priority_medium': '\033[93m', # Yellow
            'priority_low': '\033[92m',    # Green
            'conflict': '\033[41m',    # Red background
            'end': '\033[0m',          # Reset
            'bold': '\033[1m',         # Bold
            'underline': '\033[4m'     # Underline
        }
        
        # Emoji mappings
        self.priority_emojis = {
            5: "🔥", 4: "⭐", 3: "📋", 2: "📝", 1: "💭"
        }
        
        self.day_emojis = {
            0: "🌙", 1: "🌅", 2: "🌞", 3: "🌅", 4: "🌟", 5: "🎉", 6: "🌙"
        }
    
    def forward(self, start_date: str = "", days: int = 7, 
                view_type: str = "timeline", show_conflicts: bool = True) -> str:
        """Display the schedule in a beautiful, formatted view"""
        try:
            # Parse start date
            if start_date:
                start = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
            else:
                start = datetime.date.today()
            
            end = start + datetime.timedelta(days=days-1)
            events = self.schedule_manager.get_schedule(start, end)
            
            # Get conflicts if requested
            conflicts = []
            if show_conflicts:
                all_conflicts = self.schedule_manager.get_all_conflicts()
                conflict_events = set()
                for event1, event2 in all_conflicts:
                    conflict_events.add(event1.title)
                    conflict_events.add(event2.title)
                conflicts = list(conflict_events)
            
            # Generate the beautiful display based on view type
            if view_type == "timeline":
                display = self._create_timeline_view(events, start, end, conflicts)
            elif view_type == "agenda":
                display = self._create_agenda_view(events, start, end, conflicts)
            elif view_type == "calendar":
                display = self._create_calendar_view(events, start, end, conflicts)
            elif view_type == "compact":
                display = self._create_compact_view(events, start, end, conflicts)
            else:
                display = self._create_timeline_view(events, start, end, conflicts)
            
            return display
            
        except ValueError as e:
            return f"Error displaying schedule: {str(e)}"
    
    def _create_timeline_view(self, events: List, start_date: datetime.date, 
                             end_date: datetime.date, conflicts: List[str]) -> str:
        """Create a timeline-style view of the schedule"""
        output = []
        
        # Header
        output.append(f"\n{self.colors['header']}{self.colors['bold']}")
        output.append("┌─────────────────────────────────────────────────────────────────────┐")
        output.append("│                        📅 YOUR SCHEDULE                            │")
        output.append("└─────────────────────────────────────────────────────────────────────┘")
        output.append(f"{self.colors['end']}")
        
        # Date range
        output.append(f"{self.colors['date']}{self.colors['bold']}")
        output.append(f"📆 Period: {start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}")
        output.append(f"📊 Total Events: {len(events)}")
        if conflicts:
            output.append(f"⚠️  Conflicts Detected: {len(conflicts)} events")
        output.append(f"{self.colors['end']}\n")
        
        # Group events by date
        events_by_date = {}
        for event in events:
            event_date = event.start_time.date()
            if event_date not in events_by_date:
                events_by_date[event_date] = []
            events_by_date[event_date].append(event)
        
        # Display each day
        current_date = start_date
        while current_date <= end_date:
            day_name = current_date.strftime('%A')
            day_emoji = self.day_emojis[current_date.weekday()]
            
            output.append(f"{self.colors['date']}{self.colors['bold']}")
            output.append(f"{day_emoji} {day_name}, {current_date.strftime('%B %d, %Y')}")
            output.append("─" * 50)
            output.append(f"{self.colors['end']}")
            
            if current_date in events_by_date:
                day_events = sorted(events_by_date[current_date], key=lambda x: x.start_time)
                
                for i, event in enumerate(day_events):
                    is_conflict = event.title in conflicts
                    priority_emoji = self.priority_emojis.get(event.priority, "📋")
                    
                    # Time display
                    start_time = event.start_time.strftime('%H:%M')
                    end_time = event.end_time.strftime('%H:%M')
                    duration = event.end_time - event.start_time
                    duration_str = f"{duration.seconds // 3600}h {(duration.seconds % 3600) // 60}m"
                    
                    # Event line
                    if is_conflict:
                        output.append(f"{self.colors['conflict']}{self.colors['bold']}")
                        output.append(f"⚠️  {start_time} - {end_time} │ {priority_emoji} {event.title}")
                        output.append(f"{self.colors['end']}")
                    else:
                        priority_color = self._get_priority_color(event.priority)
                        output.append(f"{self.colors['time']}{start_time} - {end_time}{self.colors['end']} │ "
                                    f"{priority_color}{priority_emoji} {event.title}{self.colors['end']}")
                    
                    # Duration and location
                    details = []
                    if duration_str != "0h 0m":
                        details.append(f"⏱️  {duration_str}")
                    if event.location:
                        details.append(f"📍 {event.location}")
                    
                    if details:
                        output.append(f"    {self.colors['description']}{' │ '.join(details)}{self.colors['end']}")
                    
                    # Description
                    if event.description:
                        desc_lines = self._wrap_text(event.description, 60)
                        for line in desc_lines:
                            output.append(f"    {self.colors['description']}💬 {line}{self.colors['end']}")
                    
                    # Add spacing between events
                    if i < len(day_events) - 1:
                        output.append("    │")
            else:
                output.append(f"    {self.colors['description']}🌟 No events scheduled{self.colors['end']}")
            
            output.append("")
            current_date += datetime.timedelta(days=1)
        
        return "\n".join(output)
    
    def _create_agenda_view(self, events: List, start_date: datetime.date, 
                           end_date: datetime.date, conflicts: List[str]) -> str:
        """Create an agenda-style view of the schedule"""
        output = []
        
        # Header
        output.append(f"\n{self.colors['header']}{self.colors['bold']}")
        output.append("╔════════════════════════════════════════════════════════════════════╗")
        output.append("║                          📋 AGENDA VIEW                           ║")
        output.append("╚════════════════════════════════════════════════════════════════════╝")
        output.append(f"{self.colors['end']}")
        
        if not events:
            output.append(f"\n{self.colors['description']}🌟 No events in this period{self.colors['end']}")
            return "\n".join(output)
        
        # Sort all events by start time
        sorted_events = sorted(events, key=lambda x: x.start_time)
        
        for i, event in enumerate(sorted_events):
            is_conflict = event.title in conflicts
            priority_emoji = self.priority_emojis.get(event.priority, "📋")
            priority_color = self._get_priority_color(event.priority)
            
            # Event header
            event_date = event.start_time.strftime('%A, %B %d')
            event_time = f"{event.start_time.strftime('%H:%M')} - {event.end_time.strftime('%H:%M')}"
            
            if is_conflict:
                output.append(f"\n{self.colors['conflict']}{self.colors['bold']}")
                output.append(f"⚠️  CONFLICT: {priority_emoji} {event.title}")
                output.append(f"{self.colors['end']}")
            else:
                output.append(f"\n{priority_color}{self.colors['bold']}")
                output.append(f"{priority_emoji} {event.title}")
                output.append(f"{self.colors['end']}")
            
            # Event details
            output.append(f"    {self.colors['date']}📅 {event_date}{self.colors['end']}")
            output.append(f"    {self.colors['time']}⏰ {event_time}{self.colors['end']}")
            
            if event.location:
                output.append(f"    {self.colors['location']}📍 {event.location}{self.colors['end']}")
            
            if event.description:
                desc_lines = self._wrap_text(event.description, 60)
                output.append(f"    {self.colors['description']}💬 Description:{self.colors['end']}")
                for line in desc_lines:
                    output.append(f"       {self.colors['description']}{line}{self.colors['end']}")
            
            # Priority indicator
            priority_text = ["", "Low", "Medium-Low", "Medium", "Medium-High", "High"][event.priority]
            output.append(f"    {priority_color}⭐ Priority: {priority_text}{self.colors['end']}")
            
            # Separator
            if i < len(sorted_events) - 1:
                output.append(f"    {self.colors['description']}{'─' * 50}{self.colors['end']}")
        
        return "\n".join(output)
    
    def _create_calendar_view(self, events: List, start_date: datetime.date, 
                             end_date: datetime.date, conflicts: List[str]) -> str:
        """Create a calendar grid view of the schedule"""
        output = []
        
        # Header
        output.append(f"\n{self.colors['header']}{self.colors['bold']}")
        output.append("╔════════════════════════════════════════════════════════════════════╗")
        output.append("║                        📅 CALENDAR VIEW                           ║")
        output.append("╚════════════════════════════════════════════════════════════════════╝")
        output.append(f"{self.colors['end']}")
        
        # Group events by date
        events_by_date = {}
        for event in events:
            event_date = event.start_time.date()
            if event_date not in events_by_date:
                events_by_date[event_date] = []
            events_by_date[event_date].append(event)
        
        # Create calendar grid
        current_date = start_date
        while current_date <= end_date:
            day_events = events_by_date.get(current_date, [])
            day_name = current_date.strftime('%a')
            day_num = current_date.strftime('%d')
            
            # Day header
            if day_events:
                event_count = len(day_events)
                conflict_count = sum(1 for e in day_events if e.title in conflicts)
                
                if conflict_count > 0:
                    output.append(f"{self.colors['conflict']}{self.colors['bold']}")
                    output.append(f"⚠️  {day_name} {day_num} │ {event_count} events ({conflict_count} conflicts)")
                else:
                    output.append(f"{self.colors['date']}{self.colors['bold']}")
                    output.append(f"📅 {day_name} {day_num} │ {event_count} events")
                output.append(f"{self.colors['end']}")
                
                # Show events for this day
                for event in sorted(day_events, key=lambda x: x.start_time):
                    time_str = f"{event.start_time.strftime('%H:%M')}-{event.end_time.strftime('%H:%M')}"
                    priority_emoji = self.priority_emojis.get(event.priority, "📋")
                    
                    if event.title in conflicts:
                        output.append(f"   ⚠️  {time_str} {priority_emoji} {event.title}")
                    else:
                        priority_color = self._get_priority_color(event.priority)
                        output.append(f"   {self.colors['time']}{time_str}{self.colors['end']} "
                                    f"{priority_color}{priority_emoji} {event.title}{self.colors['end']}")
            else:
                output.append(f"{self.colors['description']}{day_name} {day_num} │ No events{self.colors['end']}")
            
            output.append("")
            current_date += datetime.timedelta(days=1)
        
        return "\n".join(output)
    
    def _create_compact_view(self, events: List, start_date: datetime.date, 
                           end_date: datetime.date, conflicts: List[str]) -> str:
        """Create a compact view of the schedule"""
        output = []
        
        # Header
        output.append(f"\n{self.colors['header']}{self.colors['bold']}")
        output.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        output.append("                            📊 COMPACT SCHEDULE")
        output.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        output.append(f"{self.colors['end']}")
        
        if not events:
            output.append(f"\n{self.colors['description']}🌟 No events scheduled{self.colors['end']}")
            return "\n".join(output)
        
        # Sort events by start time
        sorted_events = sorted(events, key=lambda x: x.start_time)
        
        # Create compact table
        output.append(f"{self.colors['bold']}")
        output.append("┌─────────────┬───────────────┬─────────────────────────────────────────┐")
        output.append("│    DATE     │     TIME      │                 EVENT                   │")
        output.append("├─────────────┼───────────────┼─────────────────────────────────────────┤")
        output.append(f"{self.colors['end']}")
        
        for event in sorted_events:
            date_str = event.start_time.strftime('%m/%d')
            time_str = f"{event.start_time.strftime('%H:%M')}-{event.end_time.strftime('%H:%M')}"
            priority_emoji = self.priority_emojis.get(event.priority, "📋")
            
            # Truncate title if too long
            title = event.title
            if len(title) > 35:
                title = title[:32] + "..."
            
            if event.title in conflicts:
                output.append(f"│ {self.colors['conflict']} {date_str:^9} {self.colors['end']} │ "
                            f"{self.colors['conflict']} {time_str:^11} {self.colors['end']} │ "
                            f"{self.colors['conflict']} ⚠️ {priority_emoji} {title:<35} {self.colors['end']} │")
            else:
                priority_color = self._get_priority_color(event.priority)
                output.append(f"│ {self.colors['date']} {date_str:^9} {self.colors['end']} │ "
                            f"{self.colors['time']} {time_str:^11} {self.colors['end']} │ "
                            f"{priority_color} {priority_emoji} {title:<35} {self.colors['end']} │")
        
        output.append("└─────────────┴───────────────┴─────────────────────────────────────────┘")
        
        # Summary
        total_events = len(events)
        conflict_events = len([e for e in events if e.title in conflicts])
        
        output.append(f"\n{self.colors['description']}")
        output.append(f"📊 Summary: {total_events} events")
        if conflict_events > 0:
            output.append(f"⚠️  {conflict_events} events have conflicts")
        output.append(f"{self.colors['end']}")
        
        return "\n".join(output)
    
    def _get_priority_color(self, priority: int) -> str:
        """Get color based on priority level"""
        if priority >= 4:
            return self.colors['priority_high']
        elif priority >= 3:
            return self.colors['priority_medium']
        else:
            return self.colors['priority_low']
    
    def _wrap_text(self, text: str, width: int) -> List[str]:
        """Wrap text to specified width"""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= width:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
                current_length = len(word)
        
        if current_line:
            lines.append(" ".join(current_line))
        
        return lines if lines else [""]

# Update the create_schedule_agent function to include the beautiful schedule tool
def create_schedule_agent(code_agent: CodeAgent) -> CodeAgent:
    """Create a schedule management agent with the given CodeAgent as base"""
    
    # Initialize the schedule manager
    schedule_manager = ScheduleManager()
    
    # Create tool instances (including the new beautiful schedule tool)
    tools = [
        AddEventTool(schedule_manager),
        RemoveEventTool(schedule_manager),
        ViewScheduleTool(schedule_manager),
        BeautifulScheduleTool(schedule_manager),  # New beautiful display tool
        CheckConflictsTool(schedule_manager),
        UpdateEventTool(schedule_manager)
    ]
    
    # Add tools to the agent
    code_agent.tools.extend(tools)
    
    # Update the agent's system prompt
    original_prompt = getattr(code_agent, 'system_prompt', '')
    schedule_prompt = """

You are now enhanced with comprehensive schedule management capabilities. You can help users:

1. **Add Events**: Create new calendar events with title, time, description, location, and priority
2. **Remove Events**: Delete events by title
3. **View Schedule**: Display events for any date range
4. **Beautiful Schedule Display**: Show schedule in beautiful, formatted views with colors and emojis
5. **Check Conflicts**: Identify scheduling conflicts and provide resolution suggestions
6. **Update Events**: Modify existing events

**Key Features:**
- Automatic conflict detection when adding/updating events
- Priority-based conflict resolution suggestions
- Beautiful visual schedule displays with multiple view types
- Color-coded priority levels and conflict highlighting
- Persistent storage of events
- Flexible date/time handling

**Available Tools:**
- `add_event` - Add new event with full details
- `remove_event` - Remove event by title  
- `view_schedule` - View schedule for date range (basic format)
- `show_beautiful_schedule` - Display schedule with beautiful formatting and colors
- `check_conflicts` - Find and analyze all conflicts
- `update_event` - Update existing event

**Beautiful Schedule View Types:**
- **timeline**: Day-by-day timeline with detailed event information
- **agenda**: Chronological list with full event details
- **calendar**: Calendar grid showing events per day
- **compact**: Condensed table format for quick overview

**Time Format:** Use 'YYYY-MM-DD HH:MM' for all times (e.g., '2024-01-15 14:30')
**Date Format:** Use 'YYYY-MM-DD' for dates (e.g., '2024-01-15')
**Priority:** 1-5 scale where 5 is highest priority

When users ask to see their schedule, prefer using the `show_beautiful_schedule` tool for better visual experience.
Conflicts are automatically highlighted in red, and priorities are color-coded and marked with emojis.

Be proactive in helping users resolve conflicts and maintain an organized, visually appealing schedule.
"""
    
    code_agent.system_prompt = original_prompt + schedule_prompt
    
    return code_agent

def create_schedule_agent(code_agent: CodeAgent) -> CodeAgent:
    """Create a schedule management agent with the given CodeAgent as base"""
    
    # Initialize the schedule manager
    schedule_manager = ScheduleManager()
    
    # Create tool instances
    tools = [
        AddEventTool(schedule_manager),
        RemoveEventTool(schedule_manager),
        ViewScheduleTool(schedule_manager),
        CheckConflictsTool(schedule_manager),
        UpdateEventTool(schedule_manager)
    ]
    
    # Add tools to the agent
    code_agent.tools.extend(tools)
    
    # Update the agent's system prompt to include schedule management capabilities
    original_prompt = getattr(code_agent, 'system_prompt', '')
    schedule_prompt = """

You are now enhanced with comprehensive schedule management capabilities. You can help users:

1. **Add Events**: Create new calendar events with title, time, description, location, and priority
2. **Remove Events**: Delete events by title
3. **View Schedule**: Display events for any date range
4. **Check Conflicts**: Identify scheduling conflicts and provide resolution suggestions
5. **Update Events**: Modify existing events

**Key Features:**
- Automatic conflict detection when adding/updating events
- Priority-based conflict resolution suggestions
- Persistent storage of events
- Flexible date/time handling
- Comprehensive event information tracking

**Available Tools:**
- `add_event` - Add new event with full details
- `remove_event` - Remove event by title  
- `view_schedule` - View schedule for date range
- `check_conflicts` - Find and analyze all conflicts
- `update_event` - Update existing event

**Time Format:** Use 'YYYY-MM-DD HH:MM' for all times (e.g., '2024-01-15 14:30')
**Date Format:** Use 'YYYY-MM-DD' for dates (e.g., '2024-01-15')
**Priority:** 1-5 scale where 5 is highest priority

When conflicts are detected, always provide helpful suggestions based on:
- Event priorities
- Event durations
- Available time slots
- Practical scheduling options

Be proactive in helping users resolve conflicts and maintain an organized schedule.
"""
    
    code_agent.system_prompt = original_prompt + schedule_prompt
    
    return code_agent

# Example usage
if __name__ == "__main__":
    # Create a base CodeAgent (you would import this from smolagents)
    base_agent = CodeAgent()  # This should be your actual CodeAgent instance
    
    # Create the enhanced schedule agent
    schedule_agent = create_schedule_agent(base_agent)
    
    # Example interactions
    print("Schedule Management Agent Created!")
    print("Available tools:")
    for tool in schedule_agent.tools[-5:]:  # Show the last 5 tools (our schedule tools)
        print(f"- {tool.name}: {tool.description}")
    
    print("\nYou can now use commands like:")
    print("- 'Add a meeting tomorrow at 2 PM for 1 hour'")
    print("- 'Show my schedule for this week'")
    print("- 'Check for any scheduling conflicts'")
    print("- 'Remove the dentist appointment'")
    print("- 'Update my lunch meeting to start at 1 PM'")