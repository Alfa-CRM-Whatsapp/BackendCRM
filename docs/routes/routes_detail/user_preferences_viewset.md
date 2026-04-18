# UserPreferencesViewSet

- Route: /api/user-preferences/
- View: UserPreferencesViewSet

## Codigo Da View

Fonte: src\core\authentication\views\user.py

```python
from rest_framework_simplejwt.views import TokenObtainPairView
from core.authentication.serializers import EmailTokenObtainPairSerializer, UserListSerializer, UserCreateSerializer, UserPreferencesSerializer
from rest_framework import viewsets

class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = UserListSerializer.Meta.model.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return UserListSerializer
        elif self.action == 'create':
            return UserCreateSerializer
        return UserListSerializer
    
class UserPreferencesViewSet(viewsets.ModelViewSet):
    queryset = UserPreferencesSerializer.Meta.model.objects.all()
    serializer_class = UserPreferencesSerializer
```

## Metodos Aceitos

### GET
- Lista: `GET /api/user-preferences/`
- Detalhe: `GET /api/user-preferences/{id}/`

### POST
- Criacao: `POST /api/user-preferences/`
- Payload:
```json
{
  "user": 1,
  "theme": "light",
  "primary_color": "#1E3A5F"
}
```

### PUT
- Atualizacao Completa: `PUT /api/user-preferences/{id}/`

### PATCH
- Atualizacao Parcial: `PATCH /api/user-preferences/{id}/`
- Exemplo:
```json
{
  "theme": "dark"
}
```

### DELETE
- Remocao: `DELETE /api/user-preferences/{id}/`

