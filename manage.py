import os
import sys
from utils.banner import print_banner

def get_env_from_args():
    for arg in sys.argv:
        if arg == "--env=production":
            sys.argv.remove(arg)
            return "production"
    return "development"

if __name__ == "__main__":
    env = get_env_from_args()

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"blog.settings.{env}")

    if "runserver" in sys.argv:
        print_banner(env)

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    execute_from_command_line(sys.argv)
