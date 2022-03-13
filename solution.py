
from calendar import c
from socket import *
import os
import sys
import struct
import time
import select
import binascii
import statistics

# Should use stdev

ICMP_ECHO_REQUEST = 8


def checksum(string):
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


def receiveOnePing(mySocket, ID, timeout, destAddr):
    send_timestamp = time.time()
    while 1:

        timeReceived = time.time()
        data = (
            b"\x50\x49\x4E\x47\x2D\x50\x4F\x4E\x47\x20\x46\x52\x4F\x4D"
            b"\x50\x49\x4E\x47\x2D\x50\x4F\x4E\x47\x20\x46\x52\x4F\x4D"
        )
        buffer_size = (
                60 + 8 + struct.calcsize("Q") + len(data)
        )  # calcsize('Q'): timestamp size
        try:
            recPacket, addr = mySocket.recvfrom(buffer_size)
        except Exception as s:
            #print(s)
            return

        recv_timestamp = time.time()

        vihl = struct.unpack("B", recPacket[:1])[
            0
        ]  # First byte consists of 4 bit IP Version and 4 bit IHL
        ihl = (
                      (vihl << 4) & 0xFF
              ) >> 4  # Cut out the IHL (Internet Header Length) value
        iphdr_len = 4 * ihl  # and recalculate IP header length

        # Actual IP packet size of the recPacket
        icmphdr_len = 8
        packet_size = iphdr_len + icmphdr_len + struct.calcsize("Q") + len(data)
        in_packet = struct.unpack(
            "BBHHH", recPacket[iphdr_len: iphdr_len + icmphdr_len]
        )
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
        ip_header = dict(zip(names, struct.unpack("!BBHHHBBHII", recPacket[:20])))
        # This is Echo Reply (icmp_type_reply in in_packet[0])
        # to our Echo Request with ID (in_packet[3]) and sequence number (in_packet[4])
        # print(
        #     "{size} bytes from {host}: ttl={ttl} time={time:0.4f} ms".format(
        #         size=packet_size,
        #         host=destAddr,
        #         seq=in_packet[4],
        #         ttl=ip_header["ttl"],
        #         time=(recv_timestamp - send_timestamp) * 1000,
        #     )
        # )
        return (recv_timestamp - send_timestamp) * 1000
        # Fetch the ICMP header from the IP packet


def sendOnePing(mySocket, destAddr, ID):
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)

    myChecksum = 0
    # Make a dummy header with a 0 checksum
    # struct -- Interpret strings as packed binary data
    data = (
        b"\x50\x49\x4E\x47\x2D\x50\x4F\x4E\x47\x20\x46\x52\x4F\x4D"

    )
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
    mySocket.sendto(packet, (destAddr, 1))  # AF_INET address must be tuple, not str

    # Both LISTS and TUPLES consist of a number of objects
    # which can be referenced by their position number within the object.


def doOnePing(destAddr, timeout):
    icmp = getprotobyname("icmp")

    # SOCK_RAW is a powerful socket type. For more details:   http://sockraw.org/papers/sock_raw
    mySocket = socket(AF_INET, SOCK_RAW, icmp)
    mySocket.settimeout(2)

    myID = os.getpid() & 0xFFFF  # Return the current process i
    sendOnePing(mySocket, destAddr, myID)
    delay = receiveOnePing(mySocket, myID, timeout, destAddr)
    mySocket.close()
    return delay


def ping(host, timeout=2):
    # timeout=1 means: If one second goes by without a reply from the server,  	# the client assumes that either the client's ping or the server's pong is lost
    try:
        dest = gethostbyname(host)
    except Exception:
        return ["0", "0.0", "0", "0.0"]
    #print("Pinging " + dest + " using Python:")
    rtt = []
    # Calculate vars values and return them
    # Send ping requests to a server separated by approximately one second
    for i in range(0, 4):
        delay = doOnePing(dest, timeout)
        rtt.append(delay)
        time.sleep(1)  # one second

    packet_min = min(rtt)
    packet_max = max(rtt)
    stdev_var = statistics.stdev(rtt)

    packet_avg = sum(rtt, 0.0) / len(rtt)
    vars = [
        str(round(packet_min, 2)),
        str(round(packet_avg, 2)),
        str(round(packet_max, 2)),
        str(round(stdev_var, 2)),
    ]

    return vars



