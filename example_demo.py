import numpy as np

# Sample events (subset from the original)
events = [
    {"event": "Failed SSH login", "severity": "warning", "actions": ["ignored", "blocked"]},
    {"event": "RDP brute force attempt", "severity": "critical", "actions": ["blocked", "reported"]},
    {"event": "Suspicious DNS activity", "severity": "info", "actions": ["monitored", "allowed"]},
]

n = 5
np.random.seed(42)  # For reproducible results

# Step by step execution:
event_indices = np.random.randint(0, len(events), n)
print(f"event_indices: {event_indices}")
# Output: [1 0 2 1 0]

chosen_events = [events[i] for i in event_indices]
print(f"chosen_events: {chosen_events}")
# Output: [
#   {"event": "RDP brute force attempt", "severity": "critical", "actions": ["blocked", "reported"]},
#   {"event": "Failed SSH login", "severity": "warning", "actions": ["ignored", "blocked"]},
#   {"event": "Suspicious DNS activity", "severity": "info", "actions": ["monitored", "allowed"]},
#   {"event": "RDP brute force attempt", "severity": "critical", "actions": ["blocked", "reported"]},
#   {"event": "Failed SSH login", "severity": "warning", "actions": ["ignored", "blocked"]}
# ]

event_names = [e['event'] for e in chosen_events]
print(f"event_names: {event_names}")
# Output: ['RDP brute force attempt', 'Failed SSH login', 'Suspicious DNS activity', 'RDP brute force attempt', 'Failed SSH login']

severities = [e['severity'] for e in chosen_events]
print(f"severities: {severities}")
# Output: ['critical', 'warning', 'info', 'critical', 'warning']

actions_list = [e['actions'] for e in chosen_events]
print(f"actions_list: {actions_list}")
# Output: [['blocked', 'reported'], ['ignored', 'blocked'], ['monitored', 'allowed'], ['blocked', 'reported'], ['ignored', 'blocked']]

actions = [np.random.choice(a) for a in actions_list]
print(f"actions: {actions}")
# Output: ['blocked', 'blocked', 'allowed', 'reported', 'ignored']