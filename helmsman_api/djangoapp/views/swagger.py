import json
import yaml
from django.shortcuts import render
from django.conf import settings
from rest_framework.decorators import api_view, authentication_classes


@api_view(['GET'])
@authentication_classes([])
def swagger(request):
    file = open(settings.SWAGGER_YAML_FILE)
    spec = yaml.safe_load(file.read())
    return render(request, template_name="swagger_base.html", context={'data': json.dumps(spec)})