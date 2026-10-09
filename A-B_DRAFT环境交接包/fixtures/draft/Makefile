CC ?= cc
CFLAGS ?= -std=c11 -O2 -Wall -Wextra -Wpedantic

TARGET := hello
SOURCES := main.c

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(SOURCES)
	$(CC) $(CFLAGS) $(SOURCES) -o $@

clean:
	rm -f $(TARGET)
