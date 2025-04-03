# libcap specifics
#export DESTDIR=$ANDROID_LIBS
#export lib=lib
#export porefix=
make CC="$CC -Wl,-rpath=$ANDROID_LIBS/lib -Wl,--enable-new-dtags" OBJCOPY=$OBJCOPY PREFIX="$ANDROID_LIBS" PTHREADS=no PAM_CAP=no



sudo make CC="$CC -Wl,-rpath=$ANDROID_LIBS/lib -Wl,--enable-new-dtags" OBJCOPY=$OBJCOPY prefix="$ANDROID_LIBS" RAISE_SETFCAP=no lib=/lib PTHREADS=no install PAM_CAP=no

#sudo make install

