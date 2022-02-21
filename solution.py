from socket import *

# import ssl
# second submission

def smtp_client(mailPort=1025, mailServer="127.0.0.1"):
    YOUR_EMAIL = "ejmontero83@gmail.com"
    YOUR_DESTINATION_EMAIL = "ejmontero83@gmail.com"
    YOUR_SUBJECT_EMAIL = "just a test for smtp"
    YOUR_BODY_EMAIL = "worked"
    msg = "{}. \r\ncyber security Rocks!".format(YOUR_BODY_EMAIL)
    endmsg = "\r\n.\r\n"
    # Choose a mail server (e.g. Google mail server) and call it mailserver
    # mailServer = "smtp.google.com"  #
    # mailPort = 587
    # Create socket called clientSocket and establish a TCP connection with mailserver
    # Fill in start

    # clientSocket = ssl.wrap_socket(socket(AF_INET, SOCK_STREAM))
    clientSocket = socket(AF_INET, SOCK_STREAM)

    clientSocket.connect((mailServer, mailPort))
    # Fill in end
    recv = clientSocket.recv(1024).decode()
    # print(recv)
    # if recv[:3] != "220":
    #     print("220 reply not received from server.")
    # Send HELO command and print server response.
    heloCommand = "HELO Anonymous\r\n".encode()
    clientSocket.send(heloCommand)
    recv1 = clientSocket.recv(1024).decode()
    # print(recv1)
    # if recv1[:3] != "250":
    #     print("250 reply not received from server.")

    # Fill in start

    # Fill in end
    # Send MAIL FROM command and print server response.
    # Fill in start
    mailfrom = "MAIL FROM: <{}>\r\n".format(YOUR_EMAIL)
    clientSocket.send(mailfrom.encode())
    recv5 = clientSocket.recv(1024).decode()
    # print(recv5)
    # Fill in end
    # Send RCPT TO command and print server response.
    # Fill in start
    rcptto = "RCPT TO: <{}>\r\n".format(YOUR_DESTINATION_EMAIL)
    clientSocket.send(rcptto.encode())
    recv6 = clientSocket.recv(1024).decode()
    # Fill in end
    # Send DATA command and print server response.

    data = "DATA\r\n"
    clientSocket.send(data.encode())
    recv7 = clientSocket.recv(1024).decode()
    # print(recv7)
    # Fill in end
    # Send message data.
    # Fill in start
    clientSocket.send("Subject: {}\n\n{}".format(YOUR_SUBJECT_EMAIL, msg).encode())
    # Fill in end
    # Message ends with a single period.
    # Fill in start
    clientSocket.send(endmsg.encode())
    recv8 = clientSocket.recv(1024).decode()
    # print(recv8)
    # Fill in end
    # Send QUIT command and get server response.
    # Fill in start
    quitcommand = "QUIT\r\n"
    clientSocket.send(quitcommand.encode())
    recv9 = clientSocket.recv(1024).decode()
    # print(recv9)
    clientSocket.close()
    # print("Was successful!")
    # Fill in end

