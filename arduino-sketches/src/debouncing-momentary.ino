/// debouncing-momentary.ino
///
/// A momentary connector that only returns HIGH on low-to-high edge detection
/// and ignores subsequent contacts within the debounce period.

#define DEBOUNCE_MSEC 5

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
