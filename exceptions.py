class DomainToIPError(Exception):
    """도메인에서 IP 주소를 찾지 못했을 때 발생하는 에러."""
    
    def __init__(self, message="도메인에서 IP 주소를 찾지 못했습니다.", status_code=500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message} (상태 코드: {self.status_code})"