# Copyright (c) 2026, redtch and contributors
# For license information, please see license.txt


def get_notification_config():
	return {
		"for_doctype": {
			"Law Case": {"status": ["not in", ["منتهية"]]},
			"Case Hearing": {"hearing_status": "مجدولة"},
			"Power of Attorney": {"is_active": 1},
		}
	}
