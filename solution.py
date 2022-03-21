from socket import *
import os
import sys
import struct
import time
import select
import binascii

ICMP_ECHO_REQUEST = 8
MAX_HOPS = 30
TIMEOUT = 2.0
TRIES = 3
# The packet that we shall send to each router along the path is the ICMP echo
# request packet, which is exactly what we had used in the ICMP ping exercise.
# We shall use the same packet that we built in the Ping exercise


def checksum(string):
    # In this function we make the checksum of our packet
    csum = 0
    countTo = (len(string) // 2) * 2
    count = 0

    while count < countTo:
        thisVal = (string[count + 1]) * 256 + (string[count])
        csum += thisVal
        csum &= 0xFFFFFFFF
        count += 2

    if countTo < len(string):
        csum += string[len(string) - 1]
        csum &= 0xFFFFFFFF

    csum = (csum >> 16) + (csum & 0xFFFF)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xFFFF
    answer = answer >> 8 | (answer << 8 & 0xFF00)
    return answer


def build_packet():
    myChecksum = 0
    ID = os.getpid() & 0xFFFF  # Return the current process i
    # Make a dummy header with a 0 checksum
    # struct -- Interpret strings as packed binary data
    data = b"\x50\x49\x4E\x47\x2D\x50\x4F\x4E\x47\x20\x46\x52\x4F\x4D"
    data_len = len(data)

    header = struct.pack(
        "BBHHHQ{}s".format(data_len),
        ICMP_ECHO_REQUEST,
        0,
        myChecksum,
        ID,
        1,
        int(time.time()),
        data,
    )

    # Calculate the checksum on the data and the dummy header.
    myChecksum = checksum(header)

    # Get the right checksum, and put in the header

    if sys.platform == "darwin":
        # Convert 16-bit integers from host to network  byte order
        myChecksum = htons(myChecksum) & 0xFFFF
    else:
        myChecksum = htons(myChecksum)

    packet = struct.pack(
        "BBHHHQ{}s".format(data_len),
        ICMP_ECHO_REQUEST,
        0,
        myChecksum,
        ID,
        1,
        int(time.time()),
        data,
    )
    return packet


def get_route(hostname):
    timeLeft = TIMEOUT
    tracelist1 = []  # This is your list to use when iterating through each trace
    tracelist2 = []  # This is your list to contain all traces

    for ttl in range(1, MAX_HOPS):
        for tries in range(TRIES):
            destAddr = gethostbyname(hostname)
            # Fill in start
            icmp = getprotobyname("icmp")

            mySocket = socket(AF_INET, SOCK_RAW, icmp)

            # Fill in end
            mySocket.setsockopt(IPPROTO_IP, IP_TTL, struct.pack("I", ttl))
            mySocket.settimeout(TIMEOUT)
            try:
                d = build_packet()
                mySocket.sendto(build_packet(), (destAddr, 1))
                # t= time.time()
                startedSelect = time.time()
                can_read, can_write, _ = select.select([mySocket], [], [], timeLeft)
                howLongInSelect = time.time() - startedSelect
                if can_read == []:  # Timeout
                    print(f"{ttl} * * Request timed out.")

                    tracelist1.append([f"{ttl} * * Request timed out."])
                    continue

                # Fill in start
                # You should add the list above to your all traces list
                # Fill in end
                recvPacket, addr = mySocket.recvfrom(1024)

                timeReceived = time.time()
                timeLeft = timeLeft - howLongInSelect
                if timeLeft <= 0:
                   # print(f"{ttl} * * Request timed out.")
                    tracelist1.append([f"{ttl} * * Request timed out."])
                    # Fill in start
                    # You should add the list above to your all traces list
                    # Fill in end
            except timeout:
               # print("timeout")
                continue

            else:
                # Fill in start

                names = [
                    "version",
                    "type",
                    "length",
                    "id",
                    "flags",
                    "ttl",
                    "protocol",
                    "checksum",
                    "src_ip",
                    "dest_ip",
                ]
                ip_header = dict(
                    zip(names, struct.unpack("!BBHHHBBHII", recvPacket[:20]))
                )
                # Fill in end
                try:  # try to fetch the hostname
                    addr = addr[0]
                    curr_name = gethostbyaddr(addr)[0]
                except herror:  # if the host does not provide a hostname
                    curr_name = "hostname not returnable"
                types = ip_header["type"]
                howLongInSelect *= 1000  # convert to ms
                if types == 11:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28 : 28 + bytes])[0]
                    # Fill in start
                    # You should add your responses to your lists
                    #print(f"{ttl} {howLongInSelect} {addr} Request timed out.")
                    tracelist1.append(
                        [f"{ttl} {howLongInSelect} {addr} Request timed out."]
                    )

                    # Fill in end
                elif types == 3:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28 : 28 + bytes])[0]
                    # Fill in start
                    # You should add your responses to your lists
                   # print(f"{ttl} {howLongInSelect} {addr} Destination Unreachable")
                    tracelist1.append(
                        [f"{ttl} {howLongInSelect} {addr} Destination Unreachable"]
                    )

                    #
                    # Fill in end
                elif types == 0:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28 : 28 + bytes])[0]
                    # Fill intracelist1 start
                    # You should add your responses to your lists
                   # print(f"{ttl} {howLongInSelect} {addr} {curr_name}")

                    tracelist1.append([f"{ttl} {howLongInSelect} {addr} {curr_name}"])

                    if addr == destAddr:
                        return tracelist1
                    #  and return your list if your destination IP is met
                    # Fill in end
                else:
                    # Fill in start
                    # If there is an exception/error to your if statements, you should append that to your list here
                   # print(f"{ttl} {howLongInSelect} {addr} {curr_name}")
                    tracelist1.append([f"{ttl} {howLongInSelect} {addr} {curr_name}"])

                    # Fill in end
            finally:
                mySocket.close()
            break


