[![GitHub Release](https://img.shields.io/github/release/brezlord/hass-waterco-electrochlor.svg?style=flat-square)](https://github.com/brezlord/hass-waterco-electrochlor/releases)
[![License](https://img.shields.io/github/license/brezlord/hass-waterco-electrochlor.svg?style=flat-square)](LICENSE.md)
[![HACS Badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=flat-square)](https://github.com/custom-components/hacs)
![HACS Build](https://github.com/brezlord/hass-waterco-electrochlor/workflows/HACS/badge.svg?style=flat-square)

[![Waterco](https://raw.githubusercontent.com/brezlord/hass-waterco-electrochlor/refs/heads/main/images/waterco-logo.png)](https://www.waterco.com.au)

# Waterco Home Assistant Integration

The `Waterco` custom component integrates **Waterco's Electrochlor Mineral Chlorinator** with Home Assistant, enabling automation and monitoring of pool sanitization and filtration systems. This integration allows users to access real-time data and control various aspects of their pool equipment directly from the Home Assistant interface.

## Features

- **Real-Time Monitoring**: Displays current pool temperature, chlorine production levels, and system status.
- **Automation Support**: Facilitates automation of sanitization cycles and filtration schedules based on sensor data.
- **System Alerts**: Provides notifications for system errors or maintenance needs.
- **Compatibility**: Designed to work seamlessly with Waterco's Electrochlor Mineral Chlorinator systems.

## Installation

It is recommended this is installed using [Home Assistant Community Store (HACS)](https://hacs.xyz/) to ensure your Home Assistant instance can easily be kept up-to-date with the latest changes.

However, to install this manually:

1. Clone or download the repository.
2. Place the `waterco` folder into your Home Assistant's `custom_components` directory.
3. Configure the integration through the Home Assistant UI.

## Configuration

- Browse to your Home Assistant instance
- In the sidebar click on  **Settings**
- From the Settings menu select: **Devices & services**
- In the bottom right, click on the **+ Add Integration** button
- From the list, search and select “_Waterco_”
- Follow the instruction to complete the set up

## Recommendation

- It is strongly recommended to assign a static IP address to your Waterco Electrochlor Pool Controller. This must be configured through your router’s DHCP settings, as the controller itself does not provide an option to manually set an IP address.

- If the IP address does change, it can be updated directly via the integration’s configuration UI without needing to remove or reinstall the integration.

## Usage

Once installed, the component will create **sensors** and **switches** in Home Assistant representing various aspects of the Electrochlor system. These entities can be used in dashboards, automations, and scripts to monitor and control your pool's sanitization and filtration processes.

## Notes

- Ensure your Electrochlor system is connected to the network and accessible by Home Assistant.
- Refer to the [Waterco Electrochlor Manual](https://www.waterco.com.au/waterco/manuals/pool-spa/chlorination/electrochlor-mineral-chlorinator_manual_jan18_single.pdf) for detailed information on your system's capabilities and setup.
- For advanced configurations or troubleshooting, consult the component's documentation and the Home Assistant community forums.

---

This integration enhances the functionality of your Electrochlor system, providing greater control and insight into your pool's maintenance.

## Disclaimer

**This project is not endorsed by, directly affiliated with, maintained, authorized, or sponsored by Waterco.**