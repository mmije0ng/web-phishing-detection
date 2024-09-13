class ErrorResponseDTO:
    def __init__(self, status, message):
        self.status = status
        self.message = message

    def to_dict(self):
        return {
            "status": self.status,
            "message": self.message
        }
