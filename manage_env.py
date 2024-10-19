import os
import sys
from utils.banner import print_banner

def get_env_from_args():
    # Verifique se existe um argumento --env=development ou --env=production
    for arg in sys.argv:
        if arg.startswith("--env="):
            _, env = arg.split("=")
            sys.argv.remove(arg)  # Remove o argumento para evitar conflitos com o Django
            return env
    return "development"  # Padrão para desenvolvimento

if __name__ == "__main__":
    # Definir o ambiente usando a nova função
    env = get_env_from_args()

    # Definir a variável de ambiente do Django
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
