CC ?= cc
CFLAGS = -O0 -Wall -Wextra -std=c11

.PHONY: all clean

all: app

app: main.o
	$(CC) $(CFLAGS) -o $@ $^

main.o: main.c config.h
	$(CC) $(CFLAGS) -c -o $@ $<

clean:
	rm -f app main.o
