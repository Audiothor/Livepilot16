# -*- coding: utf-8 -*-
"""
LivePilot 16 — Embedded Lightweight HTTP & WebSocket Server for Android Tablet Display
Compatible Python 3.7+ (Ableton Live 11 & Live 12)
Pure standard library: socket, threading, hashlib, base64, struct, json, os, mimetypes.
Zero external pip dependencies required.
"""

from __future__ import absolute_import, print_function, unicode_literals
import socket
import threading
import hashlib
import base64
import struct
import json
import os
import mimetypes
import time

WS_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

class LivePilotWebServer(object):
    """
    Serveur Web & WebSocket ultra-léger et autonome embarqué dans le Remote Script Ableton.
    Sert l'application Web HTML5/CSS/JS pour tablette Android
    et diffuse les données du Live Object Model en temps réel (WebSocket).
    """

    def __init__(self, host="0.0.0.0", port=8080, web_dir=None, on_client_message=None, logger=None):
        self.host = host
        self.port = port
        self.web_dir = web_dir or os.path.join(os.path.dirname(__file__), "web")
        self.on_client_message = on_client_message
        self.logger = logger or print
        
        self.clients = set()
        self.lock = threading.Lock()
        self.running = False
        self.server_sock = None
        self._server_thread = None

    def log(self, msg):
        try:
            self.logger("[LivePilot WebServer] " + str(msg))
        except Exception:
            pass

    def get_local_ips(self):
        """Retourne la liste des adresses IP locales de la machine pour guider l'utilisateur"""
        ips = []
        try:
            hostname = socket.gethostname()
            # Récupération via gethostbyname_ex
            _, _, host_ips = socket.gethostbyname_ex(hostname)
            for ip in host_ips:
                if not ip.startswith("127.") and ip not in ips:
                    ips.append(ip)
        except Exception:
            pass

        # Méthode alternative via socket UDP dummy pour trouver la route par défaut
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            def_ip = s.getsockname()[0]
            s.close()
            if def_ip and def_ip not in ips and not def_ip.startswith("127."):
                ips.insert(0, def_ip)
        except Exception:
            pass

        if not ips:
            ips.append("127.0.0.1")
        return ips

    def start(self):
        """Démarre le serveur dans un thread d'arrière-plan avec fallback de port si nécessaire"""
        if self.running:
            return True

        for p in [self.port, self.port + 1, self.port + 2, 8888, 9000]:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind((self.host, p))
                sock.listen(15)
                self.server_sock = sock
                self.port = p
                self.running = True
                break
            except Exception as e:
                self.log("Port {} indisponible ({}), tentative sur le suivant...".format(p, e))
                try:
                    sock.close()
                except Exception:
                    pass

        if not self.running or not self.server_sock:
            self.log("ERREUR CRITIQUE: Impossible d'ouvrir un socket serveur.")
            return False

        self._server_thread = threading.Thread(target=self._accept_loop)
        self._server_thread.daemon = True
        self._server_thread.start()

        ips = self.get_local_ips()
        self.log("Serveur Cockpit démarré sur le port {} !".format(self.port))
        for ip in ips:
            self.log("-> Accessible sur tablette à : http://{}:{}".format(ip, self.port))
        return True

    def stop(self):
        """Arrête proprement le serveur et déconnecte les clients"""
        self.running = False
        if self.server_sock:
            try:
                self.server_sock.close()
            except Exception:
                pass
            self.server_sock = None

        with self.lock:
            for c in list(self.clients):
                try:
                    c.close()
                except Exception:
                    pass
            self.clients.clear()
        self.log("Serveur arrêté.")

    def _accept_loop(self):
        while self.running:
            try:
                client_sock, addr = self.server_sock.accept()
                t = threading.Thread(target=self._handle_client, args=(client_sock, addr))
                t.daemon = True
                t.start()
            except Exception:
                if not self.running:
                    break

    def _handle_client(self, sock, addr):
        try:
            req = b""
            # Lecture des en-têtes HTTP
            while b"\r\n\r\n" not in req:
                chunk = sock.recv(1024)
                if not chunk:
                    sock.close()
                    return
                req += chunk
                if len(req) > 16384:
                    sock.close()
                    return

            headers_part = req.decode("utf-8", errors="ignore")
            lines = headers_part.split("\r\n")
            first_line = lines[0].split()
            if len(first_line) < 2:
                sock.close()
                return

            method, path = first_line[0], first_line[1]
            header_map = {}
            for line in lines[1:]:
                if ":" in line:
                    k, v = line.split(":", 1)
                    header_map[k.strip().lower()] = v.strip()

            if header_map.get("upgrade", "").lower() == "websocket":
                # Poignée de main WebSocket (RFC 6455)
                sec_key = header_map.get("sec-websocket-key")
                if not sec_key:
                    sock.close()
                    return
                accept_raw = hashlib.sha1((sec_key + WS_GUID).encode("utf-8")).digest()
                accept_key = base64.b64encode(accept_raw).decode("ascii")

                resp = (
                    "HTTP/1.1 101 Switching Protocols\r\n"
                    "Upgrade: websocket\r\n"
                    "Connection: Upgrade\r\n"
                    "Sec-WebSocket-Accept: {}\r\n\r\n"
                ).format(accept_key)
                sock.sendall(resp.encode("ascii"))

                with self.lock:
                    self.clients.add(sock)
                self.log("Client tablette connecte : {}:{}".format(addr[0], addr[1]))
                
                # Déclenche une synchronisation complète pour ce nouveau client
                if self.on_client_message:
                    try:
                        self.on_client_message({"action": "request_full_sync"})
                    except Exception:
                        pass

                self._ws_client_loop(sock)
            else:
                # Requête HTTP normale (fichiers statiques)
                self._serve_http_file(sock, path)
        except Exception:
            pass
        finally:
            with self.lock:
                self.clients.discard(sock)
            try:
                sock.close()
            except Exception:
                pass

    def _serve_http_file(self, sock, path):
        clean_path = path.split("?")[0].lstrip("/")
        if clean_path == "" or clean_path == "/":
            clean_path = "index.html"

        if not self.web_dir or not os.path.exists(self.web_dir):
            body = (
                "<!DOCTYPE html><html><head><meta charset='utf-8'><title>LivePilot Cockpit</title></head>"
                "<body style='background:#111;color:#fff;font-family:sans-serif;text-align:center;padding:50px;'>"
                "<h1>LivePilot Tablet Cockpit</h1><p>Dossier web en cours d'initialisation...</p>"
                "</body></html>"
            ).encode("utf-8")
            resp = "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nContent-Length: {}\r\n\r\n".format(len(body)).encode("ascii") + body
            sock.sendall(resp)
            return

        file_path = os.path.abspath(os.path.join(self.web_dir, clean_path))
        base_dir = os.path.abspath(self.web_dir)
        if not file_path.startswith(base_dir) or not os.path.exists(file_path) or os.path.isdir(file_path):
            resp = b"HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n"
            sock.sendall(resp)
            return

        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = "application/octet-stream"
        if file_path.endswith(".js"):
            mime_type = "application/javascript"
        elif file_path.endswith(".css"):
            mime_type = "text/css"
        elif file_path.endswith(".html"):
            mime_type = "text/html; charset=utf-8"
        elif file_path.endswith(".json") or file_path.endswith(".webmanifest"):
            mime_type = "application/json"
        elif file_path.endswith(".svg"):
            mime_type = "image/svg+xml"

        try:
            with open(file_path, "rb") as f:
                content = f.read()

            header = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: {}\r\n"
                "Content-Length: {}\r\n"
                "Access-Control-Allow-Origin: *\r\n"
                "Cache-Control: no-cache\r\n\r\n"
            ).format(mime_type, len(content))
            sock.sendall(header.encode("ascii") + content)
        except Exception:
            resp = b"HTTP/1.1 500 Internal Server Error\r\nContent-Length: 0\r\n\r\n"
            sock.sendall(resp)

    def _ws_client_loop(self, sock):
        while self.running:
            try:
                header = sock.recv(2)
                if not header or len(header) < 2:
                    break
                b1, b2 = header[0], header[1]
                opcode = b1 & 0x0F
                masked = (b2 & 0x80) != 0
                payload_len = b2 & 0x7F

                if opcode == 0x8:  # Close
                    break

                if payload_len == 126:
                    ext = sock.recv(2)
                    payload_len = struct.unpack("!H", ext)[0]
                elif payload_len == 127:
                    ext = sock.recv(8)
                    payload_len = struct.unpack("!Q", ext)[0]

                mask_key = sock.recv(4) if masked else None
                data = b""
                while len(data) < payload_len:
                    chunk = sock.recv(min(8192, payload_len - len(data)))
                    if not chunk:
                        break
                    data += chunk

                if masked and mask_key:
                    unmasked = bytearray(len(data))
                    for i in range(len(data)):
                        unmasked[i] = data[i] ^ mask_key[i % 4]
                    data = bytes(unmasked)

                if opcode == 0x1:  # Text JSON frame
                    text = data.decode("utf-8", errors="ignore")
                    if self.on_client_message:
                        try:
                            msg_dict = json.loads(text)
                            self.on_client_message(msg_dict)
                        except Exception as e:
                            self.log("Erreur parsing message client : {}".format(e))
                elif opcode == 0x9:  # Ping
                    sock.sendall(b"\x8a\x00")  # Pong
            except Exception:
                break

    def broadcast(self, data_obj):
        """Diffuse un dictionnaire JSON à tous les clients WebSocket connectés"""
        with self.lock:
            if not self.clients:
                return
            try:
                payload = json.dumps(data_obj).encode("utf-8")
                length = len(payload)
                if length < 126:
                    header = struct.pack("!BB", 0x81, length)
                elif length <= 0xFFFF:
                    header = struct.pack("!BBH", 0x81, 126, length)
                else:
                    header = struct.pack("!BBQ", 0x81, 127, length)
                frame = header + payload

                dead_socks = []
                for s in self.clients:
                    try:
                        s.sendall(frame)
                    except Exception:
                        dead_socks.append(s)

                for s in dead_socks:
                    self.clients.discard(s)
                    try:
                        s.close()
                    except Exception:
                        pass
            except Exception:
                pass
