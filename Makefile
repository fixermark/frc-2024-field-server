
.PHONY: build-inos
build-inos:
	$(MAKE) -C arduino-sketches out/amp/amp.ino out/speaker/speaker.ino

.PHONY: run
run:
	poetry run python3 frc_2024_field_server/app.py --host 10.0.1.1 --port 8008

.PHONY: run-local
run-local:
	poetry run python3 frc_2024_field_server/app.py --host 127.0.0.1 --port 8008
