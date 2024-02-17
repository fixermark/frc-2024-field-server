
out/amp/amp.ino: src/common-net.ino src/debouncing-momentary.ino src/amp.ino
	mkdir -p out/amp
	cat src/common-net.ino src/debouncing-momentary.ino src/amp.ino > out/amp/amp.ino

out/speaker/speaker.ino: src/common-net.ino src/speaker.ino
	mkdir -p out/speaker
	cat src/common-net.ino src/speaker.ino > out/speaker/speaker.ino

.PHONY: verify
verify: out/amp/amp.ino out/speaker/speaker.ino
	arduino --verify out/amp/amp.ino
	arduino --verify out/speaker/speaker.ino
