from rest_framework import viewsets, status
from rest_framework.response import Response

from .models import Item, UserKey
from .serializers import ItemSerializer, AuthorizedKeySerializer, UserKeySerializer
from .utils import add_authorized_key


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

class UserKeyManageSet(viewsets.ViewSet):
    def list(self, request):
        email = request.query_params.get("email")

        if email:
            key = UserKey.objects.filter(email=email).first()
            if not key:
                return Response(
                    {"status": "error", "message": "Key not found for this email"},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = UserKeySerializer(key)
            return Response(
                {
                    "status": "success",
                    "message": "User key found",
                    "key": serializer.data,
                },
                status=status.HTTP_200_OK
            )

        # If no email filter, return all keys
        keys = UserKey.objects.all()
        serializer = UserKeySerializer(keys, many=True)
        return Response(
            {
                "status": "success",
                "message": "All user keys",
                "keys": serializer.data,
            },
            status=status.HTTP_200_OK
        )

    def create(self, request):
        serializer = AuthorizedKeySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"]
        key = serializer.validated_data["key"]

        result = add_authorized_key(email, key)

        if "error" in result:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        return Response(result, status=status.HTTP_201_CREATED)

