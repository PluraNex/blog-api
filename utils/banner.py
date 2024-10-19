import os
from colorama import Fore, Style, init

# Inicializar colorama para garantir que funcione no Windows também
init(autoreset=True)

def print_banner(env):
    # Verificar se já imprimimos o banner
    if os.environ.get("DJANGO_ALREADY_STARTED") != "true":
        # Banner estilizado
        banner = """
        -------------------------------------------------
        |                                               |
        |          🚀 Welcome to Blog API 🚀            |
        |                                               |
        -------------------------------------------------
        """
        print(banner)
        
        # Configurações de cores e ícones para ambientes específicos
        color = Fore.CYAN if env == "development" else Fore.RED if env == "production" else Fore.YELLOW
        icon = "🛠️" if env == "development" else "🚀" if env == "production" else "🧪"

        # Informações formatadas
        print(f"{color}{icon}  Status: {Style.BRIGHT}Debug {'Active' if env == 'development' else 'Off'}")
        print(f"{color}{icon}  Server: {Style.BRIGHT}http://127.0.0.1:8000")
        print(f"{color}{icon}  Environment: {Style.BRIGHT}{env.capitalize()}")
        print(f"{color}{icon}  Settings: {Style.BRIGHT}project.settings.{env}")

        # Marcar que o banner já foi impresso
        os.environ["DJANGO_ALREADY_STARTED"] = "true"
