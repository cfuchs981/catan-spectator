SHELL := /bin/bash

all: relaunch

launch:
	@mkdir -p log
	python3 main.py &>log/buffer.log & echo $$! > log/running.pid
	@cat log/running.pid
	@echo "Follow logs: tail -f log/buffer.log, or make logs"

logs:
	tail -f log/buffer.log

relaunch:
	@mkdir -p log
	-mv log/buffer.log log/spectator-launch-`date +"%Y-%m-%d_%H-%M-%S"`.log
	-cat log/running.pid | xargs kill
	python3 main.py &>log/buffer.log & echo $$! > log/running.pid
	@cat log/running.pid
	@echo "Follow logs: tail -f log/buffer.log, or make logs"
