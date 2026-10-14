def es_primo(n: int) -> bool:
    # Devuelve True si n es un numero primo
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0:
        return False
    divisor = 3
    while divisor * divisor <= n:
        if n % divisor == 0:
            return False
        divisor += 2
    return True
 
 
def siguiente_primo(n: int) -> int:
    # Devuelve el menor primo mayor o igual que n
    candidato = max(n, 2)
    while not es_primo(candidato):
        candidato += 1
    return candidato
 
 
def capacidad_rehashing(m: int) -> int:
    # Nueva capacidad tras rehashing: siguiente primo >= 2m + 1
    return siguiente_primo(2 * m + 1)
