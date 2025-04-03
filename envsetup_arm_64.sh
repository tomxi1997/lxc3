export ANDROID_SDK_HOME=/sdk
export ANDROID_NDK_HOME=/android-ndk-r18b
export ANDROID_STANDALONE_TOOLCHAIN_HOME=/opt/toolchain/android-toolchain-arm_64-4.9-android-24
export SYSROOT=$ANDROID_STANDALONE_TOOLCHAIN_HOME/sysroot

# User specific environment and startup programs
PATH=${ANDROID_NDK_HOME}
PATH=$PATH:${ANDROID_SDK_HOME}/tools:${ANDROID_SDK_HOME}/platform-tools
PATH=$PATH:${ANDROID_STANDALONE_TOOLCHAIN_HOME}/bin:/usr/local/sbin:/usr/local/bin
PATH=$PATH:/usr/sbin:/usr/bin:/sbin:/bin
export PATH=$PATH

# Tell configure what tools to use.
export BUILD_TARGET_HOST=aarch64-linux-android
export AR=$ANDROID_STANDALONE_TOOLCHAIN_HOME/bin/$BUILD_TARGET_HOST-ar
export AS=$ANDROID_STANDALONE_TOOLCHAIN_HOME/bin/$BUILD_TARGET_HOST-gcc
export CC=$ANDROID_STANDALONE_TOOLCHAIN_HOME/bin/$BUILD_TARGET_HOST-gcc
export CXX=$ANDROID_STANDALONE_TOOLCHAIN_HOME/bin/$BUILD_TARGET_HOST-g++
export LD=$ANDROID_STANDALONE_TOOLCHAIN_HOME/bin/$BUILD_TARGET_HOST-ld
export STRIP=$ANDROID_STANDALONE_TOOLCHAIN_HOME/bin/$BUILD_TARGET_HOST-strip
export RANLIB=$ANDROID_STANDALONE_TOOLCHAIN_HOME/bin/$BUILD_TARGET_HOST-ranlib
export OBJCOPY=$ANDROID_STANDALONE_TOOLCHAIN_HOME/bin/$BUILD_TARGET_HOST-objcopy

# Tell configure what flags Android requires.
export CFLAGS="-fPIE -fPIC --sysroot=$SYSROOT"
export LDFLAGS="-pie"

# SELinux specifics
export ANDROID_LIBS="/data/lxc3"
export CFLAGS="$CFLAGS -I$ANDROID_LIBS/include"
export LDFLAGS="$LDFLAGS -L$ANDROID_LIBS/lib"

export ODMDIR=/data/lxc3
