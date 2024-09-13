# (확장용) 분석 결과 응답 DTO 클래스
class SimpleResponseDTO:
    def __init__(self, url, prediction_result, prediction_prob):
        self.url = url
        self.prediction_result = int(prediction_result)  # 피싱 여부
        self.prediction_prob = f"{prediction_prob}%"  # 피싱 확률

    def to_dict(self):
        return {
            "url": self.url,
            "prediction_result": self.prediction_result,
            "prediction_prob": self.prediction_prob,
        }

# (웹용) 상세 분석 결과 응답 DTO 클래스
class DetailedResponseDTO:
    def __init__(self, url, prediction_result, prediction_prob, suspicious_features, ip_info):
        self.url = url
        self.prediction_result = int(prediction_result)  # 피싱 여부
        self.prediction_prob = f"{prediction_prob}%"  # 피싱 확률
        self.ip_address = ip_info["ip_address"]
        self.country = ip_info["country"]
        self.region = ip_info["region"]
        self.is_vpn = ip_info["is_vpn"]
        self.isp_name = ip_info["isp_name"]
        self.suspicious_features = suspicious_features

    def to_dict(self):
        return {
            "url": self.url,
            "prediction_result": self.prediction_result,
            "prediction_prob": self.prediction_prob,
            "ip_address": self.ip_address,
            "country": self.country,
            "region": self.region,
            "is_vpn": self.is_vpn,
            "isp_name": self.isp_name,
            "url_based_feature_list": self.suspicious_features["url_based_features"],
            "content_based_feature_list": self.suspicious_features["content_based_features"],
            "domain_based_feature_list": self.suspicious_features["domain_based_features"]
        }
