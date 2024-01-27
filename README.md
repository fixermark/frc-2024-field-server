# FRC 2024 field logic server

# Setup
**TODO**

# Tasks to complete
* [ ] Implement EthernetComms side of shim library.
- [ ] Prototype reconnection logic for comms (can simulate with serial by having a pushbutton drop connection).
* [ ] Server: how will telnet connections from server to client operate bidirectionally?
  - Will need to find the asyncio equivalent of "select on multiple futures"
* [ ] Server: UI
* [ ] Server: space on UI to start auton mode, teleop moed
- [ ] Amp client
  - get some details on how the LED chaser strip is controlled.
