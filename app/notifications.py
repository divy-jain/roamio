# app/notifications.py

from flask import Response, current_app
import json
import queue
import threading
from datetime import datetime

class NotificationSystem:
    def __init__(self):
        self.listeners = {}
        self._lock = threading.Lock()
        
    def add_listener(self, user_id):
        """Add a new listener for a specific user"""
        with self._lock:
            if user_id not in self.listeners:
                self.listeners[user_id] = []
            q = queue.Queue(maxsize=5)
            self.listeners[user_id].append(q)
            return q
            
    def remove_listener(self, user_id, queue):
        """Remove a listener for a specific user"""
        with self._lock:
            if user_id in self.listeners:
                try:
                    self.listeners[user_id].remove(queue)
                except ValueError:
                    pass
                    
    def notify_user(self, user_id, event_type, data):
        """Send a notification to a specific user"""
        if user_id in self.listeners:
            message = {
                'type': event_type,
                'data': data,
                'timestamp': datetime.utcnow().isoformat()
            }
            with self._lock:
                dead_queues = []
                for q in self.listeners[user_id]:
                    try:
                        q.put_nowait(message)
                    except queue.Full:
                        dead_queues.append(q)
                
                # Clean up dead queues
                for q in dead_queues:
                    try:
                        self.listeners[user_id].remove(q)
                    except ValueError:
                        pass

notification_system = NotificationSystem()

def event_stream(user_id):
    """Generate SSE events for a user"""
    q = notification_system.add_listener(user_id)
    try:
        while True:
            message = q.get()
            yield f"data: {json.dumps(message)}\n\n"
    finally:
        notification_system.remove_listener(user_id, q)