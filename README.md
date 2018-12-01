# rhw-ham
This repository has additional information to help HAM's listening to Reaktor Hello World satellite.

Project web page: https://reaktorspace.com/reaktor-hello-world/


# Telemetry decoding

An example GNU Radio Companion file is provided that can decode the FSK packets transmitted by Reaktor Hello World. It requires the [CC11XX decoder block](https://github.com/andrepuschmann/gr-cc11xx). The sample file used by default is a real recording from orbit with a single EPS telemetry packet. The format is explained in the [Reaktor Hello World page](https://reaktorspace.com/reaktor-hello-world/#get-in-touch). The decoder print to standard out the bytes starting after the sync word, i.e., the first byte is the radio packet length.

See telemetry_unit_conversions.py for the information on how to convert adc readings to meaningful units.
