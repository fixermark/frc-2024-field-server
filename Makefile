.PHONY: build-inos run

build-inos:
	$(MAKE) -C arduino-sketches out/amp/amp.ino

run:
	poetry run python3 frc_2024_field_server/app.py --host 127.0.0.1 --port 8008
