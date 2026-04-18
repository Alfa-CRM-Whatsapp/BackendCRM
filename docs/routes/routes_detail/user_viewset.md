# UserViewSet

- Route: /api/users/
- View: UserViewSet

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
- Lista: `GET /api/users/`
- Detalhe: `GET /api/users/{id}/`

### POST
- Criacao: `POST /api/users/`
- Payload:
```json
{
  "email": "novo@empresa.com",
  "password": "SenhaForte123"
}
```

### PUT
- Atualizacao Completa: `PUT /api/users/{id}/`
- Payload: Mesmo formato da representacao do usuario listada pela API.

### PATCH
- Atualizacao Parcial: `PATCH /api/users/{id}/`
- Payload: Campos parciais do usuario.

### DELETE
- Remocao: `DELETE /api/users/{id}/`

