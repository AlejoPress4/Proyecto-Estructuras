
from models.gui import main

if __name__ == "__main__":
    """
    Punto de entrada principal de la aplicación.

    Este bloque de código se ejecuta cuando el archivo se ejecuta directamente.
    Importa y llama a la función `main` desde el módulo `models.gui`.

    Pasos:
    1. Importa la función `main` desde `models.gui`.
    2. Verifica si el archivo se está ejecutando como un script principal.
    3. Llama a la función `main` para iniciar la aplicación.

    Función `main`:
    - La función `main` inicializa la aplicación Qt, crea la ventana principal y ejecuta el bucle de eventos.
    """
    main()
