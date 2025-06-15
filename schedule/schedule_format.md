# Schedule Management JSON Format Documentation

## Overview
This document describes the JSON format used for storing and managing calendar events in the schedule management system. The JSON file serves as persistent storage for all calendar events and their associated metadata.

## File Structure
The schedule is stored as a JSON array containing event objects. The default filename is `schedule.json`.

```json
[
  {
    "title": "Team Meeting",
    "start_time": "2024-01-15T14:00:00",
    "end_time": "2024-01-15T15:30:00",
    "description": "Weekly team sync meeting",
    "location": "Conference Room A",
    "priority": 3
  },
  {
    "title": "Doctor Appointment",
    "start_time": "2024-01-16T10:00:00",
    "end_time": "2024-01-16T11:00:00",
    "description": "Annual checkup",
    "location": "Medical Center",
    "priority": 4
  }
]
```

## Event Object Schema

Each event in the JSON array must contain the following fields:

### Required Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `title` | string | Event name/title | `"Team Meeting"` |
| `start_time` | string (ISO 8601) | Event start date and time | `"2024-01-15T14:00:00"` |
| `end_time` | string (ISO 8601) | Event end date and time | `"2024-01-15T15:30:00"` |

### Optional Fields

| Field | Type | Description | Default | Example |
|-------|------|-------------|---------|---------|
| `description` | string | Event description/notes | `""` | `"Weekly team sync meeting"` |
| `location` | string | Event location | `""` | `"Conference Room A"` |
| `priority` | integer | Priority level (1-5) | `1` | `3` |

## Date/Time Format
- **Format**: ISO 8601 format (`YYYY-MM-DDTHH:MM:SS`)
- **Timezone**: Local time (no timezone offset specified)
- **Examples**:
  - `"2024-01-15T14:00:00"` (January 15, 2024 at 2:00 PM)
  - `"2024-12-31T23:59:59"` (December 31, 2024 at 11:59:59 PM)

## Priority System
Events use a numerical priority system:
- `1`: Low priority
- `2`: Below normal
- `3`: Normal priority (default)
- `4`: High priority
- `5`: Critical priority

## Validation Rules

### Time Constraints
- `start_time` must be before `end_time`
- Both times must be valid ISO 8601 formatted strings

### Title Constraints
- Must be non-empty string
- Used for event identification in update/delete operations
- Case-insensitive matching for operations

### Priority Constraints
- Must be integer between 1 and 5 (inclusive)
- Values outside this range may cause errors

## Complete Example

```json
[
  {
    "title": "Project Kickoff Meeting",
    "start_time": "2024-01-15T09:00:00",
    "end_time": "2024-01-15T10:30:00",
    "description": "Initial meeting for the new web development project. Discuss requirements, timeline, and team assignments.",
    "location": "Main Conference Room",
    "priority": 5
  },
  {
    "title": "Lunch with Client",
    "start_time": "2024-01-15T12:00:00",
    "end_time": "2024-01-15T13:30:00",
    "description": "Business lunch to discuss contract renewal",
    "location": "Downtown Restaurant",
    "priority": 4
  },
  {
    "title": "Code Review Session",
    "start_time": "2024-01-15T15:00:00",
    "end_time": "2024-01-15T16:00:00",
    "description": "Review pull requests for the authentication module",
    "location": "Development Office",
    "priority": 2
  },
  {
    "title": "Personal Workout",
    "start_time": "2024-01-15T18:00:00",
    "end_time": "2024-01-15T19:00:00",
    "description": "",
    "location": "Local Gym",
    "priority": 1
  }
]
```

## Conflict Detection Logic

Events are considered conflicting when their time periods overlap:
- Event A conflicts with Event B if:
  - `A.start_time < B.end_time` AND `A.end_time > B.start_time`

## File Operations

### Reading Schedule
- Load JSON file and parse array of event objects
- Handle missing file (empty schedule)
- Handle malformed JSON (reset to empty schedule)

### Writing Schedule
- Sort events chronologically by `start_time`
- Write formatted JSON with 2-space indentation
- Atomic file operations to prevent corruption

### Event Management
- **Add**: Append new event, check conflicts, sort, save
- **Remove**: Filter out events by title (case-insensitive), save
- **Update**: Modify existing event fields, validate, check new conflicts, save

## Error Handling

Common error scenarios:
1. **Invalid date format**: Return error message with expected format
2. **Start time after end time**: Validation error
3. **Missing required fields**: Return field-specific error
4. **File access issues**: Handle permissions/disk space problems
5. **Event not found**: Clear error message for update/delete operations

## Integration Notes

When integrating with AI systems:
- Always validate JSON structure before processing
- Provide clear error messages for malformed data
- Support partial updates (only specified fields changed)
- Maintain chronological sorting for better user experience
- Implement conflict detection before confirming operations