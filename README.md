# FRC 2024 field logic server

# Requirements
* Tk (for field server user interface). In Ubuntu, this can be installed by
  `sudo apt-get install python3-tk`

# Setup
**TODO**

## Network

The default network configuration is as follows:
* Field server: IP 10.0.1.1

|         | Amp        | Speaker    |
|---------|------------|------------|
| Blue    | 10.0.1.111 | 10.0.1.110 |
| Red     | 10.0.1.113 | 10.0.1.112 |

# Tasks to complete
* Clients (shared)
  * [X] Implement EthernetComms side of shim library. <2024-01-27 Sat>
    * [ ] Test EthernetComms side of shim libaray.
      - Will probably need working hardware to test this; I don't think wokwi can simulate the Ethernet shield infrastructure
  * [X] Arduino logic: implement IP address selection based on amp vs speaker and red alliance vs blue alliance <2024-01-27 Sat>
  * [X] Prototype reconnection logic for comms (can simulate with serial by having a pushbutton drop connection). <2024-02-03 Sat>
	- reconnect also handles bad handshake from server
  * [X] modify protocol: both amp and speaker can send 'ring speaker' and 'ring amp' score singals (override for manual scoring) <2024-01-27 Sat>
* Amp client
* Speaker client
  * [ ] get some details on how the LED chaser strip is controlled.
	- neopixel
  * [ ] implement
* Server
  * [X] Client init logic: when new client connects, send initial config by querying state <2024-02-03 Sat>
  * [X] handle dropped clients <2024-02-03 Sat>
  * [X] Server: how will telnet connections from server to client operate bidirectionally? <2024-01-28 Sun>
    - Will need to find the asyncio equivalent of "select on multiple futures"
    - Completed: spawned two infinite-loop subtasks that pipe the input and output
  * [X] space on UI to start auton mode, teleop mode <2024-01-27 Sat>
  * [ ] Rings that score within last three secs after amp mode should count amp score
  * [X] Rings that score within last three secs after match end should be counted <2024-01-28 Sun>
	- currently works for arbitrary time after auto and teleop end
  * [ ] Business logic for game score control
	* [X] Amp points (teleop) <2024-01-28 Sun>
    * [X] Speaker points (teleop, no amp) <2024-01-28 Sun>
    * [X] Amp points (auto) <2024-01-28 Sun>
    * [X] Speaker points (auto) <2024-01-28 Sun>
    * [X] Amp note banking <2024-01-28 Sun>
    * [X] Amp mode timer <2024-01-30 Tue>
    * [X] Speaker points (teleop, amp'd) <2024-01-30 Tue>
	* [X] Update speaker display to show amp timing <2024-01-30 Tue>
	* [X] Coopertition Mode <2024-02-01 Thu>
	  - triggerable if one note banked and within timeframe (and not already triggered)
	  - activates joint decision if both offer
	* [ ] At match start, init amp and speaker client state and game state
	* [ ] At match end, clear amp timer display from speaker clients
	* [ ] After NO on a client, server should *close* connection.
  * UI
    - tkinter is pretty close to built-in, we'll use that.
    * [X] Connection status indicators for telnet clients <2024-01-27 Sat>
    * [X] Ring score displays for red and blue alliance <2024-01-28 Sun>
    * [X] Time display and mode <2024-01-27 Sat>
	* [X] Red and blue amp status display <2024-01-30 Tue>
	  * [X] banked note count <2024-01-30 Tue>
	  * [X] amp time <2024-01-30 Tue>
	* [X] Coopertition status display (red offered, blue offered, cooperating) <2024-02-01 Thu>
	* [X] Blue and red side align with Cheesy Arena (blue on left) <2024-01-29 Mon>

# Notes
- amp prototype is hosted at https://wokwi.com/projects/387770973202227201
