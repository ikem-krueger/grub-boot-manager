# GRUB Boot Manager

The GRUB Boot Manager is a tool to set the default menu entry and choose in what system to reboot.

!["Screenshot of the GRUB Boot Manager"](https://github.com/ikem-krueger/grub-boot-manager/blob/master/Screenshot.png)

| Operating system | Dependencies                                            | Version | License  |
| :--------------- | :------------------------------------------------------ | :------ | :------  |
| Linux            | Python 2.x, grub-install, grub-set-default, grub-reboot | 0.9.0   | AGPL-3.0 |

## Installation:

Debian:

```
make deb
sudo dpkg -i grub-boot-manager_*.deb
```
