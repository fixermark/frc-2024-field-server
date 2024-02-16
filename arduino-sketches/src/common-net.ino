/// Common-net.ino
///
/// Common network logic
///
/// == Serial protocol ==
/// - every message ends with \r\n
///
/// = init
/// - this client sends 'HRA' or 'HBA' depending on if it's red or blue alliance
/// - server responds with OK or NO
///   - on NO, light only top alliance light solid and park in error state; must reboot
///
/// = outbound to server
/// - A: alliance button pressed
/// - C: coopertition button pressed
/// - R: Ring sensor tripped
///
/// = inbound from server
/// - L0, L1: alliance low light off or on
/// - H0, H1, HB: alliance high light off, on, blink
/// - C0, C1, CB: coopertition high light off, on, blink

#include <Ethernet.h>

/// Remote connection configs

#define USE_ETHERNET 1  // if 1, use Ethernet; otherwise, use serial debugger

#define DEBUG_DROP_CONNECTION_PIN 3

const IPAddress field_server_ip(10,0,1,1);
const int server_port = 8008;

class TextBuffer {
private:
  size_t m_cursor;
  char m_buffer[80];
public:
  TextBuffer(): m_cursor(0) {}

  // Input a byte, inserting it into the buffer at the cursor and incrementing the cursor.
  // If the byte is -1, discard it.
  // If the byte is a newline, return the pointer to the buffer and reset the input cursor.
  // Otherwise, return nullptr.
  char* input(byte in) {
    // in addition to empty inputs, we discard Telnet control codes 0xfd and 0x18
    if (in == -1 || in == 0xfd || in == 0x18) {
      return nullptr;
    }
    m_buffer[m_cursor] = in;
    m_cursor++;
    if (in == '\n') {
      m_buffer[m_cursor] = '\0';
      m_cursor = 0;
      return m_buffer;
    } else {
      return nullptr;
    }
  }
};

#if USE_ETHERNET

class EthernetComms {
  private:
    TextBuffer m_buffer;
    EthernetClient m_client;
    IPAddress m_field_server_ip;
    int m_port;
    bool m_connected;

  public:
    EthernetComms(
      const byte* mac,
      const IPAddress& my_ip,
      const IPAddress& field_server_ip,
      const int port):
      m_buffer(), m_client(), m_field_server_ip(field_server_ip), m_port(port), m_connected(false) {
      Ethernet.begin((uint8_t*)mac, my_ip);
      }



    // Return true if connection successful, false otherwise
    bool connect() {
      return m_client.connect(m_field_server_ip, m_port);
    }

    char* input() {
      for (char c = m_client.read(); c != -1; c = m_client.read()) {
        char *buffer = m_buffer.input(c);
        if (buffer != nullptr) {
          return buffer;
        }
      }
      return nullptr;
    }

    void write(const char* out) {

      for (size_t cursor = 0; out[cursor] != '\0' && cursor < 80; ++cursor) {
        m_client.write(out[cursor]);
      }
      m_client.flush();
    }

    bool connected() {
      return m_client.connected();
    }
};

using Comms = EthernetComms;

#else // serial fake for Ethernet

class SerialComms {
private:
  TextBuffer m_buffer;

public:
  SerialComms(
    const byte* mac,
    const IPAddress& my_ip,
    const IPAddress& field_server_ip,
    const int port) {
      Serial.begin(9600);
      Serial.print("mac: ");
      for (size_t i = 0; i < 6; ++i) {
        Serial.print(mac[i], HEX);
        Serial.print(" ");
      }
      Serial.println("");
      Serial.print("my ip: ");
      Serial.println(my_ip);
  }

  ~SerialComms() {
    Serial.end();
  }

  // Connection protocol. Does nothing for SerialComms except return true for success.
  bool connect() {
    return true;
  }

  char* input() {
    for (char c = Serial.read(); c != -1; c = Serial.read()) {
      char *buffer = m_buffer.input(c);
      if (buffer != nullptr) {
        return buffer;
      }
    }
    return nullptr;
  }

  // Write out a null-terminated string to serial comms
  void write(const char* out) {
    for (size_t cursor = 0; out[cursor] != '\0' && cursor < 80; ++cursor) {
      Serial.write(out[cursor]);
    }
    Serial.flush();
  }

  bool connected() {
    // debugging: report serial comms disconnected if pin 3 is pulled high
    return !digitalRead(DEBUG_DROP_CONNECTION_PIN);
  }
};

using Comms = SerialComms;

# endif // select Ethernet or serial fake

void debug_msg(const char* msg) {
#if USE_ETHERNET
  Serial.println(msg);
#endif
}

Comms* g_comms = nullptr;

// Configure mac address based on the alliance string.
// On return, mac_address is populated with new address.
// NOTE: mac_address should be a 6-byte array.
//
// MAC val last byte is
// - RA: 0x03
// - RS: 0x02
// - BA: 0x01
// - BS: 0x00
void select_mac(const char* alliance_string, byte* mac_address) {
  byte mac_val = 0x00;

  if (alliance_string[0] == 'R') {
    mac_val += 0x02;
  }

  if (alliance_string[1] == 'A') {
    mac_val += 0x01;
  }

  mac_address[0] = 0x10;
  mac_address[1] = 0x10;
  mac_address[2] = 0x11;
  mac_address[3] = 0x11;
  mac_address[4] = 0x12;
  mac_address[5] = mac_val;
}

// Generate an IP address for this client based on alliance string.
//
// IP address last octet is
// - RA: 113
// - RS: 112
// - BA: 111
// - BS: 110
IPAddress select_client_ip(const char* alliance_string) {
  int last_octet = 110;

  if (alliance_string[0] == 'R') {
    last_octet += 2;
  }

  if (alliance_string[1] == 'A') {
    last_octet += 1;
  }

  return IPAddress(10,0,1,last_octet);
}

/// Connects to server via telnet
/// msg: the signal to send to the server, one of
/// - HBA\r\n: "Hello, blue amp"
/// - HRA\r\n: "Hello, red amp"
/// - HBS\r\n: "Hello, blue speaker"
/// - HRS\r\n: "Hello, red speaker"
void establishConnection(const char* msg) {

  byte mac[6];

  select_mac(msg, mac);
  auto my_ip = select_client_ip(msg);

  while (true) {  // try forever; once connection is established, we return out of here
    if (g_comms) {
      delete g_comms;
    }

    g_comms = new Comms(mac, my_ip, field_server_ip, server_port);
    if (!g_comms->connect()) {
      debug_msg("Unable to connect; retrying.");
      continue;
    }
    g_comms->write(msg);

    char* input = g_comms->input();
    // Wait for response from server
    for (; input == nullptr; input=g_comms->input()) {
      debug_msg("Awaiting input...");
      delay(500);
    }
    if (input[0] == 'O' && input[1] == 'K') {
      debug_msg("Connected!");
      return;
    }
  }
}
