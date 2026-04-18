# EmailTokenObtainPairView

- Route: /api/token/
- View: EmailTokenObtainPairView

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

### POST
- Login JWT: `POST /api/token/`
- Payload:
```json
{
  "email": "admin@empresa.com",
  "password": "SuaSenha"
}
```
- Retorno: `access`, `refresh` e objeto `user` enriquecido com preferencias.

