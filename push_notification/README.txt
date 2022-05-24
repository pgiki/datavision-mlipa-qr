#registering Device

curl -X PATCH http://127.0.0.1:8000/push_notification/api/v1/fcm/devices/123/ -H "Content-Type:application/json" -d '{"name": "demo", "username": "demo", "registration_id": "123", "device_id": "123", "active": true, "type": "android", "app": "mlipa", "accessToken": "mlipa"}'
