class RequestLogger:
    """Manages search execution logs for real-time tracking."""
    def __init__(self):
        self.logs = []
    
    def log(self, phase: str, message: str):
        """Records a log entry and prints it to the console."""
        log_entry = f"[{phase}] {message}"
        self.logs.append(log_entry)
        print(log_entry)
