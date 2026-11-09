import re

from rest_framework.views import exception_handler


_EXACT_TRANSLATIONS = {
    "This field is required.": "Trường này là bắt buộc.",
    "This field may not be blank.": "Trường này không được để trống.",
    "This field may not be null.": "Trường này không được để trống.",
    "A valid integer is required.": "Giá trị phải là số nguyên hợp lệ.",
    "A valid number is required.": "Giá trị phải là số hợp lệ.",
    "A valid date is required.": "Ngày không hợp lệ.",
    "A valid date/time is required.": "Thời điểm không hợp lệ.",
    "Enter a valid date/time.": "Vui lòng nhập ngày giờ hợp lệ.",
    "Enter a valid date.": "Vui lòng nhập ngày hợp lệ.",
    "Enter a valid time.": "Vui lòng nhập giờ hợp lệ.",
    "Not found.": "Không tìm thấy dữ liệu yêu cầu.",
    "Authentication credentials were not provided.": "Vui lòng đăng nhập để tiếp tục.",
    "You do not have permission to perform this action.": "Bạn không có quyền thực hiện thao tác này.",
    "A server error occurred.": "Đã xảy ra lỗi máy chủ. Vui lòng thử lại sau.",
}

_STATUS_MESSAGES = {
    400: "Dữ liệu gửi lên không hợp lệ.",
    401: "Vui lòng đăng nhập để tiếp tục.",
    403: "Bạn không có quyền thực hiện thao tác này.",
    404: "Không tìm thấy dữ liệu yêu cầu.",
    405: "Phương thức gửi yêu cầu không được hỗ trợ.",
    409: "Yêu cầu bị xung đột với dữ liệu hiện tại.",
    429: "Bạn đã gửi quá nhiều yêu cầu. Vui lòng thử lại sau.",
}


def _translate_message(message, status_code):
    text = str(message)
    if text in _EXACT_TRANSLATIONS:
        return _EXACT_TRANSLATIONS[text]

    match = re.fullmatch(r"Invalid pk \"(.+)\" - object does not exist\.", text)
    if match:
        return f"Không tìm thấy dữ liệu có mã {match.group(1)}."

    match = re.fullmatch(r"Method \"([A-Z]+)\" not allowed\.", text)
    if match:
        return f"Phương thức {match.group(1)} không được hỗ trợ."

    match = re.fullmatch(
        r"Ensure this value is greater than or equal to (.+)\.", text
    )
    if match:
        return f"Giá trị phải lớn hơn hoặc bằng {match.group(1)}."

    match = re.fullmatch(r"Ensure this value is less than or equal to (.+)\.", text)
    if match:
        return f"Giá trị phải nhỏ hơn hoặc bằng {match.group(1)}."

    match = re.fullmatch(r"Ensure this value is greater than (.+)\.", text)
    if match:
        return f"Giá trị phải lớn hơn {match.group(1)}."

    match = re.fullmatch(r"Ensure this value is less than (.+)\.", text)
    if match:
        return f"Giá trị phải nhỏ hơn {match.group(1)}."

    match = re.fullmatch(
        r"Ensure this field has no more than (\d+) characters\.", text
    )
    if match:
        return f"Trường này không được vượt quá {match.group(1)} ký tự."

    # Không trả các thông báo framework chưa được dịch bằng tiếng Anh cho client.
    if text.isascii() and any(character.isalpha() for character in text):
        return _STATUS_MESSAGES.get(status_code, "Đã xảy ra lỗi. Vui lòng thử lại.")
    return text


def _translate_data(value, status_code):
    if isinstance(value, dict):
        return {
            key: _translate_data(item, status_code)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_translate_data(item, status_code) for item in value]
    if isinstance(value, str):
        return _translate_message(value, status_code)
    return value


def vietnamese_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        response.data = _translate_data(response.data, response.status_code)
    return response
