# libcap specifics
export DESTDIR=$ANDROID_LIBS
export lib=lib
export porefix=

make -j4

sudo make install

