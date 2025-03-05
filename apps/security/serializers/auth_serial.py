from rest_framework import serializers
from django.contrib.auth import authenticate, password_validation
from django.utils.translation import gettext_lazy as _
from apps.security.models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer para el registro de nuevos usuarios.
    Incluye validaciones para contraseña y confirmación.
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        validators=[password_validation.validate_password]
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'confirm_password', 
                  'first_name', 'last_name', 'phone', 'avatar', 'bio']
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': False},
            'last_name': {'required': False},
            'id': {'read_only': True}
        }

    def validate_email(self, value):
        """Valida que el email no esté ya registrado."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(_("Este correo electrónico ya está en uso."))
        return value

    def validate_username(self, value):
        """Valida que el nombre de usuario no esté ya registrado."""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(_("Este nombre de usuario ya está en uso."))
        return value

    def validate(self, data):
        """Valida que la contraseña y la confirmación coincidan."""
        if data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError({
                'confirm_password': _("Las contraseñas no coinciden.")
            })
        return data

    def create(self, validated_data):
        """Crea un nuevo usuario con los datos validados."""
        # Eliminar campo de confirmación de contraseña
        validated_data.pop('confirm_password')
        
        # Crear usuario con create_user para encriptar contraseña
        user = User.objects.create_user(
            username=validated_data.get('username'),
            email=validated_data.get('email'),
            password=validated_data.get('password'),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone=validated_data.get('phone', None),
            avatar=validated_data.get('avatar', None),
            bio=validated_data.get('bio', None)
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer para la autenticación de usuarios.
    Permite iniciar sesión con nombre de usuario o correo electrónico.
    """
    login = serializers.CharField(required=True, write_only=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, data):
        """
        Valida las credenciales del usuario y devuelve el usuario autenticado.
        Acepta login como username o email.
        """
        login = data.get('login')
        password = data.get('password')

        if not login or not password:
            raise serializers.ValidationError(_("Debe proporcionar credenciales de inicio de sesión."))

        # Determinar si el login es un email o username
        if '@' in login:
            try:
                user = User.objects.get(email=login)
                username = user.username
            except User.DoesNotExist:
                raise serializers.ValidationError(_("No existe un usuario con ese correo electrónico."))
        else:
            username = login

        # Autenticar usuario
        user = authenticate(username=username, password=password)
        
        if not user:
            raise serializers.ValidationError(_("Credenciales incorrectas. Por favor, inténtelo de nuevo."))
        
        if not user.is_active:
            raise serializers.ValidationError(_("Esta cuenta ha sido desactivada."))
            
        # Guardar el usuario en los datos validados
        data['user'] = user
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer para obtener y actualizar el perfil de usuario.
    """
    full_name = serializers.SerializerMethodField()
    session_stats = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'phone', 'avatar', 'bio', 'preferred_countdown', 'preferred_interval',
            'date_joined', 'session_stats'
        ]
        read_only_fields = ['id', 'date_joined', 'email', 'session_stats']

    def get_full_name(self, obj):
        """Obtiene el nombre completo del usuario."""
        return obj.get_full_name()
    
    def get_session_stats(self, obj):
        """Obtiene las estadísticas de sesiones del usuario."""
        return obj.get_session_statistics()