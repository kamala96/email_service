from rest_framework import serializers


class EmailSerializer(serializers.Serializer):
    subject = serializers.CharField(max_length=255)
    message = serializers.CharField(required=False, allow_null=True)
    recipient = serializers.EmailField()
    attachments = serializers.ListField(
        child=serializers.FileField(max_length=100000), required=False, allow_null=True
    )
    html_message = serializers.CharField(required=False, allow_null=True)

    def validate(self, data):
        message = data.get('message')
        html_message = data.get('html_message')
        if not message and not html_message:
            raise serializers.ValidationError(
                "Either 'message' or 'html_message' must be provided.")
        return data


class BulkEmailSerializer(serializers.Serializer):
    subject = serializers.CharField(max_length=255)
    message = serializers.CharField(required=False, allow_null=True)
    recipient_list = serializers.ListField(
        child=serializers.EmailField()
    )
    attachments = serializers.ListField(
        child=serializers.FileField(max_length=100000), required=False, allow_null=True
    )
    html_message = serializers.CharField(required=False, allow_null=True)
    collective = serializers.BooleanField(
        required=False, allow_null=True, default=False)

    def validate(self, data):
        message = data.get('message')
        html_message = data.get('html_message')
        if not message and not html_message:
            raise serializers.ValidationError(
                "Either 'message' or 'html_message' must be provided.")
        return data
