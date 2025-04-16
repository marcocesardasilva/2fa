# from src.cliente import Cliente

# cliente = Cliente()
# cliente.abrir_menu_principal()

from src.gui import *

if __name__ == "__main__":
    app = InterfaceGrafica()
    app.root.mainloop()