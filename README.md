b# FRC 2024 field logic server

# Requirements
* Tk (for field server user interface). In Ubuntu, this can be installed by
  `sudo apt-get install python3-tk`

# Setup
**TODO**

# Tasks to complete
* [X] Implement EthernetComms side of shim library. <2024-01-27 Sat>
  * [ ] Test EthernetComms side of shim libaray.
    - Will probably need working hardware to test this; I don't think wokwi can simulate the Ethernet shield infrastructure
* [X] Arduino logic: implement IP address selection based on amp vs speaker and red alliance vs blue alliance <2024-01-27 Sat>
* [ ] Prototype reconnection logic for comms (can simulate with serial by having a pushbutton drop connection).
* [ ] Server: how will telnet connections from server to client operate bidirectionally?
  - Will need to find the asyncio equivalent of "select on multiple futures"
* [ ] Server: UI
  - tkinter is pretty close to built-in, we'll use that.
  * [X] Connection status indicators for telnet clients <2024-01-27 Sat>
  * [ ] Ring score displays for red and blue alliance
  * [X] Time display and mode <2024-01-27 Sat>
* [X] Server: space on UI to start auton mode, teleop mode <2024-01-27 Sat>
* [ ] Speaker client
  - get some details on how the LED chaser strip is controlled.
* [X] modify protocol: both amp and speaker can send 'ring speaker' and 'ring amp' score singals (override for manual scoring) <2024-01-27 Sat>

# Notes
- amp prototype is hosted at https://wokwi.com/projects/387770973202227201
