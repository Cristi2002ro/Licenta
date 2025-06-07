import os
from datetime import datetime, timedelta


class SessionManager:
    def __init__(self, ttl_hours=24):
        self.sessions = {}
        self.ttl = timedelta(hours=ttl_hours)
    
    def get_session(self, session_id):
        if session_id in self.sessions:
            session = self.sessions[session_id]
            if datetime.now() - session["last_access"] < self.ttl:
                session["last_access"] = datetime.now()
                return session
            else:
                self.cleanup_session(session_id)
        return None
    
    def create_session(self, session_id, context, thread_id):
        self.sessions[session_id] = {
            "last_access": datetime.now(),
            "context": context,
            "thread_id": thread_id,
            "version": 1
        }
    
    def cleanup_session(self, session_id):
        if session_id in self.sessions:
            session_dir = os.path.join("knowledge_base", session_id)
            if os.path.exists(session_dir):
                for file in os.listdir(session_dir):
                    os.remove(os.path.join(session_dir, file))
                os.rmdir(session_dir)
            del self.sessions[session_id]
    
    def cleanup_expired(self):
        current_time = datetime.now()
        expired = [sid for sid, data in self.sessions.items() 
                  if current_time - data["last_access"] > self.ttl]
        for session_id in expired:
            self.cleanup_session(session_id)

    def clear_session_files(self, session_id):
        """Clear all files for a session without removing the session itself"""
        session_dir = os.path.join("knowledge_base", session_id)
        if os.path.exists(session_dir):
            for file in os.listdir(session_dir):
                os.remove(os.path.join(session_dir, file))

session_manager = SessionManager()
