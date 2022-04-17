# =====================================================================================================================
# IMPORT
# =====================================================================================================================


import socket
# =====================================================================================================================
# CLASS
# =====================================================================================================================


class Client:
    """
    Class server
    """

    def __init__(self, machine_name, host, port):
        self.machine_name = machine_name
        self.HOST = host
        self.PORT = port
        self.CONNECTION_WITH_SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_info = None
        self.__repr__()

    def connect_device(self):
        """
        Method that connects the client to the server
        """
        self.CONNECTION_WITH_SERVER.connect((self.HOST, self.PORT))

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
        self.CONNECTION_WITH_SERVER.send(mess_to_send)

        return mess

    def get_message(self):
        """
        method that gets a message
        :return client_message_decoded: message decoded, str
        """
        client_message = self.CONNECTION_WITH_SERVER.recv(1024)
        client_message_decoded = client_message.decode()

        if "quit" in client_message_decoded.lower():
            self.end()
        return client_message_decoded

    def end(self):
        """
        Method that ends the chat
        """
        self.CONNECTION_WITH_SERVER.close()

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


# server = Client("User_client", "...", 1030)
# server.connect_device()
