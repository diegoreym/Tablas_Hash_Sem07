class Registro:
    
    def __init__(self, codigo: int, nombre: str) -> None:
        if not isinstance(codigo, int) or isinstance(codigo, bool):
            raise TypeError('El codigo debe ser un entero')
        if not isinstance(nombre, str):
            raise TypeError('El nombre debe ser una cadena')
        if codigo < 0:
            raise ValueError('El codigo no puede ser negativo')
        if nombre.strip() == '':
            raise ValueError('El nombre no puede estar vacio')
        self.codigo: int = codigo
        self.nombre: str = nombre.strip()
 
    def __repr__(self) -> str:
        return f'Registro(codigo={self.codigo}, nombre={self.nombre!r})' # !r sirve para mostrar el valor de la variable con comillas simples
 
    def __str__(self) -> str:
        return f'[{self.codigo}] {self.nombre}'
