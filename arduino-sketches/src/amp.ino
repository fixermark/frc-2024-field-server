/// amp.ino
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
/// = outbound to server
/// - A: alliance button pressed
/// - C: coopertition button pressed
/// - R: Ring sensor tripped
///
/// = inbound from server
/// - L0, L1: alliance low light off or on
/// - H0, H1, HB: alliance high light off, on, blink
/// - C0, C1, CB: coopertition high light off, on, blink

#define ALLIANCE_LIGHT_LOW_PIN 12
#define ALLIANCE_LIGHT_HIGH_PIN 11
#define COOPERTITION_LIGHT_PIN 9

#define ALLIANCE_BUTTON 10
#define COOPERTITION_BUTTON 8
#define NOTE_SENSOR 6
#define ALLIANCE_SELECTION_PIN 5
#define MANUAL_SPEAKER_SCORING 4

#define ALLIANCE_LIGHT_BLINK_PERIOD_MSEC 500
#define COOPERTITION_LIGHT_BLINK_PERIOD_MSEC 1000

#define COOPERTITION_EXPIRATION_MSEC (5 * 1000)

struct AmpState {
  bool low_light_lit;         // if true, low light should be lit
  bool high_light_lit;        // if true, high light should be lit
  bool alliance_light_blink;  // if true, alliance light should be blinking

  bool coopertition_light_lit;       // if true, coopertition light should be lit
  bool coopertition_light_blink;  // if true, coopertition light should be blinking

  DebouncingMomentary alliance_button;
  DebouncingMomentary coopertition_button;
  DebouncingMomentary note_sensor;
  DebouncingMomentary manual_speaker_score;
};

AmpState g_amp_state = {false, false, false ,false, false,
  DebouncingMomentary(), DebouncingMomentary(), DebouncingMomentary()};

void setup() {
  pinMode(ALLIANCE_LIGHT_LOW_PIN, OUTPUT);
  pinMode(ALLIANCE_LIGHT_HIGH_PIN, OUTPUT);
  pinMode(COOPERTITION_LIGHT_PIN, OUTPUT);

  pinMode(ALLIANCE_BUTTON, INPUT);
  pinMode(COOPERTITION_BUTTON, INPUT);
  pinMode(NOTE_SENSOR, INPUT);
  pinMode(ALLIANCE_SELECTION_PIN, INPUT);
  pinMode(MANUAL_SPEAKER_SCORING, INPUT);
  pinMode(DEBUG_DROP_CONNECTION_PIN, INPUT);

  digitalWrite(ALLIANCE_LIGHT_LOW_PIN, LOW);
  digitalWrite(ALLIANCE_LIGHT_HIGH_PIN, LOW);
  digitalWrite(COOPERTITION_LIGHT_PIN, LOW);

  establishConnection(digitalRead(ALLIANCE_SELECTION_PIN) == HIGH ? "HBA\r\n" : "HRA\r\n");

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

  if (!g_comms->connected()) {
    establishConnection(digitalRead(ALLIANCE_SELECTION_PIN) == HIGH ? "HBA\r\n" : "HRA\r\n");
  }

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
  auto manual_speaker = digitalRead(MANUAL_SPEAKER_SCORING);

  auto alliance_button_hit = g_amp_state.alliance_button.update_state(current_time, alliance_button);
  auto coopertition_button_hit = g_amp_state.coopertition_button.update_state(current_time, coopertition_button);
  auto note_sensor_triggered = g_amp_state.note_sensor.update_state(current_time, note_sensor);
  auto manual_speaker_score_triggered = g_amp_state.manual_speaker_score.update_state(current_time, manual_speaker);

  // Communicate button state to server.
  if (alliance_button_hit) {
    g_comms->write("A\r\n");
  }
  if (coopertition_button_hit) {
    g_comms->write("C\r\n");
  }
  if (note_sensor_triggered) {
    g_comms->write("RA\r\n");
  }
  if (manual_speaker_score_triggered) {
    g_comms->write("RS\r\n");
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
