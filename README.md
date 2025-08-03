# WIP This is still a work in progress and hasn't been tested


# Monoprice Blackbird 27842 HDMI Matrix Integration

A Home Assistant integration for the Monoprice Blackbird 27842 8x8 HDMI Matrix Switch.

## Features

- **Matrix Power Control**: Turn the entire matrix on/off
- **Input Selection**: Choose which input (1-8) feeds each output (1-8)
- **Custom Names**: Configure custom names for inputs and outputs during setup
- **TCP Connection**: Connects directly to the matrix via IP address

## Installation

### HACS (Recommended)

1. Add this repository to HACS as a custom repository
2. Install the integration through HACS
3. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/blackbird` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for "Blackbird"
4. Enter your matrix IP address (port 4001 is used by default)
5. Configure custom names for your inputs and outputs

## Entities Created

- **1 Switch Entity**: Matrix Power (turn entire matrix on/off)
- **8 Select Entities**: One for each output to choose which input feeds it

## Requirements

- Monoprice Blackbird 27842 HDMI Matrix Switch
- Network connection to the matrix (TCP port 4001)
- pyavcontrol library (automatically installed)

## Supported Operations

- Power on/off the matrix
- Route any input (1-8) to any output (1-8)
- Status monitoring and updates

## Notes

- Only HDBaseT outputs (1-8) are controllable via this integration
- Local HDMI outputs (9-16) are not controllable via the TCP interface
- The integration polls the device for status updates