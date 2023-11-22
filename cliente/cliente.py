import socket
import sys

if len(sys.argv) != 4:
    print("Uso: python cliente.py CONSULTA|ESCRITURA <USUARIO> <IP>")
    sys.exit(1)

request = sys.argv[1]
user = sys.argv[2]
host = sys.argv[3]
host_port = (host, 59004)

try:
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.settimeout(5)
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error as e:
    print(f"Error al crear socket: {e}")
    sys.exit(1)

try:
    match request:
        case "ESCRITURA":
            message = f"{request}".encode()
            udp.sendto(message, host_port)
            msg, (add, port) = udp.recvfrom(1024)
            port = int(msg.decode())
            tcp.connect((host, port))
            print("Solicitud de escritura de usuario aceptada")
            tcp.sendall(user.encode())

            response = tcp.recv(1024)
            print(f"El servidor ha confirmado la escritura de {response.decode()} caracteres")
            tcp.close()
            print("Cerrando socket TCP...")
        case "CONSULTA":
            message = f"{request}-{user}".encode()
            print(f"Consultando si existe el usuario {user}...")
            udp.sendto(message, host_port)
            msg, (add, port) = udp.recvfrom(1024)
            print(f"El usuario {user} {msg.decode()} existe en la base de datos")
        case _:
            print(f"Error, '{request}' no es una operacion valida")

finally:
    # Cerrar los sockets después de usarlos
    udp.close()
    tcp.close()
