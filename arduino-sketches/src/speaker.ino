/// speaker.ino
///
/// Logic for controlling the speaker lights (NeoPixel strip)
///
///
/// == Setup ==
/// Consult #defines in code below for what pin goes to what light and what switch.
///
/// When wiring NeoPixel, make sure to put a 470-ohm resistor between the control pin and
/// the pixel input.

#include <Adafruit_NeoPixel.h>
#define NEOPIXEL_CONTROL_PIN 8
#define NUM_NEOPIXELS 20

struct SpeakerState {
  int amp_level;
};

SpeakerState g_speaker_state = {0};
Adafruit_NeoPixel g_neo_pixel(NUM_NEOPIXELS, NEOPIXEL_CONTROL_PIN, NEO_GRB + NEO_KHZ800);

uint32_t g_on_color = g_neo_pixel.Color(RED_ALLIANCE ? 255: 0, 0, RED_ALLIANCE ? 0 :255);
uint32_t g_off_color = g_neo_pixel.Color(0,0,0);

void setup() {
  g_neo_pixel.begin();

  establishConnection(RED_ALLIANCE ? "HBS\r\n" : "HRS\r\n");
}

void loop() {
  unsigned long current_time = millis();
  delay(50);

  if (!g_comms->connected()) {
    establishConnection(RED_ALLIANCE ? "HBS\r\n" : "HRS\r\n");
  }

  int lit_pixels = g_speaker_state.amp_level * NUM_NEOPIXELS / 10;

  // update light state
  for(int i=0; i < NUM_NEOPIXELS; ++i) {
    g_neo_pixel.setPixelColor(i, lit_pixels > i ? g_on_color : g_off_color);
  }
  g_neo_pixel.show();


  // Read light state from the server
  char* input = g_comms->input();

  if (input == nullptr) {
    return;
  }

  switch(input[0]) {
    case 'A':
      g_speaker_state.amp_level = input[1] == 'A' ? 10 : input[1] - '0';
      break;
  }
}
