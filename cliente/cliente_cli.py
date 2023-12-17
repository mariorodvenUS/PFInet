import typer
from rich.progress import track
import time
import socket
import sys
app = typer.Typer()

host_port = 59004


@app.command()
def consulta(name:str, ip:str):
    udp, tcp = create_sockets()
    message = f"CONSULTA-{name}".encode()
    print(f"Consultando si existe el usuario {name}...")
    udp.sendto(message, (ip,host_port))
    msg, (add, port) = udp.recvfrom(1024)
    print(f"El usuario {name} {msg.decode()} existe en la base de datos")
    return msg.decode()

@app.command()
def escritura(name:str,ip:str):
    if consulta(name, ip) == 'NO':
        print("El usuario no existe en la base de datos")
        udp, tcp = create_sockets()
        message = "ESCRITURA".encode()
        for _ in range(5):  # Realizar el envío y recepción hasta 5 veces
            udp.sendto(message, (ip,host_port))
            try:
                msg, (addr, port) = udp.recvfrom(1024)
                break  # Si se recibe la respuesta, salir del bucle
            except socket.timeout:
                print("Timeout (5 seg): servidor no responde...\nreintentando")
        else:
            # Si el bucle se ejecuta completamente sin salir, es decir, después de 5 intentos sin éxito
            print("Error: No se pudo establecer la conexión después de 5 intentos.")
            sys.exit()
        port = int(msg.decode())
        tcp.connect((ip, port))
        progress_bar()
        print("Solicitud de escritura de usuario aceptada")
        tcp.sendall(name.encode())

        response = tcp.recv(1024)
        print(f"El servidor ha confirmado la escritura de {response.decode()} caracteres")
        tcp.close()
        print("Cerrando socket TCP...")
    elif consulta(name, ip) == 'SI':
        print("El usuario ya existe en la base de datos")
        sys.exit()
        

def progress_bar():
    for value in track(range(100), description="Processing..."):
        # Fake processing time
        time.sleep(0.01)

def create_sockets():
    try:
        udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp.settimeout(5)
        tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        return (udp, tcp)
    except socket.error as e:
        print(f"Error al crear socket: {e}")
        sys.exit(1)


if __name__ == "__main__":
    app()