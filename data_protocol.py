from PIL import ImageGrab
import socket
import cv2
import numpy as np
import struct
import time

from RadarExtractor import RadarExtractor

def get_screen():
    screenshot = ImageGrab.grab(all_screens=True)
    screen = np.array(screenshot)
    
    # escolha a configuracao do monitor
    # frame = screen[:2160, :3840, ::-1] # tela principal
    # frame = screen[2160:, :1920, ::-1] # tela inferior esquerda
    # frame = screen[2160:, 1927:, ::-1] # tela inferior direita
    # frame = screen[:, 1920:, ::-1] # pc pessoal
    frame = screen[:, :1920, ::-1] # pc pessoal

    if (frame.shape[0] != 1080 and frame.shape[1] != 1920) and (not get_screen.first_time):
        print(f"[ATENÇÃO] Altura: {frame.shape[0]} (recom. 1080), Comprimento: {frame.shape[1]} (recom. 1920)")
        get_screen.first_time = False

    return frame

get_screen.first_time = True

radar_radius = 488
radar_center = (806, 539)
shape = (1080, 1920)
radarext = RadarExtractor(radar_radius, radar_center, shape)

def sender(conn: socket.socket):
    frame = get_screen()
    # frame, radar_img = radarext.radar_from_tpn_recording(frame)

    buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 95])[1]

    size = len(buffer)

    header = struct.pack('!id', size, time.time()) # TESTAR ESSE PRIMEIRO
    # header = (str(size).ljust(10) + str(time.time()).ljust(18)).encode("utf-8") # SE O DE CIMA NAO FUNCIONAR

    conn.sendall(header)
    conn.sendall(buffer)

def receiver(conn: socket.socket):
    header = conn.recv(12) # TESTAR ESSE PRIMEIRO
    # header = conn.recv(28) # SE O DE CIMA NAO FUNCIONAR

    size, img_time = struct.unpack('!id', header) # TESTAR ESSE PRIMEIRO
    ### SE O DE CIMA NAO FUNCIONAR ###
    # header = header.decode("utf-8")
    # print(header)
    # size = int(header[:10])
    # img_time = float(header[10:])
    # print(size, img_time)
    ###

    received = 0
    buffer = bytes()
    while received < size:
        incoming = conn.recv(1024 if ((size - received)//1024 != 0) else (size - received))
        buffer = b''.join([buffer, incoming])
        received = len(buffer)

    frame = cv2.imdecode(np.frombuffer(buffer, dtype=np.uint8), cv2.IMREAD_COLOR)

    return frame, img_time