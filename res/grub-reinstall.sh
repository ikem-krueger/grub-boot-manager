# mount system partition...
mount /dev/sda2 /mnt

# mount efi partition...
mount /dev/sda1 /mnt/boot/efi

# mount bindings...
for i in /dev /dev/pts /proc /sys /run
do 
  mount --bind $i /mnt/$i
done

# install grub...
chroot /mnt grub-install /dev/sda

# update grub config...
chroot /mnt update-grub

