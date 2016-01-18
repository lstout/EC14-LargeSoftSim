EC14-voxelyze
=============

Custom Voxelyze code for the Evolutionary Computing 2014 group

### Installation

git clone this repo into your home directory, cd into the voxelyze library folder and compile:
```
cd ~
git clone git@github.com:fgolemo/EC14-voxelyze.git
cd EC14-voxelyze/voxcad-code-2014/Voxelyze/
make
```

This should work fine (but with a bunch of warnings). Then copy the just-created library file and the header files to a new directory (*assuming that you are still in the same directory as before**):
```
mkdir ~/libvoxsim
cp -R ./* ~/libvoxsim
```

Now cd into the directory with the custom voxelyze main file and compile
```
cd ~/EC14-voxelyze/voxelyzeMain
make
```

Done :) Now you have a binary called `voxelyze` in that directory (i.e. in `~/EC14-voxelyze/voxelyzeMain`), which will do all the voxelization for you.
