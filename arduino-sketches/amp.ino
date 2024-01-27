/// Amp.ino
///
/// Logic for controlling an Amp's lights, buttons, and IR sensor
///
/// From the FRC 2024 manual:
/// -bottom light on: the ALLIANCE has 1 NOTE towards AMPLIFICATION (or Coopertition)
/// − both lights on: the ALLIANCE has 2 NOTES toward AMPLIFICATION (1 of which can be used for
/// Coopertition)
/// − top light blinking at 2Hz: the SPEAKER is AMPLIFIED
///
/// The Coopertition light behavior and meaning are as follows:
/// − blinking at 1 Hz: it’s AUTO or the initial 45 seconds of TELEOP and the ALLIANCE has not used a NOTE
/// for Coopertition
/// − solid on:
///   o if initial 45 seconds of TELEOP, the HUMAN PLAYER has used a NOTE for Coopertition
///   o if after the initial 45 seconds of TELEOP, both ALLIANCES have used a NOTE for Coopertition
/// − off: the Coopertition window has expired, and Coopertition was not accomplished
///
/// == Setup ==
/// Consult #defines in code below for what pin goes to what light and what switch.
///
/// When wiring buttons and switches, remember to put a 10k-ohm resistance
/// between button and ground (to avoid shorting 5v to ground with no resistance).
///
/// For red alliance, pull pin 5 low. For blue alliance, pull pin 5 high
///
/// == Serial protocol ==
/// - every message ends with \r\n
///
/// = init
/// - this client sends 'RA' or 'BA' depending on if it's red or blue alliance
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

#define ALLIANCE_LIGHT_LOW_PIN 12
#define ALLIANCE_LIGHT_HIGH_PIN 11
#define COOPERTITION_LIGHT_PIN 9

#define ALLIANCE_BUTTON 10
#define COOPERTITION_BUTTON 8
#define NOTE_SENSOR 6
#define ALLIANCE_SELECTION_PIN 5

#define ALLIANCE_LIGHT_BLINK_PERIOD_MSEC 500
#define COOPERTITION_LIGHT_BLINK_PERIOD_MSEC 1000
#define DEBOUNCE_MSEC 5

#define COOPERTITION_EXPIRATION_MSEC (5 * 1000)

/// Remote connection configs

byte mac[] = {0x10, 0x10, 0x11, 0x11, 0x12, 0x12};
IPAddress my_ip(10,0,1,2);
IPAddress field_server_ip(10,0,1,1);

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
    if (in == -1) {
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

#if 0  // 1 = Ethernet, 0 = Serial fake

class EthernetComms {

};

using Comms = EthernetComms;

#else // serial fake

class SerialComms {
private:
  TextBuffer m_buffer;

public:
  SerialComms(
    const byte* mac,
    const IPAddress& my_ip,
    const IPAddress& field_server_ip) {
    Serial.begin(9600);
  }

  ~SerialComms() {
    Serial.end();
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
  void write(char* out) {
    for (size_t cursor = 0; out[cursor] != '\0' && cursor < 80; ++cursor) {
      Serial.write(out[cursor]);
    }
    Serial.flush();
  }

  bool connected() {
    // serial comms cannot disconnect
    return true;
  }
};

using Comms = SerialComms;

# endif // select Ethernet or serial fake




class DebouncingMomentary {
  bool m_past_state;
  unsigned long m_debounce_deadline_msec;

public:
  DebouncingMomentary(): m_past_state(false), m_debounce_deadline_msec(0) {}

  // Given the current time and the current (sensed) toggle state, returns what the state should be
  int update_state(unsigned long current_time_msec, int current_state) {
    if (m_debounce_deadline_msec > 0) {
      if (current_time_msec < m_debounce_deadline_msec) {
        return LOW;
      }
      m_debounce_deadline_msec = 0;
      m_past_state = current_state;
      return LOW;
    }

    if (current_state != m_past_state) {
      m_past_state = current_state;
      m_debounce_deadline_msec = current_time_msec + DEBOUNCE_MSEC;
      return current_state;
    }

    return LOW;
  }
};

struct AmpState {
  bool low_light_lit;         // if true, low light should be lit
  bool high_light_lit;        // if true, high light should be lit
  bool alliance_light_blink;  // if true, alliance light should be blinking

  bool coopertition_light_lit;       // if true, coopertition light should be lit
  bool coopertition_light_blink;  // if true, coopertition light should be blinking

  DebouncingMomentary alliance_button;
  DebouncingMomentary coopertition_button;
  DebouncingMomentary note_sensor;
};

AmpState g_amp_state = {false, false, false ,false, false,
  DebouncingMomentary(), DebouncingMomentary(), DebouncingMomentary()};

Comms* g_comms;

void setup() {
  pinMode(ALLIANCE_LIGHT_LOW_PIN, OUTPUT);
  pinMode(ALLIANCE_LIGHT_HIGH_PIN, OUTPUT);
  pinMode(COOPERTITION_LIGHT_PIN, OUTPUT);

  pinMode(ALLIANCE_BUTTON, INPUT);
  pinMode(COOPERTITION_BUTTON, INPUT);
  pinMode(NOTE_SENSOR, INPUT);
  pinMode(ALLIANCE_SELECTION_PIN, INPUT);

  digitalWrite(ALLIANCE_LIGHT_LOW_PIN, LOW);
  digitalWrite(ALLIANCE_LIGHT_HIGH_PIN, LOW);
  digitalWrite(COOPERTITION_LIGHT_PIN, LOW);

  // TODO: we should have an establish connection handshake function that can successfully
  // negotiate a connection so that if we lose connection we can restore it
  g_comms = new Comms(mac, my_ip, field_server_ip);

  auto msg = digitalRead(ALLIANCE_SELECTION_PIN) == HIGH ? "BA\r\n" : "RA\r\n";
  g_comms->write(msg);

  char* input = g_comms->input();
  // Wait for response from server
  for (; input == nullptr; input=g_comms->input()) {
    delay(500);
  }
  if (input[0] != 'O' || input[1] != 'K') {
    // Error state: highlight top light only, sleep forever.
    digitalWrite(ALLIANCE_LIGHT_HIGH_PIN, HIGH);
    while(true) {
      delay(500);
    }
  }
}

/// returns 1 (high) or 0 (low) depending on the current time and the blink period
int blink_state(int current_time, int blink_period_msec) {
  auto blink_phase = current_time / blink_period_msec;

  return blink_phase & 0x01;
}

/// returns true if val is 1, false otherwise
bool update_lit_state(char val) {
  return val == '1';
}

void loop() {
  unsigned long current_time = millis();
  char out_buffer[4];
  out_buffer[1]='\r';
  out_buffer[2]='\n';
  out_buffer[3]='\0';

  // update light state
  digitalWrite(ALLIANCE_LIGHT_LOW_PIN, g_amp_state.low_light_lit);

  if (g_amp_state.alliance_light_blink) {
    digitalWrite(ALLIANCE_LIGHT_HIGH_PIN, blink_state(current_time, ALLIANCE_LIGHT_BLINK_PERIOD_MSEC));
  } else {
    digitalWrite(ALLIANCE_LIGHT_HIGH_PIN, g_amp_state.high_light_lit);
  }

  if (g_amp_state.coopertition_light_blink) {
    digitalWrite(COOPERTITION_LIGHT_PIN, blink_state(current_time, COOPERTITION_LIGHT_BLINK_PERIOD_MSEC));
  } else {
    digitalWrite(COOPERTITION_LIGHT_PIN, g_amp_state.coopertition_light_lit);
  }

  auto alliance_button = digitalRead(ALLIANCE_BUTTON);
  auto coopertition_button = digitalRead(COOPERTITION_BUTTON);
  auto note_sensor = digitalRead(NOTE_SENSOR);

  auto alliance_button_hit = g_amp_state.alliance_button.update_state(current_time, alliance_button);
  auto coopertition_button_hit = g_amp_state.coopertition_button.update_state(current_time, coopertition_button);
  auto note_sensor_triggered = g_amp_state.note_sensor.update_state(current_time, note_sensor);

  // Communicate button state to server.
  if (alliance_button_hit) {
    out_buffer[0] = 'A';
    g_comms->write(out_buffer);
  }
  if (coopertition_button_hit) {
    out_buffer[0] = 'C';
    g_comms->write(out_buffer);
  }
  if (note_sensor_triggered) {
    out_buffer[0] = 'R';
    g_comms->write(out_buffer);
  }

  // Read light state from the server
  char* input = g_comms->input();

  if (input == nullptr) {
    return;
  }

  switch(input[0]) {
    case 'L':
      g_amp_state.low_light_lit = update_lit_state(input[1]);
      break;
    case 'H':
      g_amp_state.high_light_lit = update_lit_state(input[1]);
      g_amp_state.alliance_light_blink = input[1] == 'B';
      break;
    case 'C':
      g_amp_state.coopertition_light_lit = update_lit_state(input[1]);
      g_amp_state.coopertition_light_blink = input[1] == 'B';
  }
}
