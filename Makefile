.PHONY: test install uninstall

test:
	python3 -m unittest discover --top-level-directory . --start-directory tests

install:
	./install.sh

uninstall:
	./uninstall.sh
