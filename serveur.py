# =====================================================================================================================
# IMPORT
# =====================================================================================================================


import socket
# =====================================================================================================================
# CLASS
# =====================================================================================================================


class Server:
    """
    Class server
    """

    def __init__(self, machine_name, host, port, max_con):
        self.machine_name = machine_name
        self.HOST = host
        self.PORT = port
        self.MAX_CONNECTIONS = max_con
        self.MAIN_CONNECTION = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection_with_client = None
        self.client_info = None
        self.__repr__()

    def bind_server(self):
        """
        Methods that configures the server
        """
        self.MAIN_CONNECTION.bind((self.HOST, self.PORT))

    def listen_connections(self):
        """
        Methods that listens connections
        """
        self.MAIN_CONNECTION.listen(self.MAX_CONNECTIONS)

    def accept_connections(self):
        """
        Methods that accepts a new connection / gets a server-side chat channel
        """
        (connection_with_client, client_info) = self.MAIN_CONNECTION.accept()

        self.connection_with_client = connection_with_client
        self.client_info = client_info

    def encode(self, message):
        """
        Methods that encodes a message
        :return: message encoded
        """
        return message.encode()

    def send_message(self, message: str):
        """
        Methods that allows to send a message
        :param message: message
        :return mess: converted message, str
        """
        mess = "\n" + self.machine_name + " : " + message

        mess_to_send = self.encode(mess)
        self.connection_with_client.send(mess_to_send)

        return mess

    def get_message(self):
        """
        method that gets a message
        :return client_message_decoded: message decoded, str
        """
        client_message = self.connection_with_client.recv(1024)
        client_message_decoded = client_message.decode()

        if "quit" in client_message_decoded.lower():
            self.end()
        return client_message_decoded

    def end(self):
        """
        Method that ends the chat
        """
        self.MAIN_CONNECTION.close()
        self.connection_with_client.close()

    def __repr__(self):
        """
        Method that displays infos
        """
        infos = ["Affichage de l'IP machine ", socket.gethostbyname_ex(socket.gethostname())]

        for elt in infos:
            print(elt)


# =====================================================================================================================
# MAIN
# =====================================================================================================================


#server = Server("User_server", "...", 1030, 1)

#server.bind_server()  # binding connections
#server.listen_connections()  # listening connections
#server.accept_connections()  # getting a server-side chat channel