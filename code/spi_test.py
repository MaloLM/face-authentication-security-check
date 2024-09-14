import spidev
import RPi.GPIO as GPIO

# Pin definitions for the MFRC522 module
RST_PIN = 22  # Connect RST to GPIO22 (adjust if you use a different GPIO)
CS_PIN = 24   # Connect SDA/SS to SPI0 CS0

# Initialize GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(RST_PIN, GPIO.OUT)
GPIO.output(RST_PIN, 1)  # Set RST to HIGH

# Initialize SPI
spi = spidev.SpiDev()
spi.open(0, 0)  # SPI bus 0, device 0 (adjust if using a different SPI bus/device)
spi.max_speed_hz = 1000000  # Set SPI speed (adjust if needed)


def read_from_mfrc522():
    # Send a test command to MFRC522
    response = spi.xfer([0x00])  # Dummy command for testing
    print("Response from MFRC522:", response)


try:
    while True:
        read_from_mfrc522()
except KeyboardInterrupt:
    GPIO.cleanup()
