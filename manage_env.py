import os
import sys
from utils.banner import print_banner

if __name__ == "__main__":
    # Definir qual ambiente usar
    env = sys.argv[1] if len(sys.argv) > 1 else "development"
    
    # Garantir que o ambiente não seja um comando do Django
    if env in ["runserver", "migrate", "createsuperuser", "shell", "makemigrations"]:
        env = "development"
    else:
        sys.argv.pop(1)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"project.settings.{env}")

    # Log para confirmar o ambiente
    print_banner(env)

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Executar o comando do Django
    execute_from_command_line(sys.argv)
