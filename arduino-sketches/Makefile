.PHONY: verify

out/amp/amp.ino: src/common-net.ino src/debouncing-momentary.ino src/amp.ino
	mkdir -p out/amp
	cat src/common-net.ino src/debouncing-momentary.ino src/amp.ino > out/amp/amp.ino


verify: out/amp/amp.ino
	arduino --verify out/amp.ino
